#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可预测的测试策略

这个策略设计用于验证夏普比率计算的准确性：
1. 每10个小时买入一次
2. 持有10个小时后卖出
3. 使用95%的资金进行交易
4. 产生可预测的收益率序列

这样的设计使我们能够手工计算预期的夏普比率，然后与系统计算结果进行对比
"""

import backtrader as bt


class Strategy(bt.Strategy):
    """可预测的测试策略"""
    
    params = (
        ('trade_frequency', 10),  # 每10个小时交易一次
        ('position_size', 0.95),  # 使用95%的资金
    )
    
    def __init__(self):
        """初始化策略"""
        self.order = None
        self.trade_counter = 0
        self.buy_time = None
        self.buy_price = None
        
        print(f"🔧 测试策略初始化: 交易频率={self.params.trade_frequency}小时, 仓位大小={self.params.position_size}")
    
    def log(self, txt, dt=None):
        """记录日志"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()}: {txt}')
    
    def notify_order(self, order):
        """订单状态通知"""
        if order.status in [order.Submitted, order.Accepted]:
            return
        
        if order.status in [order.Completed]:
            if order.isbuy():
                self.buy_time = self.datas[0].datetime.datetime(0)
                self.buy_price = order.executed.price
                self.log(f'✅ 买入执行: 价格=${order.executed.price:.2f}, 数量={order.executed.size:.4f}, 总价值=${order.executed.value:.2f}')
            else:
                if self.buy_price:
                    hold_hours = (self.datas[0].datetime.datetime(0) - self.buy_time).total_seconds() / 3600
                    profit_rate = (order.executed.price - self.buy_price) / self.buy_price
                    self.log(f'✅ 卖出执行: 价格=${order.executed.price:.2f}, 持有时间={hold_hours:.0f}小时, 收益率={profit_rate:.4%}')
                else:
                    self.log(f'✅ 卖出执行: 价格=${order.executed.price:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('❌ 订单取消/拒绝/保证金不足')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易完成通知"""
        if not trade.isclosed:
            return
        
        self.log(f'📊 交易完成: 毛利润=${trade.pnl:.2f}, 净利润=${trade.pnlcomm:.2f}, 手续费=${trade.commission:.2f}')
    
    def next(self):
        """策略主逻辑"""
        # 如果有未完成的订单，等待
        if self.order:
            return
        
        current_price = self.datas[0].close[0]
        current_bar = len(self.datas[0])
        
        # 如果没有持仓
        if not self.position:
            # 每trade_frequency个小时买入一次（从第1个小时开始）
            if (current_bar - 1) % self.params.trade_frequency == 0 and current_bar > 1:
                # 计算买入数量
                cash = self.broker.get_cash()
                size = (cash * self.params.position_size) / current_price
                
                if size > 0:
                    self.trade_counter += 1
                    self.log(f'📈 发出买入信号 (第{self.trade_counter}次交易): 价格=${current_price:.2f}')
                    self.order = self.buy(size=size)
        
        else:
            # 已有持仓，检查是否应该卖出
            if self.buy_time:
                hold_hours = (self.datas[0].datetime.datetime(0) - self.buy_time).total_seconds() / 3600
                
                # 持有满trade_frequency小时后卖出
                if hold_hours >= self.params.trade_frequency:
                    self.log(f'📉 发出卖出信号: 价格=${current_price:.2f}, 已持有{hold_hours:.0f}小时')
                    self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """策略结束时调用"""
        final_value = self.broker.get_value()
        initial_value = 10000.0  # 初始资金
        total_return = (final_value - initial_value) / initial_value
        
        self.log(f'📊 策略结束统计:')
        self.log(f'   总交易次数: {self.trade_counter}')
        self.log(f'   初始资金: ${initial_value:,.2f}')
        self.log(f'   最终价值: ${final_value:,.2f}')
        self.log(f'   总收益率: {total_return:.4%}')
        self.log(f'   策略参数: 交易频率={self.params.trade_frequency}小时, 仓位大小={self.params.position_size}')
