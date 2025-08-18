"""
Coze Like LLM 实现
基于 Coze API 的大语言模型接口实现
"""

import random
import logging
from typing import Optional, Dict, Any

# 导入项目模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.llm.base import BaseLLM
from core.llm.types import ELLMType
from core.llm.coze_jwt import CozeJWTTTS
from core.mysql.coze_info import get_all_coze_infos


class LLMCozeLike(BaseLLM):
    """
    Coze Like LLM 实现类
    继承自 BaseLLM，实现基于 Coze API 的大语言模型功能
    """
    
    def __init__(self, sub_name: ELLMType):
        super().__init__()
        self.name = 'cozeLike'
        self.sub_name = sub_name
        self.coze_jwt_tts: Optional[CozeJWTTTS] = None
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置专用的日志记录器"""
        logger = logging.getLogger(f'LLMCozeLike.{self.sub_name.value}')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def init(self) -> None:
        """
        初始化 LLM 实例
        """
        self.logger.info(f'初始化 LLMCozeLike，子类型：{self.sub_name.value}')
        await super().init()
        
        # 初始化 CozeJWTTTS
        self.coze_jwt_tts = CozeJWTTTS()
        
        self.logger.info('LLMCozeLike 初始化完成')
    
    async def completions(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        文本补全接口
        Args:
            content: 输入文本内容
            options: 可选参数
        Returns:
            生成的文本回复
        """
        self.logger.info(f'completions [{self.sub_name.value}], content length: [{len(content)}]')
        
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化，请先调用 init() 方法')
        
        try:
            # 获取所有可用的 Coze 配置信息
            all_coze_infos = get_all_coze_infos()
            
            # 过滤出有效的配置（comment 不为空）
            valid_coze_infos = []
            for coze_info in all_coze_infos:
                if coze_info.comment is not None and coze_info.comment.strip():
                    valid_coze_infos.append(coze_info)
            
            if not valid_coze_infos:
                raise Exception('没有找到有效的 Coze 配置信息（comment 为空）')
            
            # 随机选择一个有效配置
            selected_coze = random.choice(valid_coze_infos)
            self.logger.info(f'选择 Coze 配置：{selected_coze.name} (ID: {selected_coze.id})')
            
            # 调用对话接口
            result = self.coze_jwt_tts.conversation(selected_coze, self.sub_name, content)
            
            self.logger.info(f'对话完成，回复长度：{len(result)}')
            return result
            
        except Exception as e:
            self.logger.error(f'completions 调用失败：{str(e)}')
            raise e
    
    async def completions_stream(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        流式文本补全接口
        Args:
            content: 输入文本内容
            options: 可选参数
        Returns:
            生成的文本回复
        """
        self.logger.info(f'completions_stream [{self.sub_name.value}], content length: [{len(content)}]')
        
        # 目前直接调用普通补全接口
        # 如果需要真正的流式实现，可以在这里扩展
        return await self.completions(content, options)
    
    async def get_voice_list(self, coze_info: Optional[CozeInfo] = None) -> Dict[str, Any]:
        """
        获取可用的语音列表
        Args:
            coze_info: 可选的 Coze 配置信息
        Returns:
            语音列表数据
        """
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化')
        
        selected_coze = coze_info or await self.coze_jwt_tts.pick_jwt()
        access_token = self.coze_jwt_tts.get_access_token(selected_coze)
        
        # 调用 Coze API 获取语音列表
        voices_url = f"{self.coze_jwt_tts.base_url}/v1/audio/voices"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(voices_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    async def list_workspaces(self, coze_info: Optional[CozeInfo] = None) -> Dict[str, Any]:
        """
        获取工作空间列表
        Args:
            coze_info: 可选的 Coze 配置信息
        Returns:
            工作空间列表数据
        """
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化')
        
        selected_coze = coze_info or await self.coze_jwt_tts.pick_jwt()
        access_token = self.coze_jwt_tts.get_access_token(selected_coze)
        
        # 调用 Coze API 获取工作空间列表
        workspaces_url = f"{self.coze_jwt_tts.base_url}/v1/workspaces"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(workspaces_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    async def list_bots(self, coze_info: CozeInfo, space_id: str) -> Dict[str, Any]:
        """
        获取指定工作空间的机器人列表
        Args:
            coze_info: Coze 配置信息
            space_id: 工作空间 ID
        Returns:
            机器人列表数据
        """
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化')
        
        access_token = await self.coze_jwt_tts.get_access_token(coze_info)
        
        # 调用 Coze API 获取机器人列表
        bots_url = f"{self.coze_jwt_tts.base_url}/v1/bots"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        params = {'space_id': space_id}
        
        response = requests.get(bots_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    async def create_bot(self, coze_info: CozeInfo, space_id: str, bot_name: str) -> Dict[str, Any]:
        """
        创建新的机器人
        Args:
            coze_info: Coze 配置信息
            space_id: 工作空间 ID
            bot_name: 机器人名称
        Returns:
            创建结果数据
        """
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化')
        
        access_token = await self.coze_jwt_tts.get_access_token(coze_info)
        
        # 调用 Coze API 创建机器人
        create_url = f"{self.coze_jwt_tts.base_url}/v1/bots"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        create_data = {
            'space_id': space_id,
            'name': bot_name
        }
        
        response = requests.post(create_url, headers=headers, json=create_data, timeout=30)
        response.raise_for_status()
        
        return response.json()
    
    async def publish_bot(self, coze_info: CozeInfo, bot_id: str) -> None:
        """
        发布机器人
        Args:
            coze_info: Coze 配置信息
            bot_id: 机器人 ID
        """
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化')
        
        access_token = await self.coze_jwt_tts.get_access_token(coze_info)
        
        # 调用 Coze API 发布机器人
        publish_url = f"{self.coze_jwt_tts.base_url}/v1/bots/{bot_id}/publish"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        publish_data = {
            'connector_ids': ['1024']  # 默认连接器 ID
        }
        
        response = requests.post(publish_url, headers=headers, json=publish_data, timeout=30)
        response.raise_for_status()
        
        self.logger.info(f'机器人 {bot_id} 发布成功')


# 便捷函数
async def create_coze_like_llm(sub_name: ELLMType) -> LLMCozeLike:
    """
    创建并初始化 LLMCozeLike 实例
    Args:
        sub_name: LLM 子类型
    Returns:
        初始化完成的 LLMCozeLike 实例
    """
    llm = LLMCozeLike(sub_name)
    await llm.init()
    return llm


# 测试代码
if __name__ == "__main__":
    import asyncio
    
    async def test_llm_coze_like():
        """测试 LLMCozeLike 功能"""
        print("🧪 测试 LLMCozeLike...")
        
        try:
            # 创建 LLM 实例
            llm = await create_coze_like_llm(ELLMType.DOUBAO_THINKING)
            print("✅ LLMCozeLike 创建成功")
            
            # 测试文本补全
            test_content = "你好，请介绍一下你自己。"
            result = await llm.completions(test_content)
            print(f"✅ 文本补全成功，回复长度：{len(result)}")
            print(f"回复内容：{result[:100]}...")
            
            print("🎉 所有测试通过！")
            
        except Exception as e:
            print(f"❌ 测试失败：{e}")
            import traceback
            traceback.print_exc()
    
    # 运行测试
    asyncio.run(test_llm_coze_like())
