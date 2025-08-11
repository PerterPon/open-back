#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成器 - 用于验证夏普比率计算准确性

这个模块创建可预测的K线数据，使我们能够手工计算预期的夏普比率
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json


def create_predictable_kline_data(periods: int = 100, base_price: float = 50000.0) -> List[Dict[str, Any]]:
    """
    创建可预测的K线数据
    
    策略设计：
    1. 基础趋势：价格每小时上涨0.1%
    2. 添加小幅随机波动，使收益率有一定变化
    3. 每10小时进行一次买入，持有10小时后卖出
    4. 这样可以产生可预测但有变化的收益率序列
    
    Args:
        periods: 数据点数量
        base_price: 基础价格
        
    Returns:
        K线数据列表
    """
    # 生成时间序列（每小时一个数据点）
    start_date = datetime(2024, 1, 1, 0, 0, 0)
    dates = [start_date + timedelta(hours=i) for i in range(periods)]
    
    # 设置随机种子以确保结果可重复
    np.random.seed(12345)
    
    data = []
    
    for i, date in enumerate(dates):
        # 基础趋势：每小时上涨0.1%
        base_growth = 1.001 ** i
        
        # 添加小幅随机波动（±0.05%）
        random_factor = 1 + np.random.normal(0, 0.0005)
        
        # 计算当前价格
        current_price = base_price * base_growth * random_factor
        
        # 生成OHLCV，添加小幅日内波动
        intraday_volatility = 0.002  # 0.2%的日内波动
        open_price = current_price * (1 + np.random.normal(0, intraday_volatility))
        high_price = current_price * (1 + abs(np.random.normal(0, intraday_volatility)))
        low_price = current_price * (1 - abs(np.random.normal(0, intraday_volatility)))
        close_price = current_price
        
        # 确保价格逻辑正确
        high_price = max(high_price, open_price, close_price)
        low_price = min(low_price, open_price, close_price)
        
        volume = np.random.uniform(800, 1200)  # 随机成交量
        
        data.append({
            'time': date,
            'currency': 'TESTCOIN',
            'time_interval': '1h',
            'o': round(open_price, 2),
            'h': round(high_price, 2),
            'l': round(low_price, 2),
            'c': round(close_price, 2),
            'v': round(volume, 2)
        })
    
    return data


def calculate_expected_returns_and_sharpe(data: List[Dict[str, Any]], 
                                        trade_frequency: int = 10) -> Dict[str, float]:
    """
    根据测试策略计算预期的收益率和夏普比率
    
    测试策略：
    - 每trade_frequency个小时买入一次
    - 持有trade_frequency个小时后卖出
    - 每次使用95%的资金
    
    Args:
        data: K线数据
        trade_frequency: 交易频率（每多少个小时交易一次）
        
    Returns:
        包含预期收益率和夏普比率的字典
    """
    prices = [item['c'] for item in data]
    returns = []
    
    # 模拟策略交易
    i = 0
    while i + trade_frequency < len(prices):
        buy_price = prices[i]
        sell_price = prices[i + trade_frequency]
        
        # 计算收益率（扣除0.1%手续费，买入和卖出各0.05%）
        gross_return = (sell_price - buy_price) / buy_price
        net_return = gross_return - 0.001  # 总手续费0.1%
        
        returns.append(net_return)
        i += trade_frequency
    
    if not returns:
        return {'mean_return': 0, 'std_return': 0, 'sharpe_ratio': 0, 'trade_count': 0}
    
    # 计算统计指标
    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)
    
    # 年化夏普比率计算
    # 每trade_frequency小时交易一次，一年有8760小时
    trades_per_year = 8760 / trade_frequency
    
    if std_return > 0:
        # 年化收益率和波动率
        annualized_return = mean_return * trades_per_year
        annualized_volatility = std_return * np.sqrt(trades_per_year)
        sharpe_ratio = annualized_return / annualized_volatility
    else:
        sharpe_ratio = 0
    
    return {
        'returns': returns,
        'mean_return': mean_return,
        'std_return': std_return,
        'annualized_return': annualized_return,
        'annualized_volatility': annualized_volatility,
        'sharpe_ratio': sharpe_ratio,
        'trade_count': len(returns),
        'trades_per_year': trades_per_year
    }


def print_test_analysis():
    """打印测试数据分析"""
    print("📊 创建测试数据并计算预期结果...")
    
    # 创建测试数据
    test_data = create_predictable_kline_data(periods=100)
    
    # 计算预期结果
    expected = calculate_expected_returns_and_sharpe(test_data, trade_frequency=10)
    
    print(f"\n📈 测试数据特征：")
    print(f"   数据点数量: {len(test_data)}")
    print(f"   起始价格: ${test_data[0]['c']:,.2f}")
    print(f"   结束价格: ${test_data[-1]['c']:,.2f}")
    print(f"   总价格涨幅: {(test_data[-1]['c'] / test_data[0]['c'] - 1) * 100:.2f}%")
    
    print(f"\n🎯 预期交易结果：")
    print(f"   交易次数: {expected['trade_count']}")
    print(f"   平均收益率: {expected['mean_return']:.6f}")
    print(f"   收益率标准差: {expected['std_return']:.6f}")
    print(f"   年化收益率: {expected['annualized_return']:.4f}")
    print(f"   年化波动率: {expected['annualized_volatility']:.4f}")
    print(f"   预期夏普比率: {expected['sharpe_ratio']:.4f}")
    
    # 显示前几笔交易的收益率
    print(f"\n📝 前5笔交易收益率:")
    for i, ret in enumerate(expected['returns'][:5]):
        print(f"   交易{i+1}: {ret:.6f} ({ret*100:.4f}%)")
    
    return test_data, expected


if __name__ == "__main__":
    print_test_analysis()
