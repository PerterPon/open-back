import pymysql
import threading
from typing import Optional, Dict, Any
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import logging
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.config.index import get_config


class MySQLConnectionPoolMain:
    """MySQL 连接池管理器（main 数据库），单例模式"""
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
        logger = logging.getLogger('MySQLConnectionPoolMain')
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def _get_config(self) -> Dict[str, Any]:
        if self._config is None:
            config = get_config()
            mysql_config = (config.get('mysql') or {}).get('main') or {}
            if not mysql_config:
                raise ValueError("MySQL main 配置未找到")
            self._config = {
                'host': mysql_config.get('host'),
                'port': mysql_config.get('port'),
                'user': mysql_config.get('username'),
                'password': mysql_config.get('password'),
                'database': mysql_config.get('database'),
                'charset': 'utf8mb4',
                'cursorclass': DictCursor,
                'autocommit': True,
                'max_allowed_packet': 16777216,
                'connect_timeout': 10,
                'read_timeout': 30,
                'write_timeout': 30,
            }
        return self._config

    def _create_connection(self):
        cfg = self._get_config()
        try:
            conn = pymysql.connect(**cfg)
            self._logger.info(f"成功连接到 MySQL(main)：{cfg['host']}:{cfg['port']}/{cfg['database']}")
            return conn
        except Exception as e:
            self._logger.error(f"连接 MySQL(main) 失败：{e}")
            raise

    def get_connection(self):
        if self._pool is None:
            with self._lock:
                if self._pool is None:
                    self._pool = self._create_connection()
        try:
            self._pool.ping(reconnect=True)
        except Exception as e:
            self._logger.warning(f"MySQL(main) 连接断开，重连：{e}")
            self._pool = self._create_connection()
        return self._pool

    def close_connection(self):
        if self._pool:
            try:
                self._pool.close()
                self._logger.info("MySQL(main) 连接已关闭")
            except Exception as e:
                self._logger.error(f"关闭 MySQL(main) 连接出错：{e}")
            finally:
                self._pool = None

    @contextmanager
    def get_cursor(self):
        connection = self.get_connection()
        cursor = None
        try:
            cursor = connection.cursor()
            yield cursor
        except Exception as e:
            self._logger.error(f"MySQL(main) 操作失败：{e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()

    def execute_query(self, sql: str, params: tuple = None) -> list:
        with self.get_cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()

    def execute_update(self, sql: str, params: tuple = None) -> int:
        with self.get_cursor() as cursor:
            return cursor.execute(sql, params)

    def execute_many(self, sql: str, params_list: list) -> int:
        with self.get_cursor() as cursor:
            return cursor.executemany(sql, params_list)


_pool_main = MySQLConnectionPoolMain()


def get_connection():
    return _pool_main.get_connection()


def get_cursor():
    return _pool_main.get_cursor()


def execute_query(sql: str, params: tuple = None) -> list:
    return _pool_main.execute_query(sql, params)


def execute_update(sql: str, params: tuple = None) -> int:
    return _pool_main.execute_update(sql, params)


def execute_many(sql: str, params_list: list) -> int:
    return _pool_main.execute_many(sql, params_list)


def close_connection():
    _pool_main.close_connection()


