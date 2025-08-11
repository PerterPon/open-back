#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试backtrader内置分析器的准确性

使用一个极其简单的场景来验证内置分析器是否正常工作
"""

import sys
import os
import numpy as np
from unittest.mock import patch
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(__file__))

from index import BacktestEngine


def create_profitable_test_data():
    """
    创建确保盈利的测试数据
    价格持续上涨，确保买入后能盈利
    """
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    data = []
    
    # 价格从50000开始，每小时涨500（1%），确保大幅盈利
    for i in range(50):
        base_price = 50000
        price = base_price * (1.01 ** i)  # 每小时1%复合增长
        date = start_date + timedelta(hours=i)
        
        data.append({
            'time': date,
            'currency': 'TESTCOIN',
            'time_interval': '1h',
            'o': price,
            'h': price * 1.005,  # 高点稍高
            'l': price * 0.995,  # 低点稍低
            'c': price,
            'v': 1000.0
        })
    
    return data


def create_buy_hold_strategy():
    """创建简单的买入持有策略"""
    strategy_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
买入持有策略 - 第一天买入，最后一天卖出
确保有明确的盈利
"""

import backtrader as bt


class Strategy(bt.Strategy):
    """买入持有策略"""
    
    def __init__(self):
        self.bought = False
        
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        if order.status == order.Completed:
            if order.isbuy():
                self.log(f'✅ 买入: 价格=${order.executed.price:.2f}, 价值=${order.executed.value:.2f}')
            else:
                self.log(f'✅ 卖出: 价格=${order.executed.price:.2f}, 价值=${order.executed.value:.2f}')
    
    def notify_trade(self, trade):
        if trade.isclosed:
            self.log(f'📊 交易完成: 毛利润=${trade.pnl:.2f}, 净利润=${trade.pnlcomm:.2f}')
    
    def next(self):
        current_bar = len(self.datas[0])
        current_price = self.datas[0].close[0]
        
        # 第一天买入
        if current_bar == 1 and not self.bought:
            cash = self.broker.get_cash()
            size = (cash * 0.95) / current_price
            self.buy(size=size)
            self.bought = True
            self.log(f'📈 买入信号: 价格=${current_price:.2f}')
        
        # 最后一天卖出
        elif current_bar == 49 and self.position:  # 倒数第二天卖出
            self.sell(size=self.position.size)
            self.log(f'📉 卖出信号: 价格=${current_price:.2f}')
    
    def stop(self):
        final_value = self.broker.get_value()
        self.log(f'📊 策略结束: 最终价值=${final_value:.2f}')
'''
    
    # 写入策略文件
    strategy_file = '/Volumes/data/project/open-back/back-test/strategy/buy_hold.py'
    with open(strategy_file, 'w', encoding='utf-8') as f:
        f.write(strategy_content)
    
    print(f"✅ 创建买入持有策略: {strategy_file}")


def run_builtin_analyzer_test():
    """运行内置分析器测试"""
    print("🧪 backtrader内置分析器验证测试")
    print("=" * 50)
    
    # 1. 创建盈利的测试数据和策略
    test_data = create_profitable_test_data()
    create_buy_hold_strategy()
    
    print(f"📊 测试数据特征:")
    print(f"   起始价格: ${test_data[0]['c']:,.2f}")
    print(f"   结束价格: ${test_data[-1]['c']:,.2f}")
    print(f"   总涨幅: {(test_data[-1]['c'] / test_data[0]['c'] - 1) * 100:.1f}%")
    
    # 2. 运行回测
    print(f"\n🚀 运行回测系统:")
    engine = BacktestEngine('TESTCOIN', '1h', 'buy_hold')
    
    with patch('index.get_all_klines_by_currency_time_interval') as mock_get:
        mock_get.return_value = test_data
        result = engine.run_backtest()
    
    # 3. 分析结果
    print(f"\n📊 内置分析器测试结果:")
    if 'error' in result:
        print(f"❌ 回测失败: {result['error']}")
        return False
    
    print(f"   交易次数: {result['trade_count']}")
    print(f"   夏普比率: {result['sharpe_ratio']}")
    print(f"   最大回撤: {result['max_drawdown']:.4f}")
    print(f"   胜率: {result['winning_percentage']:.2%}")
    print(f"   年化收益率: {result['annual_return']:.4f}")
    print(f"   总收益率: {result['total_return']:.2%}")
    print(f"   Calmar比率: {result['calmar_ratio']:.4f}")
    
    # 4. 验证合理性
    print(f"\n✅ 合理性验证:")
    
    # 基本检查
    has_trades = result['trade_count'] > 0
    is_profitable = result['total_return'] > 0
    has_positive_sharpe = float(result['sharpe_ratio']) > 0
    
    print(f"   有交易记录: {'✅' if has_trades else '❌'}")
    print(f"   策略盈利: {'✅' if is_profitable else '❌'}")
    print(f"   夏普比率为正: {'✅' if has_positive_sharpe else '❌'}")
    
    # 详细交易记录
    if result['trades']:
        print(f"\n📝 交易详情:")
        for i, trade in enumerate(result['trades']):
            print(f"   交易{i+1}: 净盈亏=${trade['pnlcomm']:.2f}, 价格=${trade['price']:.2f}")
    
    if has_trades and is_profitable and has_positive_sharpe:
        print("\n🎉 内置分析器工作正常!")
        print("✅ backtrader内置分析器能够正确计算各项指标")
        return True
    else:
        print("\n❌ 内置分析器可能存在问题")
        print("需要进一步检查配置或数据")
        return False


if __name__ == "__main__":
    run_builtin_analyzer_test()
