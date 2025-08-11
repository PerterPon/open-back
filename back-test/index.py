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
    """自定义分析器，用于收集交易数据和统计信息"""
    
    def __init__(self):
        super().__init__()
        self.trades = []
        self.balances = []
        self.returns = []
        self.equity_curve = []
        
    def notify_trade(self, trade):
        """交易完成时的回调"""
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
    
    def notify_order(self, order):
        """订单状态变化时的回调"""
        pass
    
    def next(self):
        """每个数据点的回调"""
        current_value = self.strategy.broker.get_value()
        self.balances.append(current_value)
        self.equity_curve.append({
            'time': bt.num2date(self.strategy.datas[0].datetime[0]).strftime('%Y-%m-%d %H:%M:%S'),
            'balance': current_value
        })
        
        if len(self.balances) > 1:
            ret = (current_value - self.balances[-2]) / self.balances[-2]
            self.returns.append(ret)
    
    def get_analysis(self):
        """返回分析结果"""
        return {
            'trades': self.trades,
            'balances': self.balances,
            'returns': self.returns,
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
        
        # 添加分析器（通过 cerebro 添加，而不是直接创建）
        self.cerebro.addanalyzer(BacktestAnalyzer, _name='backtest_analyzer')
        
        # 添加其他分析器
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe')
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name='trades')
        self.cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')
        
        print(f"✅ 回测引擎设置完成，初始资金：{self.init_balance}")
    
    def calculate_sharpe_ratio(self, returns: List[float], data_df: pd.DataFrame) -> float:
        """
        计算夏普比率
        注意：需要根据数据的实际时间跨度进行年化处理
        """
        if not returns or len(returns) < 2:
            return 0.0
        
        try:
            returns_array = np.array(returns)
            
            # 计算平均收益率和标准差
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array, ddof=1)
            
            if std_return == 0:
                return 0.0
            
            # 计算数据的时间跨度（年）
            start_date = data_df.index[0]
            end_date = data_df.index[-1]
            time_span_days = (end_date - start_date).days
            
            # 根据时间间隔确定年化因子
            if self.time_interval == '1m':
                periods_per_year = 365 * 24 * 60  # 每年分钟数
                periods_in_data = len(returns)
                actual_years = periods_in_data / periods_per_year
            elif self.time_interval == '5m':
                periods_per_year = 365 * 24 * 12  # 每年 5 分钟数
                periods_in_data = len(returns)
                actual_years = periods_in_data / periods_per_year
            elif self.time_interval == '1h':
                periods_per_year = 365 * 24  # 每年小时数
                periods_in_data = len(returns)
                actual_years = periods_in_data / periods_per_year
            elif self.time_interval == '1d':
                periods_per_year = 365  # 每年天数
                periods_in_data = len(returns)
                actual_years = periods_in_data / periods_per_year
            else:
                # 默认使用日历天数计算
                actual_years = max(time_span_days / 365.0, 1/365.0)  # 至少 1 天
            
            # 年化收益率和波动率
            if 'periods_per_year' in locals() and periods_per_year > 0:
                annualized_return = mean_return * math.sqrt(periods_per_year)
                annualized_volatility = std_return * math.sqrt(periods_per_year)
            else:
                annualized_return = mean_return * math.sqrt(365)
                annualized_volatility = std_return * math.sqrt(365)
            
            # 计算夏普比率（假设无风险收益率为 0）
            if annualized_volatility > 1e-10:  # 避免除零和极小值
                sharpe_ratio = annualized_return / annualized_volatility
            else:
                sharpe_ratio = 0.0
                
            # 限制夏普比率在合理范围内
            if abs(sharpe_ratio) > 100:
                sharpe_ratio = 0.0
            
            print(f"📊 收益率统计：平均={mean_return:.6f}, 标准差={std_return:.6f}")
            print(f"📊 年化收益率：{annualized_return:.4f}, 年化波动率：{annualized_volatility:.4f}")
            print(f"📊 数据时间跨度：{time_span_days}天，实际年数：{actual_years:.2f}")
            
            return round(sharpe_ratio, 4)
            
        except Exception as e:
            print(f"❌ 计算夏普比率失败：{e}")
            return 0.0
    
    def run_backtest(self) -> Dict[str, Any]:
        """执行回测"""
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
            
            # 5. 获取分析结果
            backtest_analyzer = strategy_result.analyzers.backtest_analyzer
            analysis = backtest_analyzer.get_analysis()
            
            # 6. 计算各项指标
            final_balance = self.cerebro.broker.get_value()
            total_return = (final_balance - self.init_balance) / self.init_balance
            
            # 获取内置分析器结果
            sharpe_analyzer = strategy_result.analyzers.sharpe.get_analysis()
            drawdown_analyzer = strategy_result.analyzers.drawdown.get_analysis()
            trade_analyzer = strategy_result.analyzers.trades.get_analysis()
            
            # 计算夏普比率
            sharpe_ratio = self.calculate_sharpe_ratio(analysis['returns'], data_df)
            
            # 如果自定义计算失败，使用内置分析器的结果
            if sharpe_ratio == 0.0 and 'sharperatio' in sharpe_analyzer:
                sharpe_ratio = sharpe_analyzer['sharperatio'] or 0.0
            
            # 计算最大回撤
            max_drawdown = 0.0
            if 'max' in drawdown_analyzer and 'drawdown' in drawdown_analyzer['max']:
                max_drawdown = abs(drawdown_analyzer['max']['drawdown'] / 100.0)  # 转换为小数
            
            # 计算交易统计
            trade_count = len(analysis['trades'])
            total_commission = sum(trade.get('commission', 0) for trade in analysis['trades'])
            
            # 计算胜率
            winning_trades = sum(1 for trade in analysis['trades'] if trade.get('pnl', 0) > 0)
            winning_percentage = winning_trades / trade_count if trade_count > 0 else 0.0
            
            # 准备结果
            result = {
                "currency": self.currency,
                "time_interval": self.time_interval,
                "sharpe_ratio": str(sharpe_ratio),
                "trade_count": trade_count,
                "trades": analysis['trades'],
                "total_commission": round(total_commission, 2),
                "max_drawdown": round(max_drawdown, 4),
                "winning_percentage": round(winning_percentage, 4),
                "init_balance": self.init_balance,
                "final_balance": round(final_balance, 2),
                "total_return": round(total_return, 4),
                "data_points": len(data_df),
                "start_date": str(data_df.index[0]),
                "end_date": str(data_df.index[-1])
            }
            
            print(f"📊 回测结果统计：")
            print(f"   初始资金：{result['init_balance']}")
            print(f"   最终资金：{result['final_balance']}")
            print(f"   总收益率：{result['total_return']:.2%}")
            print(f"   夏普比率：{result['sharpe_ratio']}")
            print(f"   最大回撤：{result['max_drawdown']:.2%}")
            print(f"   交易次数：{result['trade_count']}")
            print(f"   胜率：{result['winning_percentage']:.2%}")
            print(f"   总手续费：{result['total_commission']}")
            
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
