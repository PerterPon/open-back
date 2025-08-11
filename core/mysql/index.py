# 这个文件的作用是连接 mysql 数据库，实现一个底层的连接数据库功能，有一个连接池，支持多个链接并发，暴露一个 getConnection 方法，返回一个连接对象，调用的时候判断一下，如果当前未连接过，则连接，如果连接过，则直接返回。
# 每一张表就是一个单独的文件，每个文件实现对于这张表的基础 CURD 能力，需要连接数据库的时候就会调用这个方法来获取具体的数据库连接。
# 这个文件应该是一个单例，每个进程唯一，这样可以保证连接池的唯一性，避免重复连接。

import pymysql
import threading
from typing import Optional, Dict, Any
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import logging

# 导入配置管理器
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.config.index import get_config


class MySQLConnectionPool:
    """MySQL 连接池管理器，单例模式"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._pool = None
            self._config = None
            self._logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('MySQLConnectionPool')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _get_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        if self._config is None:
            config = get_config()
            mysql_config = config.get('mysql', {})
            
            if not mysql_config:
                raise ValueError("MySQL 配置未找到")
            
            self._config = {
                'host': mysql_config.get('host'),
                'port': mysql_config.get('port'),
                'user': mysql_config.get('username'),
                'password': mysql_config.get('password'),
                'database': mysql_config.get('database'),
                'charset': 'utf8mb4',
                'cursorclass': DictCursor,
                'autocommit': True,
                'max_allowed_packet': 16777216,  # 16MB
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30
            }
        
        return self._config
    
    def _create_connection(self):
        """创建数据库连接"""
        config = self._get_config()
        try:
            connection = pymysql.connect(**config)
            self._logger.info(f"成功连接到 MySQL 数据库：{config['host']}:{config['port']}/{config['database']}")
            return connection
        except Exception as e:
            self._logger.error(f"连接 MySQL 数据库失败：{e}")
            raise
    
    def get_connection(self):
        """
        获取数据库连接
        如果当前未连接过，则连接；如果连接过，则直接返回
        """
        if self._pool is None:
            with self._lock:
                if self._pool is None:
                    self._pool = self._create_connection()
        
        # 检查连接是否有效
        try:
            self._pool.ping(reconnect=True)
        except Exception as e:
            self._logger.warning(f"数据库连接已断开，正在重新连接：{e}")
            self._pool = self._create_connection()
        
        return self._pool
    
    def close_connection(self):
        """关闭数据库连接"""
        if self._pool:
            try:
                self._pool.close()
                self._logger.info("数据库连接已关闭")
            except Exception as e:
                self._logger.error(f"关闭数据库连接时出错：{e}")
            finally:
                self._pool = None
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            yield cursor
        except Exception as e:
            self._logger.error(f"数据库操作失败：{e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, sql: str, params: tuple = None) -> list:
        """执行查询语句"""
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    
    def execute_update(self, sql: str, params: tuple = None) -> int:
        """执行更新语句"""
        with self.get_cursor() as cursor:
            affected_rows = cursor.execute(sql, params)
            return affected_rows
    
    def execute_many(self, sql: str, params_list: list) -> int:
        """批量执行语句"""
        with self.get_cursor() as cursor:
            affected_rows = cursor.executemany(sql, params_list)
            return affected_rows


# 创建全局连接池实例
_mysql_pool = MySQLConnectionPool()


def get_connection():
    """
    获取数据库连接的便捷函数
    返回一个数据库连接对象
    """
    return _mysql_pool.get_connection()


def get_cursor():
    """
    获取数据库游标的便捷函数
    返回一个上下文管理器，用于安全地执行数据库操作
    """
    return _mysql_pool.get_cursor()


def execute_query(sql: str, params: tuple = None) -> list:
    """
    执行查询语句的便捷函数
    """
    return _mysql_pool.execute_query(sql, params)


def execute_update(sql: str, params: tuple = None) -> int:
    """
    执行更新语句的便捷函数
    """
    return _mysql_pool.execute_update(sql, params)


def execute_many(sql: str, params_list: list) -> int:
    """
    批量执行语句的便捷函数
    """
    return _mysql_pool.execute_many(sql, params_list)


def close_connection():
    """
    关闭数据库连接的便捷函数
    """
    _mysql_pool.close_connection()


# 示例用法
if __name__ == "__main__":
    try:
        # 测试连接
        connection = get_connection()
        print("✅ 数据库连接成功！")
        
        # 测试查询
        with get_cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"✅ MySQL 版本：{result['version']}")
        
        # 测试查询表结构
        tables = execute_query("SHOW TABLES")
        print(f"✅ 数据库中的表：{[list(table.values())[0] for table in tables]}")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    finally:
        close_connection()