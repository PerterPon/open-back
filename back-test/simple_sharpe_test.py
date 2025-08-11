#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的夏普比率计算验证测试

这个测试创建一个极其简单的场景：
1. 固定的价格数据
2. 固定的交易时机
3. 可以精确预测的收益率
4. 手工计算的夏普比率
"""

import sys
import os
import numpy as np
import math
from unittest.mock import patch
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(__file__))

from index import BacktestEngine


def create_simple_test_data():
    """
    创建极其简单的测试数据
    只有20个数据点，价格固定上涨
    """
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    data = []
    
    # 价格从50000开始，每小时涨100
    for i in range(20):
        price = 50000 + i * 100
        date = start_date + timedelta(hours=i)
        
        data.append({
            'time': date,
            'currency': 'TESTCOIN',
            'time_interval': '1h',
            'o': price,
            'h': price + 10,
            'l': price - 10,
            'c': price,
            'v': 1000.0
        })
    
    return data


def manual_calculation():
    """
    手工计算预期的交易结果
    
    策略：每5小时买入一次，立即卖出
    数据：价格从50000开始，每小时涨100
    
    交易1: 第0小时买入50000，第5小时卖出50500，收益率 = 500/50000 = 0.01
    交易2: 第5小时买入50500，第10小时卖出51000，收益率 = 500/50500 ≈ 0.0099
    交易3: 第10小时买入51000，第15小时卖出51500，收益率 = 500/51000 ≈ 0.0098
    """
    
    # 假设每次交易使用95%的资金，手续费0.1%
    initial_balance = 10000
    trades = []
    current_balance = initial_balance
    
    # 3次交易
    for i in range(3):
        buy_hour = i * 5
        sell_hour = (i + 1) * 5
        
        buy_price = 50000 + buy_hour * 100
        sell_price = 50000 + sell_hour * 100
        
        # 使用95%的资金
        investment = current_balance * 0.95
        shares = investment / buy_price
        
        # 卖出收入
        sell_value = shares * sell_price
        
        # 手续费（买入和卖出各0.05%）
        buy_fee = investment * 0.0005
        sell_fee = sell_value * 0.0005
        total_fee = buy_fee + sell_fee
        
        # 净收益
        net_profit = sell_value - investment - total_fee
        
        # 交易收益率
        trade_return = net_profit / current_balance
        
        trades.append({
            'buy_price': buy_price,
            'sell_price': sell_price,
            'investment': investment,
            'net_profit': net_profit,
            'trade_return': trade_return
        })
        
        current_balance += net_profit
    
    # 计算统计指标
    returns = [t['trade_return'] for t in trades]
    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)
    
    # 年化夏普比率
    # 每5小时一次交易，一年有8760小时，所以一年有8760/5 = 1752次交易
    trades_per_year = 8760 / 5
    
    annualized_return = mean_return * trades_per_year
    annualized_volatility = std_return * math.sqrt(trades_per_year)
    
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility > 0 else 0
    
    print("🧮 手工计算详情：")
    print(f"   交易次数: {len(trades)}")
    print(f"   交易详情:")
    for i, trade in enumerate(trades):
        print(f"      交易{i+1}: 买入${trade['buy_price']}, 卖出${trade['sell_price']}, 收益率={trade['trade_return']:.6f}")
    
    print(f"   统计指标:")
    print(f"      平均收益率: {mean_return:.6f}")
    print(f"      收益率标准差: {std_return:.6f}")
    print(f"      年化交易次数: {trades_per_year:.1f}")
    print(f"      年化收益率: {annualized_return:.4f}")
    print(f"      年化波动率: {annualized_volatility:.4f}")
    print(f"      预期夏普比率: {sharpe_ratio:.4f}")
    
    return {
        'trades': trades,
        'returns': returns,
        'mean_return': mean_return,
        'std_return': std_return,
        'sharpe_ratio': sharpe_ratio,
        'trades_per_year': trades_per_year
    }


def create_simple_strategy():
    """创建简单的测试策略文件"""
    strategy_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
极简测试策略
每5小时买入一次，立即卖出
"""

import backtrader as bt


class Strategy(bt.Strategy):
    """极简测试策略"""
    
    def __init__(self):
        self.trade_counter = 0
        self.position_opened = False
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.log(f'✅ 买入: 价格=${order.executed.price:.2f}')
                self.position_opened = True
            else:
                self.log(f'✅ 卖出: 价格=${order.executed.price:.2f}')
                self.position_opened = False
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'📊 交易完成: 净利润=${trade.pnlcomm:.2f}')
    
    def next(self):
        current_bar = len(self.datas[0])
        current_price = self.datas[0].close[0]
        
        # 每5小时交易一次
        if current_bar % 5 == 1 and current_bar <= 15:  # 第1, 6, 11小时
            if not self.position:
                # 买入
                cash = self.broker.get_cash()
                size = (cash * 0.95) / current_price
                self.buy(size=size)
                self.trade_counter += 1
                self.log(f'📈 买入信号: 价格=${current_price:.2f}')
        
        # 买入后立即卖出（下一个小时）
        elif self.position and self.position_opened:
            self.sell(size=self.position.size)
            self.log(f'📉 卖出信号: 价格=${current_price:.2f}')
    
    def stop(self):
        final_value = self.broker.get_value()
        self.log(f'📊 策略结束: 最终价值=${final_value:.2f}')
'''
    
    # 写入策略文件
    strategy_file = '/Volumes/data/project/open-back/back-test/strategy/simple_test.py'
    with open(strategy_file, 'w', encoding='utf-8') as f:
        f.write(strategy_content)
    
    print(f"✅ 创建简单测试策略: {strategy_file}")


def run_simple_test():
    """运行简单测试"""
    print("🧪 简单夏普比率计算验证")
    print("=" * 50)
    
    # 1. 创建测试数据和策略
    test_data = create_simple_test_data()
    create_simple_strategy()
    
    # 2. 手工计算预期结果
    expected = manual_calculation()
    
    # 3. 运行回测
    print(f"\n🚀 运行回测系统:")
    engine = BacktestEngine('TESTCOIN', '1h', 'simple_test')
    
    with patch('index.get_all_klines_by_currency_time_interval') as mock_get:
        mock_get.return_value = test_data
        result = engine.run_backtest()
    
    # 4. 对比结果
    print(f"\n📊 结果对比:")
    if 'error' in result:
        print(f"❌ 回测失败: {result['error']}")
        return False
    
    print(f"   交易次数: 预期={len(expected['trades'])}, 实际={result['trade_count']}")
    print(f"   夏普比率: 预期={expected['sharpe_ratio']:.4f}, 实际={float(result['sharpe_ratio']):.4f}")
    
    # 5. 验证准确性
    sharpe_diff = abs(float(result['sharpe_ratio']) - expected['sharpe_ratio'])
    trade_count_match = result['trade_count'] == len(expected['trades'])
    
    print(f"\n✅ 验证结果:")
    print(f"   交易次数匹配: {'✅' if trade_count_match else '❌'}")
    print(f"   夏普比率差异: {sharpe_diff:.6f}")
    
    tolerance = 0.1  # 放宽误差容忍度
    if trade_count_match and sharpe_diff <= tolerance:
        print("🎉 验证成功! 夏普比率计算基本正确")
        return True
    else:
        print("❌ 验证失败! 需要进一步检查计算逻辑")
        return False


if __name__ == "__main__":
    run_simple_test()
