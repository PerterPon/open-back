#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测主文件 - 基于 backtrader 框架
主要功能：
1. 从 MySQL 数据库读取 K 线数据
2. 动态加载策略文件
3. 执行回测并计算各种指标
4. 输出 JSON 格式的回测结果

使用方法：
python index.py --currency BTCUSDT --time_interval 1m --strategy_name simple_ma

输出格式：
{
  "currency": "BTCUSDT",
  "time_interval": "1m", 
  "sharpe_ratio": "1.0",
  "trade_count": 100,
  "trades": [{"time":"2023-06-15 22:00:00","balance":10025.758523936815,"price":25389.97}, ...],
  "total_commission": 100,
  "max_drawdown": 0.05,
  "winning_percentage": 0.5,
  "init_balance": 10000,
  "final_balance": 10000
}
"""

import sys
import os
import argparse
import json
import importlib.util
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import backtrader as bt
from core.mysql.kline import get_all_klines_by_currency_time_interval


class BacktestAnalyzer(bt.Analyzer):
    """简化的自定义分析器，只收集内置分析器无法提供的信息"""
    
    def __init__(self):
        super().__init__()
        self.trades = []  # 详细的交易记录
        self.equity_curve = []  # 资金曲线
        
    def notify_trade(self, trade):
        """交易完成时的回调 - 收集详细交易信息"""
        if trade.isclosed:
            self.trades.append({
                'time': bt.num2date(trade.dtclose).strftime('%Y-%m-%d %H:%M:%S'),
                'balance': self.strategy.broker.get_value(),
                'price': trade.price,
                'size': trade.size,
                'pnl': trade.pnl,
                'pnlcomm': trade.pnlcomm,
                'commission': trade.commission
            })
    
    def next(self):
        """每个数据点的回调 - 收集资金曲线"""
        current_value = self.strategy.broker.get_value()
        self.equity_curve.append({
            'time': bt.num2date(self.strategy.datas[0].datetime[0]).strftime('%Y-%m-%d %H:%M:%S'),
            'balance': current_value
        })
    
    def get_analysis(self):
        """返回分析结果"""
        return {
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, currency: str, time_interval: str, strategy_name: str):
        self.currency = currency
        self.time_interval = time_interval
        self.strategy_name = strategy_name
        self.init_balance = 10000.0
        self.commission = 0.001  # 0.1% 手续费
        
        # 初始化 backtrader 引擎
        self.cerebro = bt.Cerebro()
        self.analyzer = None
        self.strategy_class = None
        
    def load_data(self) -> Optional[pd.DataFrame]:
        """从数据库加载 K 线数据"""
        try:
            # 获取所有数据用于回测
            klines = get_all_klines_by_currency_time_interval(
                self.currency, 
                self.time_interval
            )
            
            if not klines:
                print(f"❌ 未找到 {self.currency} {self.time_interval} 的数据")
                return None
            
            # 转换为 DataFrame
            df = pd.DataFrame(klines)
            
            # 确保时间列存在且格式正确
            if 'time' not in df.columns:
                print("❌ 数据中缺少时间列")
                return None
            
            # 转换时间格式
            df['time'] = pd.to_datetime(df['time'])
            df = df.sort_values('time')  # 按时间升序排列
            
            # 检查必要的 OHLCV 列
            required_cols = ['o', 'h', 'l', 'c', 'v']
            for col in required_cols:
                if col not in df.columns:
                    print(f"❌ 数据中缺少列：{col}")
                    return None
            
            # 重命名列以符合 backtrader 要求
            df = df.rename(columns={
                'time': 'datetime',
                'o': 'open',
                'h': 'high', 
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            # 设置 datetime 为索引
            df.set_index('datetime', inplace=True)
            
            print(f"✅ 成功加载 {len(df)} 条 K 线数据")
            print(f"📊 数据时间范围：{df.index[0]} 到 {df.index[-1]}")
            
            return df[['open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            print(f"❌ 加载数据失败：{e}")
            return None
    
    def load_strategy(self) -> bool:
        """动态加载策略文件"""
        try:
            strategy_file = os.path.join(
                os.path.dirname(__file__), 
                'strategy', 
                f'{self.strategy_name}.py'
            )
            
            if not os.path.exists(strategy_file):
                print(f"❌ 策略文件不存在：{strategy_file}")
                return False
            
            # 动态导入策略模块
            spec = importlib.util.spec_from_file_location(self.strategy_name, strategy_file)
            strategy_module = importlib.util.module_from_spec(spec)
            
            # 将模块添加到 sys.modules 中，避免 backtrader 的模块查找问题
            sys.modules[self.strategy_name] = strategy_module
            
            spec.loader.exec_module(strategy_module)
            
            # 查找策略类（假设策略类名为 Strategy）
            if hasattr(strategy_module, 'Strategy'):
                self.strategy_class = strategy_module.Strategy
                print(f"✅ 成功加载策略：{self.strategy_name}")
                return True
            else:
                print(f"❌ 策略文件中未找到 Strategy 类：{strategy_file}")
                return False
                
        except Exception as e:
            print(f"❌ 加载策略失败：{e}")
            return False
    
    def setup_cerebro(self, data_df: pd.DataFrame):
        """设置 backtrader 引擎"""
        # 创建数据源
        data = bt.feeds.PandasData(dataname=data_df)
        self.cerebro.adddata(data)
        
        # 添加策略
        if self.strategy_class:
            self.cerebro.addstrategy(self.strategy_class)
        
        # 设置初始资金
        self.cerebro.broker.setcash(self.init_balance)
        
        # 设置手续费
        self.cerebro.broker.setcommission(commission=self.commission)
        
        # 添加自定义分析器
        self.cerebro.addanalyzer(BacktestAnalyzer, _name='backtest_analyzer')
        
        # 添加内置分析器 - 优先使用 backtrader 内置的计算
        # 根据数据间隔动态设置夏普比率的时间框架和压缩比
        timeframe, compression = self._parse_time_interval(self.time_interval)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', 
                                timeframe=timeframe, compression=compression, riskfreerate=0.0)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        self.cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='annual_return')
        self.cerebro.addanalyzer(bt.analyzers.Calmar, _name='calmar')
        self.cerebro.addanalyzer(bt.analyzers.VWR, _name='vwr')  # Variability-Weighted Return
        
        print(f"✅ 回测引擎设置完成，初始资金：{self.init_balance}")
    
    def _parse_time_interval(self, time_interval: str) -> tuple:
        """
        解析时间间隔字符串，返回 timeframe 和 compression
        
        Args:
            time_interval: 时间间隔字符串，如 '1m', '5m', '15m', '1h', '4h', '1d'
            
        Returns:
            tuple: (timeframe, compression)
        """
        import re
        
        # 使用正则表达式解析时间间隔
        pattern = r'^(\d+)([mhHdDwWM])$'
        match = re.match(pattern, time_interval)
        
        if not match:
            print(f"⚠️ 无法解析时间间隔 '{time_interval}'，使用默认值 (Minutes, 1)")
            return bt.TimeFrame.Minutes, 1
        
        number = int(match.group(1))
        unit = match.group(2)  # 保持原始大小写
        
        # 根据单位确定时间框架 - 注意：大写 M（月）要先判断
        if unit == 'M':  # 大写 M 表示月，必须先判断
            timeframe = bt.TimeFrame.Months
            compression = number
        elif unit.lower() == 'm':  # 小写 m 表示分钟
            timeframe = bt.TimeFrame.Minutes
            compression = number
        elif unit.lower() == 'h':
            timeframe = bt.TimeFrame.Minutes
            compression = number * 60  # 小时转换为分钟
        elif unit.lower() == 'd':
            timeframe = bt.TimeFrame.Days
            compression = number
        elif unit.lower() == 'w':
            timeframe = bt.TimeFrame.Weeks
            compression = number
        else:
            print(f"⚠️ 未知的时间单位 '{unit}'，使用默认值 (Minutes, 1)")
            timeframe = bt.TimeFrame.Minutes
            compression = 1
        
        print(f"📊 时间间隔 '{time_interval}' 解析为：{self._timeframe_name(timeframe)}, compression={compression}")
        
        return timeframe, compression
    
    def _timeframe_name(self, timeframe: int) -> str:
        """获取时间框架的名称（用于日志输出）"""
        timeframe_names = {
            bt.TimeFrame.Minutes: 'Minutes',
            bt.TimeFrame.Days: 'Days', 
            bt.TimeFrame.Weeks: 'Weeks',
            bt.TimeFrame.Months: 'Months',
            bt.TimeFrame.Years: 'Years'
        }
        return timeframe_names.get(timeframe, 'Unknown')
    
    def extract_builtin_metrics(self, strategy_result) -> Dict[str, Any]:
        """
        从 backtrader 内置分析器中提取所有指标
        优先使用内置分析器的计算结果
        """
        metrics = {}
        
        try:
            # 1. 夏普比率 - 使用内置分析器
            sharpe_analyzer = strategy_result.analyzers.sharpe.get_analysis()
            metrics['sharpe_ratio'] = sharpe_analyzer.get('sharperatio', 0.0) or 0.0
            
            # 2. 最大回撤 - 使用内置分析器
            drawdown_analyzer = strategy_result.analyzers.drawdown.get_analysis()
            metrics['max_drawdown'] = drawdown_analyzer.get('max', {}).get('drawdown', 0.0) / 100.0
            
            # 3. 交易分析 - 使用内置分析器
            trade_analyzer = strategy_result.analyzers.trades.get_analysis()
            metrics['trade_count'] = trade_analyzer.get('total', {}).get('closed', 0)
            
            # 计算胜率
            won_trades = trade_analyzer.get('won', {}).get('total', 0)
            total_trades = metrics['trade_count']
            metrics['winning_percentage'] = (won_trades / total_trades) if total_trades > 0 else 0.0
            
            # 4. 年化收益率 - 使用内置分析器
            annual_return_analyzer = strategy_result.analyzers.annual_return.get_analysis()
            # 处理可能的 OrderedDict 格式问题
            if hasattr(annual_return_analyzer, 'items'):
                # 如果是字典类型，取平均值或第一个值
                annual_return_values = list(annual_return_analyzer.values()) if annual_return_analyzer else [0.0]
                metrics['annual_return'] = annual_return_values[0] if annual_return_values else 0.0
            else:
                metrics['annual_return'] = annual_return_analyzer or 0.0
            
            # 5. Calmar 比率 - 使用内置分析器
            calmar_analyzer = strategy_result.analyzers.calmar.get_analysis()
            metrics['calmar_ratio'] = calmar_analyzer.get('calmar', 0.0) or 0.0
            
            # 6. VWR - 使用内置分析器
            vwr_analyzer = strategy_result.analyzers.vwr.get_analysis()
            metrics['vwr'] = vwr_analyzer.get('vwr', 0.0) or 0.0
            
            print(f"📊 内置分析器结果：")
            print(f"   夏普比率：{metrics['sharpe_ratio']}")
            print(f"   最大回撤：{metrics['max_drawdown']}")
            print(f"   年化收益率：{metrics['annual_return']}")
            print(f"   Calmar 比率：{metrics['calmar_ratio']}")
            print(f"   VWR:{metrics['vwr']}")
            print(f"   交易次数：{metrics['trade_count']}")
            print(f"   胜率：{metrics['winning_percentage']}")
            
        except Exception as e:
            print(f"❌ 提取内置分析器结果失败：{e}")
            # 设置默认值
            metrics.update({
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'trade_count': 0,
                'winning_percentage': 0.0,
                'annual_return': 0.0,
                'calmar_ratio': 0.0,
                'vwr': 0.0
            })
        
        return metrics
    
    def run_backtest(self) -> Dict[str, Any]:
        """执行回测 - 优先使用 backtrader 内置分析器"""
        # 1. 加载数据
        data_df = self.load_data()
        if data_df is None:
            return {"error": "数据加载失败"}
        
        # 2. 加载策略
        if not self.load_strategy():
            return {"error": "策略加载失败"}
        
        # 3. 设置回测引擎
        self.setup_cerebro(data_df)
        
        print(f"🚀 开始执行回测...")
        
        # 4. 执行回测
        try:
            results = self.cerebro.run()
            strategy_result = results[0]
            
            print(f"✅ 回测执行完成")
            
            # 5. 获取自定义分析器结果（详细交易记录等）
            custom_analyzer = strategy_result.analyzers.backtest_analyzer
            custom_analysis = custom_analyzer.get_analysis()
            
            # 6. 使用内置分析器提取所有指标
            builtin_metrics = self.extract_builtin_metrics(strategy_result)
            
            # 7. 计算基础指标
            final_balance = self.cerebro.broker.get_value()
            total_return = (final_balance - self.init_balance) / self.init_balance
            
            # 8. 计算总手续费（从详细交易记录中）
            total_commission = sum(trade.get('commission', 0) for trade in custom_analysis['trades'])
            
            # 9. 准备最终结果 - 优先使用内置分析器的结果
            result = {
                "currency": self.currency,
                "time_interval": self.time_interval,
                "sharpe_ratio": builtin_metrics['sharpe_ratio'],
                "trade_count": builtin_metrics['trade_count'],
                "trades": custom_analysis['trades'],  # 详细交易记录来自自定义分析器
                "total_commission": round(total_commission, 2),
                "max_drawdown": builtin_metrics['max_drawdown'],
                "winning_percentage": builtin_metrics['winning_percentage'],
                "init_balance": self.init_balance,
                "final_balance": round(final_balance, 2),
                "total_return": round(total_return, 4),
                "annual_return": builtin_metrics['annual_return'],
                "calmar_ratio": builtin_metrics['calmar_ratio'],
                "vwr": builtin_metrics['vwr'],
                "data_points": len(data_df),
                "start_date": str(data_df.index[0]),
                "end_date": str(data_df.index[-1])
            }
            
            print(f"📊 回测结果统计：")
            print(f"   初始资金：{result['init_balance']}")
            print(f"   最终资金：{result['final_balance']}")
            print(f"   总收益率：{result['total_return']:.2%}")
            print(f"   夏普比率：{result['sharpe_ratio']:.4f}")
            print(f"   最大回撤：{result['max_drawdown']:.2%}")
            print(f"   交易次数：{result['trade_count']}")
            print(f"   胜率：{result['winning_percentage']:.2%}")
            print(f"   总手续费：{result['total_commission']}")
            print(f"   年化收益率：{result['annual_return']:.2%}")
            print(f"   Calmar 比率：{result['calmar_ratio']:.4f}")
            
            return result
            
        except Exception as e:
            print(f"❌ 回测执行失败：{e}")
            import traceback
            traceback.print_exc()
            return {"error": f"回测执行失败：{e}"}


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='加密货币交易策略回测工具')
    parser.add_argument('--currency', type=str, required=True, help='货币对，如 BTCUSDT')
    parser.add_argument('--time_interval', type=str, required=True, help='时间间隔，如 1m, 5m, 1h, 1d')
    parser.add_argument('--strategy_name', type=str, required=True, help='策略名称')
    
    args = parser.parse_args()
    
    print(f"🔄 启动回测...")
    print(f"   货币对：{args.currency}")
    print(f"   时间间隔：{args.time_interval}")
    print(f"   策略名称：{args.strategy_name}")
    
    # 创建回测引擎
    engine = BacktestEngine(args.currency, args.time_interval, args.strategy_name)
    
    # 执行回测
    result = engine.run_backtest()
    
    # 输出 JSON 结果
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
