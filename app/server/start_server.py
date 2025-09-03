#!/usr/bin/env python3
"""
服务器启动脚本
提供便捷的启动方式
"""

import os
import sys

# 动态设置项目根目录到 Python 路径
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
sys.path.insert(0, project_root)

from main import main

if __name__ == '__main__':
    main()
