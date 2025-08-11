"""
Kline 表的数据访问层
实现基础的 CRUD 操作
"""

import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.mysql.index import get_cursor, execute_query, execute_update, execute_many


class KlineDAO:
    """Kline 数据访问对象"""
    
    TABLE_NAME = "kline"
    
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """
        创建 Kline 记录
        Args:
            data: 包含 kline 数据的字典
        Returns:
            新创建记录的 ID
        """
        fields = [
            'currency', 'time_interval', 'time', 'o', 'h', 'l', 'c', 'v', 
            'extra', 'comment'
        ]
        
        # 过滤有效字段
        valid_data = {k: v for k, v in data.items() if k in fields and v is not None}
        
        if not valid_data:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        field_names = ', '.join(valid_data.keys())
        placeholders = ', '.join(['%s'] * len(valid_data))
        sql = f"INSERT INTO {KlineDAO.TABLE_NAME} ({field_names}) VALUES ({placeholders})"
        
        with get_cursor() as cursor:
            cursor.execute(sql, tuple(valid_data.values()))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(kline_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取 Kline 记录
        Args:
            kline_id: Kline 记录 ID
        Returns:
            Kline 记录字典，如果不存在则返回 None
        """
        sql = f"SELECT * FROM {KlineDAO.TABLE_NAME} WHERE id = %s"
        results = execute_query(sql, (kline_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_currency(currency: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据货币获取 Kline 记录
        Args:
            currency: 货币名称
            limit: 限制返回记录数
        Returns:
            Kline 记录列表
        """
        sql = f"SELECT * FROM {KlineDAO.TABLE_NAME} WHERE currency = %s ORDER BY time DESC LIMIT %s"
        return execute_query(sql, (currency, limit))
    
    @staticmethod
    def get_by_currency_time_interval(currency: str, time_interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据货币和时间间隔获取 Kline 记录
        Args:
            currency: 货币名称
            time_interval: 时间间隔
            limit: 限制返回记录数
        Returns:
            Kline 记录列表
        """
        sql = f"SELECT * FROM {KlineDAO.TABLE_NAME} WHERE currency = %s AND time_interval = %s ORDER BY time DESC LIMIT %s"
        return execute_query(sql, (currency, time_interval, limit))
    
    @staticmethod
    def get_by_time_range(currency: str, time_interval: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """
        根据时间范围获取 Kline 记录
        Args:
            currency: 货币名称
            time_interval: 时间间隔
            start_time: 开始时间
            end_time: 结束时间
        Returns:
            Kline 记录列表
        """
        sql = f"SELECT * FROM {KlineDAO.TABLE_NAME} WHERE currency = %s AND time_interval = %s AND time BETWEEN %s AND %s ORDER BY time ASC"
        return execute_query(sql, (currency, time_interval, start_time, end_time))
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有 Kline 记录
        Args:
            limit: 限制返回记录数
            offset: 偏移量
        Returns:
            Kline 记录列表
        """
        sql = f"SELECT * FROM {KlineDAO.TABLE_NAME} ORDER BY time DESC LIMIT %s OFFSET %s"
        return execute_query(sql, (limit, offset))
    
    @staticmethod
    def update(kline_id: int, data: Dict[str, Any]) -> bool:
        """
        更新 Kline 记录
        Args:
            kline_id: Kline 记录 ID
            data: 要更新的数据字典
        Returns:
            更新是否成功
        """
        fields = [
            'currency', 'time_interval', 'time', 'o', 'h', 'l', 'c', 'v', 
            'extra', 'comment'
        ]
        
        # 过滤有效字段
        valid_data = {k: v for k, v in data.items() if k in fields and v is not None}
        
        if not valid_data:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        set_clause = ', '.join([f"{k} = %s" for k in valid_data.keys()])
        sql = f"UPDATE {KlineDAO.TABLE_NAME} SET {set_clause} WHERE id = %s"
        
        params = list(valid_data.values()) + [kline_id]
        affected_rows = execute_update(sql, tuple(params))
        return affected_rows > 0
    
    @staticmethod
    def delete(kline_id: int) -> bool:
        """
        删除 Kline 记录
        Args:
            kline_id: Kline 记录 ID
        Returns:
            删除是否成功
        """
        sql = f"DELETE FROM {KlineDAO.TABLE_NAME} WHERE id = %s"
        affected_rows = execute_update(sql, (kline_id,))
        return affected_rows > 0
    
    @staticmethod
    def batch_create(data_list: List[Dict[str, Any]]) -> int:
        """
        批量创建 Kline 记录
        Args:
            data_list: Kline 数据列表
        Returns:
            成功插入的记录数
        """
        if not data_list:
            return 0
        
        fields = [
            'currency', 'time_interval', 'time', 'o', 'h', 'l', 'c', 'v', 
            'extra', 'comment'
        ]
        
        # 获取第一个记录的所有字段
        first_record = data_list[0]
        valid_fields = [field for field in fields if field in first_record]
        
        if not valid_fields:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        field_names = ', '.join(valid_fields)
        placeholders = ', '.join(['%s'] * len(valid_fields))
        sql = f"INSERT INTO {KlineDAO.TABLE_NAME} ({field_names}) VALUES ({placeholders})"
        
        # 准备数据
        params_list = []
        for data in data_list:
            params = tuple(data.get(field) for field in valid_fields)
            params_list.append(params)
        
        return execute_many(sql, params_list)
    
    @staticmethod
    def count_by_currency(currency: str) -> int:
        """
        统计指定货币的 Kline 记录数量
        Args:
            currency: 货币名称
        Returns:
            记录数量
        """
        sql = f"SELECT COUNT(*) as count FROM {KlineDAO.TABLE_NAME} WHERE currency = %s"
        result = execute_query(sql, (currency,))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def get_latest_by_currency_time_interval(currency: str, time_interval: str) -> Optional[Dict[str, Any]]:
        """
        获取指定货币和时间间隔的最新 Kline 记录
        Args:
            currency: 货币名称
            time_interval: 时间间隔
        Returns:
            最新的 Kline 记录，如果不存在则返回 None
        """
        sql = f"SELECT * FROM {KlineDAO.TABLE_NAME} WHERE currency = %s AND time_interval = %s ORDER BY time DESC LIMIT 1"
        results = execute_query(sql, (currency, time_interval))
        return results[0] if results else None


# 便捷函数
def create_kline(data: Dict[str, Any]) -> int:
    """创建 Kline 记录"""
    return KlineDAO.create(data)


def get_kline_by_id(kline_id: int) -> Optional[Dict[str, Any]]:
    """根据 ID 获取 Kline 记录"""
    return KlineDAO.get_by_id(kline_id)


def get_klines_by_currency(currency: str, limit: int = 100) -> List[Dict[str, Any]]:
    """根据货币获取 Kline 记录"""
    return KlineDAO.get_by_currency(currency, limit)


def get_klines_by_currency_time_interval(currency: str, time_interval: str, limit: int = 100) -> List[Dict[str, Any]]:
    """根据货币和时间间隔获取 Kline 记录"""
    return KlineDAO.get_by_currency_time_interval(currency, time_interval, limit)


def update_kline(kline_id: int, data: Dict[str, Any]) -> bool:
    """更新 Kline 记录"""
    return KlineDAO.update(kline_id, data)


def delete_kline(kline_id: int) -> bool:
    """删除 Kline 记录"""
    return KlineDAO.delete(kline_id)


def batch_create_klines(data_list: List[Dict[str, Any]]) -> int:
    """批量创建 Kline 记录"""
    return KlineDAO.batch_create(data_list)


# 测试代码
if __name__ == "__main__":
    print("🧪 测试 Kline DAO...")
    
    try:
        # 测试创建
        test_data = {
            'currency': 'BTCUSDT',
            'time_interval': '1h',
            'time': datetime.now(),
            'o': 50000.0,
            'h': 51000.0,
            'l': 49000.0,
            'c': 50500.0,
            'v': 1000.0,
            'comment': '测试数据'
        }
        
        kline_id = create_kline(test_data)
        print(f"✅ 创建 Kline 记录成功，ID: {kline_id}")
        
        # 测试查询
        kline = get_kline_by_id(kline_id)
        print(f"✅ 查询 Kline 记录成功: {kline['currency']} - {kline['time_interval']}")
        
        # 测试更新
        update_data = {'comment': '更新后的测试数据'}
        success = update_kline(kline_id, update_data)
        print(f"✅ 更新 Kline 记录: {'成功' if success else '失败'}")
        
        # 测试按货币查询
        klines = get_klines_by_currency('BTCUSDT', 5)
        print(f"✅ 查询 BTCUSDT 记录数: {len(klines)}")
        
        # 测试按货币和时间间隔查询
        klines = get_klines_by_currency_time_interval('BTCUSDT', '1h', 5)
        print(f"✅ 查询 BTCUSDT 1h 记录数: {len(klines)}")
        
        # 测试删除
        success = delete_kline(kline_id)
        print(f"✅ 删除 Kline 记录: {'成功' if success else '失败'}")
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")