#!/usr/bin/env python3
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
