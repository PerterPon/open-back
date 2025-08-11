#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试时间间隔解析的正确性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(__file__))

from index import BacktestEngine

def test_interval_parsing():
    """测试不同时间间隔的解析"""
    print("🧪 测试时间间隔解析")
    print("=" * 50)
    
    # 测试各种时间间隔
    test_intervals = [
        '1m',   # 1分钟 -> Minutes, 1
        '5m',   # 5分钟 -> Minutes, 5
        '15m',  # 15分钟 -> Minutes, 15
        '1h',   # 1小时 -> Hours, 1
        '4h',   # 4小时 -> Hours, 4
        '12h',  # 12小时 -> Hours, 12
        '1d',   # 1天 -> Days, 1
        '1w',   # 1周 -> Weeks, 1
        '1M',   # 1月 -> Months, 1
        'invalid' # 无效格式
    ]
    
    for interval in test_intervals:
        print(f"\n📊 测试时间间隔: '{interval}'")
        
        # 创建引擎实例来测试解析
        engine = BacktestEngine('TESTCOIN', interval, 'test_strategy')
        
        # 直接调用解析方法
        timeframe, compression = engine._parse_time_interval(interval)
        timeframe_name = engine._timeframe_name(timeframe)
        
        print(f"   结果: timeframe={timeframe_name}, compression={compression}")

if __name__ == "__main__":
    test_interval_parsing()
