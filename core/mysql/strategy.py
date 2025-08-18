"""
Strategy 表的数据访问层
实现基础的 CRUD 操作
"""

import sys
import os
from typing import List, Dict, Any, Optional

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.mysql.index_main import get_cursor, execute_query, execute_update, execute_many


class StrategyDAO:
    """Strategy 数据访问对象"""
    
    TABLE_NAME = "strategy"
    
    @staticmethod
    def create(data: Dict[str, Any]) -> int:
        """
        创建 Strategy 记录
        Args:
            data: 包含 strategy 数据的字典
        Returns:
            新创建记录的 ID
        """
        fields = [
            'name', 'currency', 'time_interval', 'sharpe_ratio', 'trade_count', 
            'trades', 'total_commission', 'max_drawdown', 'winning_percentage',
            'reason', 'init_balance', 'final_balance', 'extra'
        ]
        
        # 过滤有效字段
        valid_data = {k: v for k, v in data.items() if k in fields and v is not None}
        
        if not valid_data:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        field_names = ', '.join(valid_data.keys())
        placeholders = ', '.join(['%s'] * len(valid_data))
        sql = f"INSERT INTO {StrategyDAO.TABLE_NAME} ({field_names}) VALUES ({placeholders})"
        
        with get_cursor() as cursor:
            cursor.execute(sql, tuple(valid_data.values()))
            return cursor.lastrowid
    
    @staticmethod
    def get_by_id(strategy_id: int) -> Optional[Dict[str, Any]]:
        """
        根据 ID 获取 Strategy 记录
        Args:
            strategy_id: 策略 ID
        Returns:
            Strategy 记录字典，如果不存在则返回 None
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE id = %s"
        results = execute_query(sql, (strategy_id,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_name(name: str) -> Optional[Dict[str, Any]]:
        """
        根据名称获取 Strategy 记录
        Args:
            name: 策略名称
        Returns:
            Strategy 记录字典，如果不存在则返回 None
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE name = %s"
        results = execute_query(sql, (name,))
        return results[0] if results else None
    
    @staticmethod
    def get_by_currency(currency: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据货币获取 Strategy 记录
        Args:
            currency: 货币名称
            limit: 限制返回记录数
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE currency = %s ORDER BY gmt_create DESC LIMIT %s"
        return execute_query(sql, (currency, limit))
    
    @staticmethod
    def get_by_currency_time_interval(currency: str, time_interval: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据货币和时间间隔获取 Strategy 记录
        Args:
            currency: 货币名称
            time_interval: 时间间隔
            limit: 限制返回记录数
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE currency = %s AND time_interval = %s ORDER BY gmt_create DESC LIMIT %s"
        return execute_query(sql, (currency, time_interval, limit))
    
    @staticmethod
    def get_top_strategies_by_sharpe_ratio(limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取按夏普比率排序的前N个策略
        Args:
            limit: 限制返回记录数
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE sharpe_ratio IS NOT NULL ORDER BY sharpe_ratio DESC LIMIT %s"
        return execute_query(sql, (limit,))
    
    @staticmethod
    def get_top_strategies_by_final_balance(limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取按最终余额排序的前N个策略
        Args:
            limit: 限制返回记录数
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE final_balance IS NOT NULL ORDER BY final_balance DESC LIMIT %s"
        return execute_query(sql, (limit,))
    
    @staticmethod
    def get_strategies_by_trade_count_range(min_count: int, max_count: int, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据交易次数范围获取策略
        Args:
            min_count: 最小交易次数
            max_count: 最大交易次数
            limit: 限制返回记录数
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE trade_count BETWEEN %s AND %s ORDER BY trade_count DESC LIMIT %s"
        return execute_query(sql, (min_count, max_count, limit))
    
    @staticmethod
    def get_strategies_by_winning_percentage(min_percentage: float, limit: int = 100) -> List[Dict[str, Any]]:
        """
        根据胜率获取策略
        Args:
            min_percentage: 最小胜率
            limit: 限制返回记录数
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} WHERE winning_percentage >= %s ORDER BY winning_percentage DESC LIMIT %s"
        return execute_query(sql, (min_percentage, limit))
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        获取所有 Strategy 记录
        Args:
            limit: 限制返回记录数
            offset: 偏移量
        Returns:
            Strategy 记录列表
        """
        sql = f"SELECT * FROM {StrategyDAO.TABLE_NAME} ORDER BY gmt_create DESC LIMIT %s OFFSET %s"
        return execute_query(sql, (limit, offset))
    
    @staticmethod
    def update(strategy_id: int, data: Dict[str, Any]) -> bool:
        """
        更新 Strategy 记录
        Args:
            strategy_id: 策略 ID
            data: 要更新的数据字典
        Returns:
            更新是否成功
        """
        fields = [
            'name', 'currency', 'time_interval', 'sharpe_ratio', 'trade_count', 
            'trades', 'total_commission', 'max_drawdown', 'winning_percentage',
            'reason', 'init_balance', 'final_balance', 'extra'
        ]
        
        # 过滤有效字段
        valid_data = {k: v for k, v in data.items() if k in fields and v is not None}
        
        if not valid_data:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        set_clause = ', '.join([f"{k} = %s" for k in valid_data.keys()])
        sql = f"UPDATE {StrategyDAO.TABLE_NAME} SET {set_clause} WHERE id = %s"
        
        params = list(valid_data.values()) + [strategy_id]
        affected_rows = execute_update(sql, tuple(params))
        return affected_rows > 0
    
    @staticmethod
    def delete(strategy_id: int) -> bool:
        """
        删除 Strategy 记录
        Args:
            strategy_id: 策略 ID
        Returns:
            删除是否成功
        """
        sql = f"DELETE FROM {StrategyDAO.TABLE_NAME} WHERE id = %s"
        affected_rows = execute_update(sql, (strategy_id,))
        return affected_rows > 0
    
    @staticmethod
    def batch_create(data_list: List[Dict[str, Any]]) -> int:
        """
        批量创建 Strategy 记录
        Args:
            data_list: Strategy 数据列表
        Returns:
            成功插入的记录数
        """
        if not data_list:
            return 0
        
        fields = [
            'name', 'currency', 'time_interval', 'sharpe_ratio', 'trade_count', 
            'trades', 'total_commission', 'max_drawdown', 'winning_percentage',
            'reason', 'init_balance', 'final_balance', 'extra'
        ]
        
        # 获取第一个记录的所有字段
        first_record = data_list[0]
        valid_fields = [field for field in fields if field in first_record]
        
        if not valid_fields:
            raise ValueError("至少需要提供一个有效字段")
        
        # 构建 SQL
        field_names = ', '.join(valid_fields)
        placeholders = ', '.join(['%s'] * len(valid_fields))
        sql = f"INSERT INTO {StrategyDAO.TABLE_NAME} ({field_names}) VALUES ({placeholders})"
        
        # 准备数据
        params_list = []
        for data in data_list:
            params = tuple(data.get(field) for field in valid_fields)
            params_list.append(params)
        
        return execute_many(sql, params_list)
    
    @staticmethod
    def count_by_currency(currency: str) -> int:
        """
        统计指定货币的策略数量
        Args:
            currency: 货币名称
        Returns:
            策略数量
        """
        sql = f"SELECT COUNT(*) as count FROM {StrategyDAO.TABLE_NAME} WHERE currency = %s"
        result = execute_query(sql, (currency,))
        return result[0]['count'] if result else 0
    
    @staticmethod
    def get_statistics() -> Dict[str, Any]:
        """
        获取策略统计信息
        Returns:
            统计信息字典
        """
        stats = {}
        
        # 总策略数
        total_sql = f"SELECT COUNT(*) as count FROM {StrategyDAO.TABLE_NAME}"
        total_result = execute_query(total_sql)
        stats['total_strategies'] = total_result[0]['count'] if total_result else 0
        
        # 平均夏普比率
        sharpe_sql = f"SELECT AVG(sharpe_ratio) as avg_sharpe FROM {StrategyDAO.TABLE_NAME} WHERE sharpe_ratio IS NOT NULL"
        sharpe_result = execute_query(sharpe_sql)
        stats['avg_sharpe_ratio'] = float(sharpe_result[0]['avg_sharpe']) if sharpe_result and sharpe_result[0]['avg_sharpe'] else 0.0
        
        # 平均胜率
        win_sql = f"SELECT AVG(winning_percentage) as avg_winning FROM {StrategyDAO.TABLE_NAME} WHERE winning_percentage IS NOT NULL"
        win_result = execute_query(win_sql)
        stats['avg_winning_percentage'] = float(win_result[0]['avg_winning']) if win_result and win_result[0]['avg_winning'] else 0.0
        
        # 平均交易次数
        trade_sql = f"SELECT AVG(trade_count) as avg_trades FROM {StrategyDAO.TABLE_NAME} WHERE trade_count IS NOT NULL"
        trade_result = execute_query(trade_sql)
        stats['avg_trade_count'] = float(trade_result[0]['avg_trades']) if trade_result and trade_result[0]['avg_trades'] else 0.0
        
        return stats


# 便捷函数
def create_strategy(data: Dict[str, Any]) -> int:
    """创建 Strategy 记录"""
    return StrategyDAO.create(data)


def get_strategy_by_id(strategy_id: int) -> Optional[Dict[str, Any]]:
    """根据 ID 获取 Strategy 记录"""
    return StrategyDAO.get_by_id(strategy_id)


def get_strategy_by_name(name: str) -> Optional[Dict[str, Any]]:
    """根据名称获取 Strategy 记录"""
    return StrategyDAO.get_by_name(name)


def get_strategies_by_currency(currency: str, limit: int = 100) -> List[Dict[str, Any]]:
    """根据货币获取 Strategy 记录"""
    return StrategyDAO.get_by_currency(currency, limit)


def get_strategies_by_currency_time_interval(currency: str, time_interval: str, limit: int = 100) -> List[Dict[str, Any]]:
    """根据货币和时间间隔获取 Strategy 记录"""
    return StrategyDAO.get_by_currency_time_interval(currency, time_interval, limit)


def get_top_strategies_by_sharpe_ratio(limit: int = 10) -> List[Dict[str, Any]]:
    """获取按夏普比率排序的前N个策略"""
    return StrategyDAO.get_top_strategies_by_sharpe_ratio(limit)


def get_top_strategies_by_final_balance(limit: int = 10) -> List[Dict[str, Any]]:
    """获取按最终余额排序的前N个策略"""
    return StrategyDAO.get_top_strategies_by_final_balance(limit)


def update_strategy(strategy_id: int, data: Dict[str, Any]) -> bool:
    """更新 Strategy 记录"""
    return StrategyDAO.update(strategy_id, data)


def delete_strategy(strategy_id: int) -> bool:
    """删除 Strategy 记录"""
    return StrategyDAO.delete(strategy_id)


def batch_create_strategies(data_list: List[Dict[str, Any]]) -> int:
    """批量创建 Strategy 记录"""
    return StrategyDAO.batch_create(data_list)


def get_strategy_statistics() -> Dict[str, Any]:
    """获取策略统计信息"""
    return StrategyDAO.get_statistics()


# 测试代码
if __name__ == "__main__":
    print("🧪 测试 Strategy DAO...")
    
    try:
        # 测试创建
        test_data = {
            'name': '测试策略',
            'currency': 'BTCUSDT',
            'time_interval': '1h',
            'sharpe_ratio': 1.5,
            'trade_count': 100,
            'trades': '{"trades": []}',
            'total_commission': 50.0,
            'max_drawdown': 0.1,
            'winning_percentage': 0.65,
            'reason': '这是一个测试策略',
            'init_balance': 10000.0,
            'final_balance': 12000.0,
            'extra': '{"extra": "data"}'
        }
        
        strategy_id = create_strategy(test_data)
        print(f"✅ 创建 Strategy 记录成功，ID: {strategy_id}")
        
        # 测试查询
        strategy = get_strategy_by_id(strategy_id)
        print(f"✅ 查询 Strategy 记录成功: {strategy['name']} - {strategy['currency']}")
        
        # 测试按名称查询
        strategy_by_name = get_strategy_by_name('测试策略')
        print(f"✅ 按名称查询 Strategy 记录成功: {strategy_by_name['name']}")
        
        # 测试更新
        update_data = {
            'sharpe_ratio': 1.8,
            'winning_percentage': 0.7,
            'final_balance': 12500.0
        }
        success = update_strategy(strategy_id, update_data)
        print(f"✅ 更新 Strategy 记录: {'成功' if success else '失败'}")
        
        # 测试按货币查询
        strategies = get_strategies_by_currency('BTCUSDT', 5)
        print(f"✅ 查询 BTCUSDT 策略数: {len(strategies)}")
        
        # 测试按货币和时间间隔查询
        strategies = get_strategies_by_currency_time_interval('BTCUSDT', '1h', 5)
        print(f"✅ 查询 BTCUSDT 1h 策略数: {len(strategies)}")
        
        # 测试获取统计信息
        stats = get_strategy_statistics()
        print(f"✅ 策略统计信息: 总数={stats['total_strategies']}, 平均夏普比率={stats['avg_sharpe_ratio']:.2f}")
        
        # 测试删除
        success = delete_strategy(strategy_id)
        print(f"✅ 删除 Strategy 记录: {'成功' if success else '失败'}")
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")