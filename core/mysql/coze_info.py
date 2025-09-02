"""
Coze Info 表的数据访问层
实现基础的 CRUD 操作
"""

import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.mysql.index_tts import get_cursor, execute_query, execute_update, execute_many
from core.llm.types import CozeInfo


class CozeInfoDAO:
    """Coze Info 数据访问对象"""
    
    TABLE_NAME = "coze-info"
    
    @staticmethod
    def _assembly_coze_info(item: Dict[str, Any]) -> CozeInfo:
        """
        将数据库记录转换为 CozeInfo 对象
        Args:
            item: 数据库记录
        Returns:
            CozeInfo 对象
        """
        return CozeInfo(
            id=item.get('id'),
            name=item.get('name'),
            phone=item.get('phone'),
            app_id=item.get('app_id'),
            aud=item.get('aud'),
            private_key=item.get('private_key'),
            key_id=item.get('key_id'),
            region=item.get('region'),
            gmt_create=item.get('gmt_create'),
            gmt_modify=item.get('gmt_modify'),
            comment=item.get('comment')
        )
    
    @staticmethod
    def get_by_query(query: Dict[str, Any]) -> List[CozeInfo]:
        """
        根据查询条件获取 Coze Info 记录
        Args:
            query: 查询条件字典
        Returns:
            CozeInfo 记录列表
        """
        logger = logging.getLogger('CozeInfoDAO')
        logger.info(f"get_by_query, query: {json.dumps(query)}")
        
        # 构建 WHERE 条件
        where_conditions = []
        params = []
        
        for key, value in query.items():
            where_conditions.append(f"`{key}` = %s")
            params.append(value)
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1 = 1"
        sql = f"SELECT * FROM `{CozeInfoDAO.TABLE_NAME}` WHERE {where_clause}"
        
        results = execute_query(sql, tuple(params))
        
        coze_infos = []
        for item in results:
            coze_infos.append(CozeInfoDAO._assembly_coze_info(item))
        
        return coze_infos
    
    @staticmethod
    def get_all() -> List[CozeInfo]:
        """
        获取所有 Coze Info 记录
        Returns:
            所有 CozeInfo 记录列表
        """
        logger = logging.getLogger('CozeInfoDAO')
        logger.info("get_all_coze_infos")
        
        return CozeInfoDAO.get_by_query({})
    
    @staticmethod
    def get_by_id(coze_id: int) -> Optional[CozeInfo]:
        """
        根据 ID 获取 Coze Info 记录
        Args:
            coze_id: Coze Info 记录 ID
        Returns:
            CozeInfo 记录，如果不存在则返回 None
        """
        logger = logging.getLogger('CozeInfoDAO')
        logger.info(f"get_by_id, id: {coze_id}")
        
        results = CozeInfoDAO.get_by_query({'id': coze_id})
        return results[0] if results else None
    
    @staticmethod
    def add_coze_info(coze_info: CozeInfo) -> int:
        """
        添加 Coze Info 记录
        Args:
            coze_info: CozeInfo 对象
        Returns:
            新创建记录的 ID
        """
        logger = logging.getLogger('CozeInfoDAO')
        logger.info("add_coze_info")
        
        sql = f"""
        INSERT INTO `{CozeInfoDAO.TABLE_NAME}` 
        (name, phone, app_id, aud, private_key, key_id, region, comment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        with get_cursor() as cursor:
            cursor.execute(sql, (
                coze_info.name,
                coze_info.phone,
                coze_info.app_id,
                coze_info.aud,
                coze_info.private_key,
                coze_info.key_id,
                coze_info.region,
                coze_info.comment
            ))
            return cursor.lastrowid
    
    @staticmethod
    def update_by_query(params: Dict[str, Any], query: Dict[str, Any]) -> None:
        """
        根据查询条件更新 Coze Info 记录
        Args:
            params: 要更新的参数
            query: 查询条件
        """
        logger = logging.getLogger('CozeInfoDAO')
        logger.info(f"update_by_query, params: {json.dumps(params)}, query: {json.dumps(query)}")
        
        # 构建 SET 子句
        set_conditions = []
        set_params = []
        for key, value in params.items():
            set_conditions.append(f"`{key}` = %s")
            set_params.append(value)
        
        # 构建 WHERE 条件
        where_conditions = []
        where_params = []
        for key, value in query.items():
            where_conditions.append(f"`{key}` = %s")
            where_params.append(value)
        
        set_clause = ", ".join(set_conditions)
        where_clause = " AND ".join(where_conditions) if where_conditions else "1 = 1"
        
        sql = f"""
        UPDATE `{CozeInfoDAO.TABLE_NAME}` 
        SET {set_clause} 
        WHERE {where_clause}
        """
        
        all_params = set_params + where_params
        execute_update(sql, tuple(all_params))
    
    @staticmethod
    def delete_by_id(coze_id: int) -> None:
        """
        根据 ID 删除 Coze Info 记录
        Args:
            coze_id: Coze Info 记录 ID
        """
        logger = logging.getLogger('CozeInfoDAO')
        logger.info(f"delete_by_id, id: {coze_id}")
        
        sql = f"DELETE FROM `{CozeInfoDAO.TABLE_NAME}` WHERE id = %s"
        execute_update(sql, (coze_id,))


# 便捷函数
def get_all_coze_infos() -> List[CozeInfo]:
    """获取所有 Coze Info 记录"""
    return CozeInfoDAO.get_all()


def get_coze_info_by_id(coze_id: int) -> Optional[CozeInfo]:
    """根据 ID 获取 Coze Info 记录"""
    return CozeInfoDAO.get_by_id(coze_id)


def add_coze_info(coze_info: CozeInfo) -> int:
    """添加 Coze Info 记录"""
    return CozeInfoDAO.add_coze_info(coze_info)


def update_coze_info_by_query(params: Dict[str, Any], query: Dict[str, Any]) -> None:
    """根据查询条件更新 Coze Info 记录"""
    return CozeInfoDAO.update_by_query(params, query)


def delete_coze_info_by_id(coze_id: int) -> None:
    """根据 ID 删除 Coze Info 记录"""
    return CozeInfoDAO.delete_by_id(coze_id)


# 测试代码
if __name__ == "__main__":
    print("🧪 测试 Coze Info DAO...")
    
    try:
        # 测试获取所有记录
        all_coze_infos = get_all_coze_infos()
        print(f"✅ 获取所有 Coze Info 记录成功，数量：{len(all_coze_infos)}")
        
        if all_coze_infos:
            # 测试根据 ID 查询
            first_coze = all_coze_infos[0]
            coze_by_id = get_coze_info_by_id(first_coze.id)
            print(f"✅ 根据 ID 查询成功：{coze_by_id.name if coze_by_id else 'None'}")
        
        print("🎉 所有测试通过！")
        
    except Exception as e:
        print(f"❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
