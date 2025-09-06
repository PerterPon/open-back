"""
StrategyContent 表的数据访问层
实现策略内容的 CRUD 操作，用于优化存储重复的策略内容
"""

import sys
import os
from typing import List, Dict, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.mysql.index_main import get_cursor, execute_query, execute_update, execute_many


class StrategyContentDAO:
    """StrategyContent 数据访问对象"""
    
    TABLE_NAME = "strategy_content"
    
    @staticmethod
    def create(content: str) -> int:
        """
        创建 StrategyContent 记录
        Args:
            content: 策略内容
        Returns:
            新创建记录的 ID
        """
        if not content or not content.strip():
            raise ValueError("策略内容不能为空")
        
        sql = f"INSERT INTO {StrategyContentDAO.TABLE_NAME} (content) VALUES (%s)"
        
        with get_cursor() as cursor:
            cursor.execute(sql, (content,))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(content_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取 StrategyContent 记录
        Args:
            content_id: 内容 ID
        Returns:
            StrategyContent 记录字典，如果不存在则返回 None
        """
        sql = f"SELECT * FROM {StrategyContentDAO.TABLE_NAME} WHERE id = %s"
        results = execute_query(sql, (content_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_content_by_id(content_id: int) -> Optional[str]:
        """
        根据 ID 获取策略内容
        Args:
            content_id: 内容 ID
        Returns:
            策略内容字符串，如果不存在则返回 None
        """
        record = StrategyContentDAO.get_by_id(content_id)
        return record['content'] if record else None
    
    @staticmethod
    def find_by_content(content: str) -> Optional[Dict[str, Any]]:
        """
        根据内容查找是否已存在相同的策略内容
        Args:
            content: 策略内容
        Returns:
            StrategyContent 记录字典，如果不存在则返回 None
        """
        if not content or not content.strip():
            return None
        
        sql = f"SELECT * FROM {StrategyContentDAO.TABLE_NAME} WHERE content = %s LIMIT 1"
        results = execute_query(sql, (content,))
        return results[0] if results else None
    
    @staticmethod
    def get_or_create(content: str) -> int:
        """
        获取或创建策略内容记录
        如果内容已存在，返回现有记录的 ID；否则创建新记录并返回 ID
        Args:
            content: 策略内容
        Returns:
            内容记录的 ID
        """
        if not content or not content.strip():
            raise ValueError("策略内容不能为空")
        
        # 先尝试查找是否已存在
        existing = StrategyContentDAO.find_by_content(content)
        if existing:
            return existing['id']
        
        # 不存在则创建新记录
        return StrategyContentDAO.create(content)
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有 StrategyContent 记录
        Args:
            limit: 限制返回记录数
            offset: 偏移量
        Returns:
            StrategyContent 记录列表
        """
        sql = f"SELECT * FROM {StrategyContentDAO.TABLE_NAME} ORDER BY gmt_create DESC LIMIT %s OFFSET %s"
        return execute_query(sql, (limit, offset))
    
    @staticmethod
    def update(content_id: int, content: str) -> bool:
        """
        更新 StrategyContent 记录
        Args:
            content_id: 内容 ID
            content: 新的策略内容
        Returns:
            更新是否成功
        """
        if not content or not content.strip():
            raise ValueError("策略内容不能为空")
        
        sql = f"UPDATE {StrategyContentDAO.TABLE_NAME} SET content = %s WHERE id = %s"
        affected_rows = execute_update(sql, (content, content_id))
        return affected_rows > 0
    
    @staticmethod
    def delete(content_id: int) -> bool:
        """
        删除 StrategyContent 记录
        Args:
            content_id: 内容 ID
        Returns:
            删除是否成功
        """
        sql = f"DELETE FROM {StrategyContentDAO.TABLE_NAME} WHERE id = %s"
        affected_rows = execute_update(sql, (content_id,))
        return affected_rows > 0
    
    @staticmethod
    def count() -> int:
        """
        统计策略内容总数
        Returns:
            策略内容总数
        """
        sql = f"SELECT COUNT(*) as count FROM {StrategyContentDAO.TABLE_NAME}"
        result = execute_query(sql)
        return result[0]['count'] if result else 0
    
    @staticmethod
    def get_content_usage_stats() -> List[Dict[str, Any]]:
        """
        获取策略内容使用统计
        返回每个内容被多少个策略使用
        Returns:
            使用统计列表
        """
        sql = """
        SELECT 
            sc.id,
            sc.gmt_create,
            COUNT(s.id) as usage_count,
            SUBSTRING(sc.content, 1, 100) as content_preview
        FROM strategy_content sc
        LEFT JOIN strategy s ON s.content_id = sc.id
        GROUP BY sc.id, sc.gmt_create, sc.content
        ORDER BY usage_count DESC, sc.gmt_create DESC
        """
        return execute_query(sql)
    
    @staticmethod
    def cleanup_unused_content() -> int:
        """
        清理未被使用的策略内容
        删除没有被任何策略引用的内容记录
        Returns:
            删除的记录数
        """
        sql = """
        DELETE FROM strategy_content 
        WHERE id NOT IN (
            SELECT DISTINCT content_id 
            FROM strategy 
            WHERE content_id IS NOT NULL
        )
        """
        return execute_update(sql)


# 便捷函数
def create_strategy_content(content: str) -> int:
    """创建策略内容记录"""
    return StrategyContentDAO.create(content)


def get_strategy_content_by_id(content_id: int) -> Optional[Dict[str, Any]]:
    """根据 ID 获取策略内容记录"""
    return StrategyContentDAO.get_by_id(content_id)


def get_content_by_id(content_id: int) -> Optional[str]:
    """根据 ID 获取策略内容字符串"""
    return StrategyContentDAO.get_content_by_id(content_id)


def find_strategy_content_by_content(content: str) -> Optional[Dict[str, Any]]:
    """根据内容查找策略内容记录"""
    return StrategyContentDAO.find_by_content(content)


def get_or_create_strategy_content(content: str) -> int:
    """获取或创建策略内容记录"""
    return StrategyContentDAO.get_or_create(content)


def update_strategy_content(content_id: int, content: str) -> bool:
    """更新策略内容记录"""
    return StrategyContentDAO.update(content_id, content)


def delete_strategy_content(content_id: int) -> bool:
    """删除策略内容记录"""
    return StrategyContentDAO.delete(content_id)


def get_strategy_content_count() -> int:
    """获取策略内容总数"""
    return StrategyContentDAO.count()


def get_content_usage_statistics() -> List[Dict[str, Any]]:
    """获取策略内容使用统计"""
    return StrategyContentDAO.get_content_usage_stats()


def cleanup_unused_strategy_content() -> int:
    """清理未使用的策略内容"""
    return StrategyContentDAO.cleanup_unused_content()


# 测试代码
if __name__ == "__main__":
    print("🧪 测试 StrategyContent DAO...")
    
    try:
        # 测试创建
        test_content = """
import backtrader as bt

class TestStrategy(bt.Strategy):
    def __init__(self):
        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=20)
    
    def next(self):
        if not self.position:
            if self.data.close[0] > self.sma[0]:
                self.buy()
        else:
            if self.data.close[0] < self.sma[0]:
                self.sell()

Strategy = TestStrategy
        """.strip()
        
        content_id = create_strategy_content(test_content)
        print(f"✅ 创建策略内容记录成功，ID: {content_id}")
        
        # 测试查询
        content_record = get_strategy_content_by_id(content_id)
        print(f"✅ 查询策略内容记录成功: ID={content_record['id']}")
        
        # 测试根据内容查找
        found_record = find_strategy_content_by_content(test_content)
        print(f"✅ 根据内容查找记录成功: ID={found_record['id']}")
        
        # 测试 get_or_create（应该返回现有记录）
        existing_id = get_or_create_strategy_content(test_content)
        print(f"✅ get_or_create 返回现有记录: ID={existing_id} (应该等于 {content_id})")
        
        # 测试 get_or_create（创建新记录）
        new_content = test_content + "\n# 这是一个不同的策略"
        new_id = get_or_create_strategy_content(new_content)
        print(f"✅ get_or_create 创建新记录: ID={new_id}")
        
        # 测试获取内容字符串
        retrieved_content = get_content_by_id(content_id)
        print(f"✅ 获取内容字符串成功: 长度={len(retrieved_content)}")
        
        # 测试统计
        total_count = get_strategy_content_count()
        print(f"✅ 策略内容总数: {total_count}")
        
        # 测试更新
        updated_content = test_content + "\n# 已更新"
        success = update_strategy_content(new_id, updated_content)
        print(f"✅ 更新策略内容: {'成功' if success else '失败'}")
        
        # 测试删除
        success1 = delete_strategy_content(content_id)
        success2 = delete_strategy_content(new_id)
        print(f"✅ 删除策略内容记录: {'成功' if success1 and success2 else '失败'}")
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
