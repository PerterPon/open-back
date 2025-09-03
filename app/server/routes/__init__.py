"""
路由模块
负责管理和注册所有 API 路由
"""

from flask import Flask
from .strategy_routes import register_strategy_routes


def register_routes(app: Flask) -> None:
    """
    注册所有路由到 Flask 应用
    
    Args:
        app: Flask 应用实例
    """
    
    # 注册策略相关路由
    register_strategy_routes(app)
    
    # 未来可以在这里添加更多路由模块
    # register_user_routes(app)
    # register_auth_routes(app)
    # register_data_routes(app)
