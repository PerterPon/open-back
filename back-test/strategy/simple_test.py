#!/usr/bin/env python3
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
