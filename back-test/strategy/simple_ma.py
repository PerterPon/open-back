#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单移动平均策略 (Simple Moving Average Strategy)

策略逻辑：
1. 计算短期和长期移动平均线
2. 当短期均线上穿长期均线时买入
3. 当短期均线下穿长期均线时卖出
4. 每次交易使用固定比例的资金

注意：这个文件只包含策略逻辑，不包含任何其他业务逻辑
"""

import backtrader as bt


class Strategy(bt.Strategy):
    """简单移动平均策略"""
    
    params = (
        ('short_period', 10),   # 短期均线周期
        ('long_period', 30),    # 长期均线周期
        ('position_size', 0.95), # 仓位大小（95%资金）
    )
    
    def __init__(self):
        """初始化策略"""
        # 计算移动平均线
        self.short_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, 
            period=self.params.short_period
        )
        self.long_ma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close, 
            period=self.params.long_period
        )
        
        # 计算交叉信号
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)
        
        # 记录交易状态
        self.order = None
        
        # 打印策略参数
        self.log(f'策略参数: 短期均线={self.params.short_period}, 长期均线={self.params.long_period}')
    
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
                self.log(f'买入执行: 价格={order.executed.price:.2f}, 数量={order.executed.size:.4f}, 成本={order.executed.value:.2f}, 手续费={order.executed.comm:.2f}')
            else:
                self.log(f'卖出执行: 价格={order.executed.price:.2f}, 数量={order.executed.size:.4f}, 价值={order.executed.value:.2f}, 手续费={order.executed.comm:.2f}')
        
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('订单取消/拒绝/保证金不足')
        
        self.order = None
    
    def notify_trade(self, trade):
        """交易完成通知"""
        if not trade.isclosed:
            return
        
        self.log(f'交易完成: 毛利润={trade.pnl:.2f}, 净利润={trade.pnlcomm:.2f}')
    
    def next(self):
        """策略主逻辑"""
        # 如果有未完成的订单，等待
        if self.order:
            return
        
        # 获取当前价格
        current_price = self.datas[0].close[0]
        
        # 检查是否有足够的数据
        if len(self.datas[0]) < self.params.long_period:
            return
        
        # 如果没有持仓
        if not self.position:
            # 金叉：短期均线上穿长期均线，买入信号
            if self.crossover[0] > 0:
                # 计算买入数量
                cash = self.broker.get_cash()
                size = (cash * self.params.position_size) / current_price
                
                if size > 0:
                    self.log(f'买入信号: 价格={current_price:.2f}, 短期MA={self.short_ma[0]:.2f}, 长期MA={self.long_ma[0]:.2f}')
                    self.order = self.buy(size=size)
        
        else:
            # 死叉：短期均线下穿长期均线，卖出信号
            if self.crossover[0] < 0:
                self.log(f'卖出信号: 价格={current_price:.2f}, 短期MA={self.short_ma[0]:.2f}, 长期MA={self.long_ma[0]:.2f}')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """策略结束时调用"""
        final_value = self.broker.get_value()
        self.log(f'策略结束: 最终价值={final_value:.2f}')
        self.log(f'策略参数: 短期均线={self.params.short_period}, 长期均线={self.params.long_period}, 仓位比例={self.params.position_size}')
