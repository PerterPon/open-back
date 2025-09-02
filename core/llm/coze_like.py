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
from core.llm.types import ELLMType, CozeInfo
from core.llm.coze_jwt import CozeJWTTTS
from core.mysql.coze_info import get_all_coze_infos
import requests
try:
    from cozepy import Coze, TokenAuth, Message, ChatStatus
except Exception:  # pragma: no cover
    Coze = None  # type: ignore
    TokenAuth = None  # type: ignore
    Message = None  # type: ignore
    ChatStatus = None  # type: ignore


class LLMCozeLike(BaseLLM):
    """
    Coze Like LLM 实现类
    继承自 BaseLLM，实现基于 Coze API 的大语言模型功能
    """
    
    def __init__(self, sub_name: ELLMType):
        # 先设置子类所需字段，确保基类初始化时可用
        self.name = 'cozeLike'
        self.sub_name = sub_name
        self.coze_jwt_tts: Optional[CozeJWTTTS] = None
        # 再调用基类构造，基类会调用 _setup_logger，且可安全使用 sub_name
        super().__init__()
    
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
        if Coze is None or TokenAuth is None:
            raise Exception('cozepy 未安装或导入失败，请先安装 cozepy 库')
        
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
            
            # 解析 comment 中的模型配置，找到 agent/bot id
            import json as _json
            model_config = {}
            try:
                if selected_coze.comment:
                    all_cfg = _json.loads(selected_coze.comment)
                    model_config = all_cfg.get(self.sub_name.value, {}) if isinstance(all_cfg, dict) else {}
            except Exception:
                model_config = {}
            bot_id = model_config.get('agent_id') or model_config.get('bot_id')
            if not bot_id:
                raise Exception(f'未找到模型 {self.sub_name.value} 对应的 bot/agent id')

            # 获取 access token，并用 SDK 的 create_and_poll 发起对话（与官方示例对齐）
            access_token = self.coze_jwt_tts.get_access_token(selected_coze)
            coze = Coze(auth=TokenAuth(token=access_token), base_url=self.coze_jwt_tts.base_url)  # type: ignore
            self.logger.info(f'使用 SDK 发起对话，bot_id: {bot_id}, prompt: {content}')
            resp = coze.chat.create_and_poll(
                user_id='user_id',
                bot_id=bot_id,
                additional_messages=[Message.build_user_question_text(content)],
            )
            msg = resp.messages[0].content if getattr(resp, 'messages', None) else ''

            if not msg:
                raise Exception('cozepy 返回空内容')

            self.logger.info(f'对话完成，回复长度：{len(msg)}')
            return msg
            
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
        
        # 使用 SDK 封装的接口，与 TS 对齐
        return await self.coze_jwt_tts.get_voice_list(selected_coze)
    
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
        
        # 使用 SDK 封装的接口
        return await self.coze_jwt_tts.list_space(selected_coze)
    
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
        
        access_token = self.coze_jwt_tts.get_access_token(coze_info)
        
        # 使用 SDK 封装的接口
        return await self.coze_jwt_tts.list_agent(coze_info, {'id': space_id})
    
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
        
        access_token = self.coze_jwt_tts.get_access_token(coze_info)
        
        # 使用 SDK 封装的接口
        return await self.coze_jwt_tts.create_agent(bot_name, coze_info, {'id': space_id})
    
    async def publish_bot(self, coze_info: CozeInfo, bot_id: str) -> None:
        """
        发布机器人
        Args:
            coze_info: Coze 配置信息
            bot_id: 机器人 ID
        """
        if not self.coze_jwt_tts:
            raise Exception('CozeJWTTTS 未初始化')
        
        access_token = self.coze_jwt_tts.get_access_token(coze_info)
        
        # 使用 SDK 封装的接口
        await self.coze_jwt_tts.publish_agent(coze_info, bot_id)
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
