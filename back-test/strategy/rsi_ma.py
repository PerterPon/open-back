#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSI + 移动平均策略 (RSI + Moving Average Strategy)

策略逻辑：
1. 使用RSI指标判断超买超卖
2. 结合移动平均线确认趋势方向
3. 买入条件：RSI < 30 且价格在均线上方
4. 卖出条件：RSI > 70 或价格跌破均线
5. 使用止损和止盈机制

注意：这个文件只包含策略逻辑，不包含任何其他业务逻辑
"""

import backtrader as bt


class Strategy(bt.Strategy):
    """RSI + 移动平均策略"""
    
    params = (
        ('rsi_period', 14),      # RSI周期
        ('rsi_oversold', 30),    # RSI超卖阈值
        ('rsi_overbought', 70),  # RSI超买阈值
        ('ma_period', 20),       # 移动平均线周期
        ('position_size', 0.9),  # 仓位大小（90%资金）
        ('stop_loss', 0.05),     # 止损比例（5%）
        ('take_profit', 0.15),   # 止盈比例（15%）
    )
    
    def __init__(self):
        """初始化策略"""
        # 计算技术指标
        self.rsi = bt.indicators.RSI(
            self.datas[0].close,
            period=self.params.rsi_period
        )
        
        self.ma = bt.indicators.SimpleMovingAverage(
            self.datas[0].close,
            period=self.params.ma_period
        )
        
        # 记录交易状态
        self.order = None
        self.buy_price = None
        self.buy_size = None
        
        # 打印策略参数
        self.log(f'策略参数: RSI周期={self.params.rsi_period}, MA周期={self.params.ma_period}')
        self.log(f'RSI阈值: 超卖={self.params.rsi_oversold}, 超买={self.params.rsi_overbought}')
        self.log(f'风控参数: 止损={self.params.stop_loss:.1%}, 止盈={self.params.take_profit:.1%}')
    
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
                self.buy_price = order.executed.price
                self.buy_size = order.executed.size
                self.log(f'买入执行: 价格={order.executed.price:.2f}, 数量={order.executed.size:.4f}, 成本={order.executed.value:.2f}, 手续费={order.executed.comm:.2f}')
            else:
                self.log(f'卖出执行: 价格={order.executed.price:.2f}, 数量={order.executed.size:.4f}, 价值={order.executed.value:.2f}, 手续费={order.executed.comm:.2f}')
                # 计算收益率
                if self.buy_price:
                    profit_rate = (order.executed.price - self.buy_price) / self.buy_price
                    self.log(f'本次交易收益率: {profit_rate:.2%}')
        
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
        
        # 获取当前价格和指标值
        current_price = self.datas[0].close[0]
        current_rsi = self.rsi[0]
        current_ma = self.ma[0]
        
        # 检查是否有足够的数据
        if len(self.datas[0]) < max(self.params.rsi_period, self.params.ma_period):
            return
        
        # 如果没有持仓
        if not self.position:
            # 买入条件：RSI超卖且价格在均线上方
            if (current_rsi < self.params.rsi_oversold and 
                current_price > current_ma):
                
                # 计算买入数量
                cash = self.broker.get_cash()
                size = (cash * self.params.position_size) / current_price
                
                if size > 0:
                    self.log(f'买入信号: 价格={current_price:.2f}, RSI={current_rsi:.1f}, MA={current_ma:.2f}')
                    self.order = self.buy(size=size)
        
        else:
            # 已有持仓，检查卖出条件
            should_sell = False
            sell_reason = ""
            
            # 条件1：RSI超买
            if current_rsi > self.params.rsi_overbought:
                should_sell = True
                sell_reason = f"RSI超买({current_rsi:.1f})"
            
            # 条件2：价格跌破均线
            elif current_price < current_ma:
                should_sell = True
                sell_reason = f"跌破均线(价格={current_price:.2f}, MA={current_ma:.2f})"
            
            # 条件3：止损
            elif self.buy_price and (current_price <= self.buy_price * (1 - self.params.stop_loss)):
                should_sell = True
                sell_reason = f"止损(买入价={self.buy_price:.2f}, 当前价={current_price:.2f})"
            
            # 条件4：止盈
            elif self.buy_price and (current_price >= self.buy_price * (1 + self.params.take_profit)):
                should_sell = True
                sell_reason = f"止盈(买入价={self.buy_price:.2f}, 当前价={current_price:.2f})"
            
            if should_sell:
                self.log(f'卖出信号: {sell_reason}')
                self.order = self.sell(size=self.position.size)
    
    def stop(self):
        """策略结束时调用"""
        final_value = self.broker.get_value()
        self.log(f'策略结束: 最终价值={final_value:.2f}')
        self.log(f'策略参数汇总: RSI({self.params.rsi_period},{self.params.rsi_oversold},{self.params.rsi_overbought}), MA({self.params.ma_period}), 仓位({self.params.position_size}), 止损({self.params.stop_loss:.1%}), 止盈({self.params.take_profit:.1%})')
