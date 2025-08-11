#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证夏普比率计算准确性的脚本

这个脚本：
1. 生成可预测的测试数据
2. 使用可预测的策略进行回测
3. 手工计算预期的夏普比率
4. 对比系统计算的结果与预期结果
5. 验证计算逻辑的准确性
"""

import sys
import os
from unittest.mock import patch
import numpy as np
import math

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(__file__))

from index import BacktestEngine
from test_data_generator import create_predictable_kline_data, calculate_expected_returns_and_sharpe


def manual_sharpe_calculation(returns_list, time_interval='1h', data_length=100):
    """
    手工计算夏普比率，用于验证系统计算的准确性
    
    Args:
        returns_list: 收益率列表
        time_interval: 时间间隔
        data_length: 数据长度
        
    Returns:
        手工计算的夏普比率
    """
    if not returns_list or len(returns_list) < 2:
        return 0.0
    
    returns_array = np.array(returns_list)
    mean_return = np.mean(returns_array)
    std_return = np.std(returns_array, ddof=1)
    
    if std_return == 0:
        return 0.0
    
    print(f"\n🧮 手工计算过程：")
    print(f"   收益率数量: {len(returns_list)}")
    print(f"   平均收益率: {mean_return:.8f}")
    print(f"   收益率标准差: {std_return:.8f}")
    
    # 根据时间间隔确定年化因子
    if time_interval == '1h':
        periods_per_year = 365 * 24  # 每年小时数
    else:
        periods_per_year = 365  # 默认天数
    
    # 计算交易频率（每10小时一次交易）
    trades_per_year = periods_per_year / 10
    
    print(f"   年化交易次数: {trades_per_year:.2f}")
    
    # 年化收益率和波动率
    annualized_return = mean_return * trades_per_year
    annualized_volatility = std_return * math.sqrt(trades_per_year)
    
    print(f"   年化收益率: {annualized_return:.6f}")
    print(f"   年化波动率: {annualized_volatility:.6f}")
    
    # 计算夏普比率
    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility > 0 else 0.0
    
    print(f"   手工计算夏普比率: {sharpe_ratio:.6f}")
    
    return sharpe_ratio


def run_verification():
    """运行验证测试"""
    print("🔍 开始验证夏普比率计算准确性...")
    print("=" * 70)
    
    # 1. 生成测试数据
    print("\n📊 步骤1: 生成可预测的测试数据")
    test_data = create_predictable_kline_data(periods=100)
    
    # 2. 计算预期结果
    print("\n🎯 步骤2: 计算预期的交易结果")
    expected = calculate_expected_returns_and_sharpe(test_data, trade_frequency=10)
    
    print(f"预期结果:")
    print(f"   交易次数: {expected['trade_count']}")
    print(f"   预期夏普比率: {expected['sharpe_ratio']:.6f}")
    
    # 3. 手工验证计算
    manual_sharpe = manual_sharpe_calculation(expected['returns'], '1h', 100)
    
    # 4. 运行回测系统
    print(f"\n🚀 步骤3: 运行回测系统")
    
    # 创建回测引擎
    engine = BacktestEngine('TESTCOIN', '1h', 'test_predictable')
    
    # Mock数据库调用
    with patch('index.get_all_klines_by_currency_time_interval') as mock_get:
        mock_get.return_value = test_data
        
        # 执行回测
        result = engine.run_backtest()
    
    # 5. 对比结果
    print(f"\n📋 步骤4: 结果对比")
    print("=" * 50)
    
    if 'error' in result:
        print(f"❌ 回测执行失败: {result['error']}")
        return False
    
    system_sharpe = float(result['sharpe_ratio'])
    
    print(f"📊 详细对比:")
    print(f"   交易次数:")
    print(f"      预期: {expected['trade_count']}")
    print(f"      实际: {result['trade_count']}")
    
    # 分析实际交易收益率
    if 'trades' in result and result['trades']:
        actual_returns = []
        print(f"   实际交易详情:")
        for i, trade in enumerate(result['trades']):
            if 'pnlcomm' in trade and trade['pnlcomm'] is not None:
                # 假设每次交易使用95%的资金
                trade_return = trade['pnlcomm'] / 10000  # 简化计算
                actual_returns.append(trade_return)
                print(f"      交易{i+1}: 净盈亏=${trade['pnlcomm']:.2f}, 收益率≈{trade_return:.6f}")
        
        if actual_returns:
            actual_mean = np.mean(actual_returns)
            actual_std = np.std(actual_returns, ddof=1) if len(actual_returns) > 1 else 0
            print(f"   实际收益率统计:")
            print(f"      平均收益率: {actual_mean:.6f}")
            print(f"      收益率标准差: {actual_std:.6f}")
    
    print(f"   夏普比率:")
    print(f"      手工计算: {expected['sharpe_ratio']:.6f}")
    print(f"      手工验证: {manual_sharpe:.6f}")
    print(f"      系统计算: {system_sharpe:.6f}")
    
    print(f"   其他指标:")
    print(f"      最大回撤: {result['max_drawdown']:.4f}")
    print(f"      胜率: {result['winning_percentage']:.4f}")
    print(f"      总手续费: {result['total_commission']:.2f}")
    
    # 分析交易次数差异的原因
    print(f"\n🔍 交易次数差异分析:")
    print(f"   数据长度: {len(test_data)}小时")
    print(f"   预期交易间隔: 10小时")
    print(f"   理论最大交易次数: {len(test_data) // 10}")
    print(f"   实际交易次数: {result['trade_count']}")
    
    if result['trade_count'] < expected['trade_count']:
        print(f"   ⚠️  实际交易次数少于预期，可能原因:")
        print(f"      - 数据长度不足以完成所有预期交易")
        print(f"      - 策略逻辑与预期不完全一致")
    
    # 6. 验证准确性
    print(f"\n✅ 步骤5: 准确性验证")
    print("=" * 30)
    
    # 允许一定的数值误差（由于浮点运算精度）
    tolerance = 0.001
    
    sharpe_diff_expected = abs(system_sharpe - expected['sharpe_ratio'])
    sharpe_diff_manual = abs(system_sharpe - manual_sharpe)
    
    print(f"夏普比率差异:")
    print(f"   系统 vs 预期: {sharpe_diff_expected:.8f}")
    print(f"   系统 vs 手工: {sharpe_diff_manual:.8f}")
    print(f"   允许误差: {tolerance:.8f}")
    
    if sharpe_diff_expected <= tolerance and sharpe_diff_manual <= tolerance:
        print("🎉 验证成功! 夏普比率计算准确性通过验证")
        return True
    else:
        print("❌ 验证失败! 夏普比率计算存在偏差")
        
        if sharpe_diff_expected > tolerance:
            print(f"   系统计算与预期值差异过大: {sharpe_diff_expected:.8f} > {tolerance}")
        
        if sharpe_diff_manual > tolerance:
            print(f"   系统计算与手工验证差异过大: {sharpe_diff_manual:.8f} > {tolerance}")
        
        return False


def main():
    """主函数"""
    print("🧪 夏普比率计算准确性验证工具")
    print("=" * 70)
    print("这个工具将验证回测系统中夏普比率计算的准确性")
    print("通过使用可预测的数据和策略，我们可以验证计算逻辑是否正确")
    
    try:
        success = run_verification()
        
        print("\n" + "=" * 70)
        if success:
            print("✅ 验证完成: 夏普比率计算逻辑正确!")
        else:
            print("❌ 验证失败: 夏普比率计算逻辑需要检查!")
            
    except Exception as e:
        print(f"❌ 验证过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
