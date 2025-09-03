"""
Strategy 相关的 API 路由
处理策略数据的获取和管理
"""

from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, List, Union
import os
import sys

# 动态添加项目根目录到 Python 路径
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.mysql.strategy import StrategyDAO
from core.mysql.index_main import execute_query


def register_strategy_routes(app: Flask) -> None:
    """
    注册 strategy 相关的路由
    
    Args:
        app: Flask 应用实例
    """
    
    @app.route('/api', methods=['POST'])
    def api_handler() -> tuple[Dict[str, Any], int]:
        """
        统一的 API 处理器
        根据 body 中的 method 字段分发到具体的处理函数
        
        Returns:
            统一格式的 JSON 响应和 HTTP 状态码
        """
        try:
            # 获取请求数据
            if not request.is_json:
                return create_error_response("请求必须是 JSON 格式", 400)
            
            body = request.get_json()
            if not body:
                return create_error_response("请求体不能为空", 400)
            
            method = body.get('method')
            if not method:
                return create_error_response("缺少必要的 method 参数", 400)
            
            data = body.get('data', {})
            
            # 根据 method 分发到具体的处理函数
            if method == 'getStrategy':
                return handle_get_strategy(data)
            else:
                return create_error_response(f"不支持的方法：{method}", 400)
                
        except Exception as e:
            return create_error_response(f"处理请求时发生错误：{str(e)}", 500)


def create_success_response(data: Any, message: str = "") -> tuple[Dict[str, Any], int]:
    """
    创建成功响应
    
    Args:
        data: 响应数据
        message: 消息（成功时通常为空字符串）
    
    Returns:
        格式化的成功响应和 200 状态码
    """
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return response, 200


def create_error_response(message: str, status_code: int = 500) -> tuple[Dict[str, Any], int]:
    """
    创建错误响应
    
    Args:
        message: 错误消息
        status_code: HTTP 状态码
    
    Returns:
        格式化的错误响应和对应状态码
    """
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    return response, status_code


def handle_get_strategy(data: Dict[str, Any]) -> tuple[Dict[str, Any], int]:
    """
    处理 getStrategy 请求
    
    Args:
        data: 请求参数
    
    Returns:
        策略列表响应
    """
    try:
        # 解析参数并设置默认值
        page = data.get('page', 1)
        page_size = data.get('pageSize', 20)
        order_by = data.get('orderBy')
        order = data.get('order', 'asc')
        
        # 参数验证
        if not isinstance(page, int) or page < 1:
            return create_error_response("page 参数必须是大于 0 的整数", 400)
        
        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            return create_error_response("pageSize 参数必须是 1-100 之间的整数", 400)
        
        # 验证 orderBy 参数 - API 参数名到数据库字段名的映射
        order_by_mapping = {
            'sharpe_ratio': 'sharpe_ratio',
            'findal_balance': 'final_balance',  # 注意：API 用 findal_balance，数据库用 final_balance
            'max_drawdown': 'max_drawdown',
            'trade_count': 'trade_count',
            'total_commission': 'total_commission',
            'winning_percetage': 'winning_percentage'  # 注意：API 用 winning_percetage，数据库用 winning_percentage
        }
        
        if order_by and order_by not in order_by_mapping:
            return create_error_response(f"orderBy 参数必须是以下值之一：{', '.join(order_by_mapping.keys())}", 400)
        
        # 转换为数据库字段名
        db_order_by = order_by_mapping.get(order_by) if order_by else None
        
        # 验证 order 参数
        if order not in ['asc', 'desc']:
            return create_error_response("order 参数必须是'asc'或'desc'", 400)
        
        # 从数据库获取真实数据
        try:
            strategy_data = get_strategies_from_db(page, page_size, db_order_by, order)
            return create_success_response(strategy_data)
        except Exception as db_error:
            return create_error_response(f"数据库查询失败：{str(db_error)}", 500)
        
    except Exception as e:
        return create_error_response(f"获取策略数据失败：{str(e)}", 500)


def get_strategies_from_db(page: int, page_size: int, order_by: Optional[str], order: str) -> Dict[str, Any]:
    """
    从数据库获取策略数据
    
    Args:
        page: 当前页
        page_size: 每页数量
        order_by: 排序字段（数据库字段名）
        order: 排序方向
    
    Returns:
        包含策略列表和分页信息的字典
    """
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 构建基础查询 SQL
    base_sql = "SELECT * FROM strategy"
    count_sql = "SELECT COUNT(*) as total FROM strategy"
    
    # 添加排序
    if order_by:
        order_clause = f" ORDER BY {order_by} {order.upper()}"
    else:
        order_clause = " ORDER BY gmt_create DESC"  # 默认按创建时间降序
    
    # 添加分页
    limit_clause = f" LIMIT {page_size} OFFSET {offset}"
    
    # 完整的查询 SQL
    query_sql = base_sql + order_clause + limit_clause
    
    try:
        # 查询总数
        total_result = execute_query(count_sql)
        total_count = total_result[0]['total'] if total_result else 0
        
        # 查询策略数据
        strategies_raw = execute_query(query_sql)
        
        # 转换数据格式，将数据库字段名转换为 API 字段名
        strategies = []
        for strategy in strategies_raw:
            converted_strategy = convert_db_to_api_format(strategy)
            strategies.append(converted_strategy)
        
        # 计算分页信息
        total_pages = (total_count + page_size - 1) // page_size
        
        return {
            "strategies": strategies,
            "pagination": {
                "page": page,
                "pageSize": page_size,
                "total": total_count,
                "totalPages": total_pages,
                "hasNext": page < total_pages,
                "hasPrev": page > 1
            },
            "sorting": {
                "orderBy": order_by,
                "order": order
            }
        }
        
    except Exception as e:
        raise Exception(f"数据库查询失败：{str(e)}")


def convert_db_to_api_format(db_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    将数据库记录转换为 API 响应格式
    
    Args:
        db_record: 数据库记录
    
    Returns:
        API 格式的记录
    """
    return {
        "id": db_record.get('id'),
        "name": db_record.get('name'),
        "currency": db_record.get('currency'),
        "time_interval": db_record.get('time_interval'),
        "sharpe_ratio": db_record.get('sharpe_ratio'),
        "findal_balance": db_record.get('final_balance'),  # 数据库字段名转换
        "max_drawdown": db_record.get('max_drawdown'),
        "trade_count": db_record.get('trade_count'),
        "total_commission": db_record.get('total_commission'),
        "winning_percetage": db_record.get('winning_percentage'),  # 数据库字段名转换
        "init_balance": db_record.get('init_balance'),
        "reason": db_record.get('reason'),
        "extra": db_record.get('extra'),
        "created_at": db_record.get('gmt_create').isoformat() if db_record.get('gmt_create') else None,
        "updated_at": db_record.get('gmt_modify').isoformat() if db_record.get('gmt_modify') else None
    }
