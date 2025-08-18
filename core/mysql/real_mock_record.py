"""
Real Mock Record 表的数据访问层
实现基础的 CRUD 操作
"""

import sys
import os
from typing import List, Dict, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.mysql.index_main import get_cursor, execute_query, execute_update, execute_many


class RealMockRecordDAO:
    """Real Mock Record 数据访问对象"""
    
    TABLE_NAME = "real_mock_record"
    
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """
        创建 Real Mock Record 记录
        Args:
            data: 包含 real mock record 数据的字典
        Returns:
            新创建记录的 ID
        """
        fields = ['strategy_id', 'is_delete', 'comment']
        
        # 过滤有效字段
        valid_data = {k: v for k, v in data.items() if k in fields and v is not None}
        
        if not valid_data:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        field_names = ', '.join(valid_data.keys())
        placeholders = ', '.join(['%s'] * len(valid_data))
        sql = f"INSERT INTO {RealMockRecordDAO.TABLE_NAME} ({field_names}) VALUES ({placeholders})"
        
        with get_cursor() as cursor:
            cursor.execute(sql, tuple(valid_data.values()))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(record_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取 Real Mock Record 记录
        Args:
            record_id: 记录 ID
        Returns:
            Real Mock Record 记录字典，如果不存在则返回 None
        """
        sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} WHERE id = %s"
        results = execute_query(sql, (record_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_strategy_id(strategy_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据策略 ID 获取 Real Mock Record 记录
        Args:
            strategy_id: 策略 ID
            limit: 限制返回记录数
        Returns:
            Real Mock Record 记录列表
        """
        sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} WHERE strategy_id = %s ORDER BY gmt_create DESC LIMIT %s"
        return execute_query(sql, (strategy_id, limit))
    
    @staticmethod
    def get_active_records(strategy_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取活跃记录（未删除的记录）
        Args:
            strategy_id: 策略 ID，如果为 None 则获取所有策略的活跃记录
            limit: 限制返回记录数
        Returns:
            活跃记录列表
        """
        if strategy_id is not None:
            sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} WHERE strategy_id = %s AND (is_delete IS NULL OR is_delete = 0) ORDER BY gmt_create DESC LIMIT %s"
            return execute_query(sql, (strategy_id, limit))
        else:
            sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} WHERE is_delete IS NULL OR is_delete = 0 ORDER BY gmt_create DESC LIMIT %s"
            return execute_query(sql, (limit,))
    
    @staticmethod
    def get_deleted_records(strategy_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        获取已删除记录
        Args:
            strategy_id: 策略 ID，如果为 None 则获取所有策略的已删除记录
            limit: 限制返回记录数
        Returns:
            已删除记录列表
        """
        if strategy_id is not None:
            sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} WHERE strategy_id = %s AND is_delete = 1 ORDER BY gmt_create DESC LIMIT %s"
            return execute_query(sql, (strategy_id, limit))
        else:
            sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} WHERE is_delete = 1 ORDER BY gmt_create DESC LIMIT %s"
            return execute_query(sql, (limit,))
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有 Real Mock Record 记录
        Args:
            limit: 限制返回记录数
            offset: 偏移量
        Returns:
            Real Mock Record 记录列表
        """
        sql = f"SELECT * FROM {RealMockRecordDAO.TABLE_NAME} ORDER BY gmt_create DESC LIMIT %s OFFSET %s"
        return execute_query(sql, (limit, offset))
    
    @staticmethod
    def update(record_id: int, data: Dict[str, Any]) -> bool:
        """
        更新 Real Mock Record 记录
        Args:
            record_id: 记录 ID
            data: 要更新的数据字典
        Returns:
            更新是否成功
        """
        fields = ['strategy_id', 'is_delete', 'comment']
        
        # 过滤有效字段
        valid_data = {k: v for k, v in data.items() if k in fields and v is not None}
        
        if not valid_data:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        set_clause = ', '.join([f"{k} = %s" for k in valid_data.keys()])
        sql = f"UPDATE {RealMockRecordDAO.TABLE_NAME} SET {set_clause} WHERE id = %s"
        
        params = list(valid_data.values()) + [record_id]
        affected_rows = execute_update(sql, tuple(params))
        return affected_rows > 0
    
    @staticmethod
    def delete(record_id: int) -> bool:
        """
        删除 Real Mock Record 记录（物理删除）
        Args:
            record_id: 记录 ID
        Returns:
            删除是否成功
        """
        sql = f"DELETE FROM {RealMockRecordDAO.TABLE_NAME} WHERE id = %s"
        affected_rows = execute_update(sql, (record_id,))
        return affected_rows > 0
    
    @staticmethod
    def soft_delete(record_id: int) -> bool:
        """
        软删除 Real Mock Record 记录（标记为已删除）
        Args:
            record_id: 记录 ID
        Returns:
            软删除是否成功
        """
        return RealMockRecordDAO.update(record_id, {'is_delete': 1})
    
    @staticmethod
    def restore(record_id: int) -> bool:
        """
        恢复已删除的 Real Mock Record 记录
        Args:
            record_id: 记录 ID
        Returns:
            恢复是否成功
        """
        return RealMockRecordDAO.update(record_id, {'is_delete': 0})
    
    @staticmethod
    def batch_create(data_list: List[Dict[str, Any]]) -> int:
        """
        批量创建 Real Mock Record 记录
        Args:
            data_list: Real Mock Record 数据列表
        Returns:
            成功插入的记录数
        """
        if not data_list:
            return 0
        
        fields = ['strategy_id', 'is_delete', 'comment']
        
        # 获取第一个记录的所有字段
        first_record = data_list[0]
        valid_fields = [field for field in fields if field in first_record]
        
        if not valid_fields:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        field_names = ', '.join(valid_fields)
        placeholders = ', '.join(['%s'] * len(valid_fields))
        sql = f"INSERT INTO {RealMockRecordDAO.TABLE_NAME} ({field_names}) VALUES ({placeholders})"
        
        # 准备数据
        params_list = []
        for data in data_list:
            params = tuple(data.get(field) for field in valid_fields)
            params_list.append(params)
        
        return execute_many(sql, params_list)
    
    @staticmethod
    def count_by_strategy_id(strategy_id: int) -> int:
        """
        统计指定策略的 Real Mock Record 记录数量
        Args:
            strategy_id: 策略 ID
        Returns:
            记录数量
        """
        sql = f"SELECT COUNT(*) as count FROM {RealMockRecordDAO.TABLE_NAME} WHERE strategy_id = %s"
        result = execute_query(sql, (strategy_id,))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def count_active_by_strategy_id(strategy_id: int) -> int:
        """
        统计指定策略的活跃记录数量
        Args:
            strategy_id: 策略 ID
        Returns:
            活跃记录数量
        """
        sql = f"SELECT COUNT(*) as count FROM {RealMockRecordDAO.TABLE_NAME} WHERE strategy_id = %s AND (is_delete IS NULL OR is_delete = 0)"
        result = execute_query(sql, (strategy_id,))
        return result[0]['count'] if result else 0


# 便捷函数
def create_real_mock_record(data: Dict[str, Any]) -> int:
    """创建 Real Mock Record 记录"""
    return RealMockRecordDAO.create(data)


def get_real_mock_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
    """根据 ID 获取 Real Mock Record 记录"""
    return RealMockRecordDAO.get_by_id(record_id)


def get_real_mock_records_by_strategy_id(strategy_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    """根据策略 ID 获取 Real Mock Record 记录"""
    return RealMockRecordDAO.get_by_strategy_id(strategy_id, limit)


def get_active_real_mock_records(strategy_id: int = None, limit: int = 100) -> List[Dict[str, Any]]:
    """获取活跃记录"""
    return RealMockRecordDAO.get_active_records(strategy_id, limit)


def update_real_mock_record(record_id: int, data: Dict[str, Any]) -> bool:
    """更新 Real Mock Record 记录"""
    return RealMockRecordDAO.update(record_id, data)


def delete_real_mock_record(record_id: int) -> bool:
    """删除 Real Mock Record 记录（物理删除）"""
    return RealMockRecordDAO.delete(record_id)


def soft_delete_real_mock_record(record_id: int) -> bool:
    """软删除 Real Mock Record 记录"""
    return RealMockRecordDAO.soft_delete(record_id)


def restore_real_mock_record(record_id: int) -> bool:
    """恢复已删除的 Real Mock Record 记录"""
    return RealMockRecordDAO.restore(record_id)


def batch_create_real_mock_records(data_list: List[Dict[str, Any]]) -> int:
    """批量创建 Real Mock Record 记录"""
    return RealMockRecordDAO.batch_create(data_list)


# 测试代码
if __name__ == "__main__":
    print("🧪 测试 Real Mock Record DAO...")
    
    try:
        # 测试创建
        test_data = {
            'strategy_id': 1,
            'is_delete': 0,
            'comment': '测试模拟记录'
        }
        
        record_id = create_real_mock_record(test_data)
        print(f"✅ 创建 Real Mock Record 记录成功，ID: {record_id}")
        
        # 测试查询
        record = get_real_mock_record_by_id(record_id)
        print(f"✅ 查询 Real Mock Record 记录成功: 策略ID {record['strategy_id']}")
        
        # 测试更新
        update_data = {'comment': '更新后的测试模拟记录'}
        success = update_real_mock_record(record_id, update_data)
        print(f"✅ 更新 Real Mock Record 记录: {'成功' if success else '失败'}")
        
        # 测试按策略ID查询
        records = get_real_mock_records_by_strategy_id(1, 5)
        print(f"✅ 查询策略ID 1 的记录数: {len(records)}")
        
        # 测试获取活跃记录
        active_records = get_active_real_mock_records(1, 5)
        print(f"✅ 查询策略ID 1 的活跃记录数: {len(active_records)}")
        
        # 测试软删除
        success = soft_delete_real_mock_record(record_id)
        print(f"✅ 软删除 Real Mock Record 记录: {'成功' if success else '失败'}")
        
        # 测试恢复
        success = restore_real_mock_record(record_id)
        print(f"✅ 恢复 Real Mock Record 记录: {'成功' if success else '失败'}")
        
        # 测试物理删除
        success = delete_real_mock_record(record_id)
        print(f"✅ 物理删除 Real Mock Record 记录: {'成功' if success else '失败'}")
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
