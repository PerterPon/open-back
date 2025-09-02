"""
Coze JWT TTS 实现
基于 Coze API 的文本转语音和对话功能
严格使用 coze-python SDK（cozepy）方法，不做回退逻辑。
"""

import json
import random
import logging
import asyncio
from typing import Optional, Dict, Any, List
import math

# 导入项目模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.llm.types import CozeInfo, ELLMType, TTSOptions, TTSResult
from core.mysql.coze_info import get_all_coze_infos

# 严格按 SDK 使用，假设以下符号均存在
from cozepy import Coze, TokenAuth, JWTAuth


class CozeJWTTTS:
    """Coze JWT TTS 类"""
    
    def __init__(self):
        self.tts_name = 'cozeJWT'
        self.logger = self._setup_logger()
        self.base_url = 'https://api.coze.cn'  # Coze 中国区 API 基础 URL
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger('CozeJWTTTS')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _create_coze_client(self, access_token: str):
        """
        使用 Token 创建 SDK 客户端（中国区 base_url）。
        """
        return Coze(auth=TokenAuth(token=access_token), base_url=self.base_url)  # type: ignore

    # ========== 与 TS 实现保持一致的 SDK 封装接口 ==========
    async def get_voice_list(self, coze_info: Optional[CozeInfo] = None) -> Dict[str, Any]:
        selected_coze = coze_info or await self.pick_jwt()
        access_token = self.get_access_token(selected_coze)
        client = self._create_coze_client(access_token)
        return client.audio.voices.list()

    async def list_space(self, coze_info: Optional[CozeInfo] = None) -> Dict[str, Any]:
        selected_coze = coze_info or await self.pick_jwt()
        access_token = self.get_access_token(selected_coze)
        client = self._create_coze_client(access_token)
        return client.workspaces.list()

    async def list_agent(self, coze_info: CozeInfo, space: Dict[str, Any]) -> Dict[str, Any]:
        access_token = self.get_access_token(coze_info)
        client = self._create_coze_client(access_token)
        space_id = space.get('id') if isinstance(space, dict) else getattr(space, 'id', None)
        return client.bots.list(space_id=space_id)

    async def create_agent(self, space_name: str, coze_info: CozeInfo, space: Dict[str, Any]) -> Dict[str, Any]:
        access_token = self.get_access_token(coze_info)
        client = self._create_coze_client(access_token)
        space_id = space.get('id') if isinstance(space, dict) else getattr(space, 'id', None)
        return client.bots.create(space_id=space_id, name=space_name)

    async def publish_agent(self, coze_info: CozeInfo, bot_id: str) -> None:
        access_token = self.get_access_token(coze_info)
        client = self._create_coze_client(access_token)
        client.bots.publish(bot_id=bot_id, connector_ids=['1024'])

    async def update_agent(self, coze_info: CozeInfo, name: str, bot_id: str, model_id: str) -> None:
        access_token = self.get_access_token(coze_info)
        client = self._create_coze_client(access_token)
        client.bots.update(
            bot_id=bot_id,
            plugin_id_list={},
            workflow_id_list={},
            name=name,
            model_info_config={'model_id': model_id}
        )

    async def pick_jwt(self) -> CozeInfo:
        """
        从数据库随机选择一个 Coze 配置信息
        Returns:
            随机选择的 CozeInfo 对象
        """
        self.logger.info('开始获取 Coze 配置信息')
        
        # 获取所有配置信息
        all_coze_infos = get_all_coze_infos()
        
        if not all_coze_infos:
            raise Exception('没有找到可用的 Coze 配置信息')
        
        # 随机选择一个配置
        selected_coze = random.choice(all_coze_infos)
        self.logger.info(f'随机选择 Coze 配置：{selected_coze.name} (ID: {selected_coze.id})')
        
        return selected_coze
    
    def get_access_token(self, coze_info: CozeInfo) -> str:
        """
        获取 Coze API 的访问令牌
        Args:
            coze_info: Coze 配置信息
        Returns:
            访问令牌
        """
        self.logger.info(f'获取 Coze Access Token，AppID: {coze_info.app_id}')
        
        if not all([coze_info.private_key, coze_info.key_id, coze_info.app_id, coze_info.aud]):
            raise Exception('Coze 配置信息不完整')
        
        # 正确方式：使用 SDK 的 JWTAuth（参考 coze-py examples）
        auth = JWTAuth(
            client_id=coze_info.app_id,
            private_key=coze_info.private_key,
            public_key_id=coze_info.key_id,
            ttl=3600,
            base_url=self.base_url,
        )
        token = auth.token
        self.logger.info('获取 access token 成功（JWTAuth）')
        return token
    
    def estimate_duration(self, text: str) -> float:
        """
        根据文本长度估算语音时长（秒）
        Args:
            text: 输入文本
        Returns:
            估算的时长（秒）
        """
        # 假设平均每个汉字或字符发音约为 0.3 秒
        char_count = len(text)
        # 估算时长并添加一点缓冲
        return max(1.0, math.ceil(char_count * 0.3))
    
    def conversation(self, coze_info: CozeInfo, model_name: ELLMType, message: str) -> str:
        """
        与 Coze 机器人进行对话
        Args:
            coze_info: Coze 配置信息
            model_name: 模型名称
            message: 用户消息
        Returns:
            机器人回复
        """
        self.logger.info(f'conversation, model_name: {model_name.value}')

        # 获取访问令牌 -> SDK 调用
        access_token = self.get_access_token(coze_info)

        # 解析 comment 中的配置信息
        comment_data = {}
        try:
            if coze_info.comment:
                comment_data = json.loads(coze_info.comment)
        except json.JSONDecodeError:
            raise Exception(f'coze_info.comment 不是有效的 JSON 字符串：{coze_info.comment}')

        # 获取对应模型的 bot/agent id
        model_config = comment_data.get(model_name.value, {}) if isinstance(comment_data, dict) else {}
        bot_id = model_config.get('agent_id') or model_config.get('bot_id')
        if not bot_id:
            raise Exception(f'未找到模型 {model_name.value} 对应的 bot/agent id')

        # 使用 SDK 发起对话：直接 create_and_poll（与 TS 对齐）
        coze = self._create_coze_client(access_token)
        resp = coze.chat.create_and_poll(
            bot_id=bot_id,
            additional_messages=[{'role': 'user', 'content': message}],
        )
        messages = resp.messages
        return messages[0].content

    def conversation_with_messages(self, coze_info: CozeInfo, model_name: ELLMType, messages: List[Dict[str, str]]) -> str:
        """
        与 Coze 机器人进行多消息对话（与 TS 版 conversationWithMessages 对齐）
        """
        self.logger.info(f'conversation_with_messages, model_name: {model_name.value}, messages: {len(messages)}')

        access_token = self.get_access_token(coze_info)

        # 解析 comment，获取 bot/agent id
        try:
            comment_data = json.loads(coze_info.comment) if coze_info.comment else {}
        except json.JSONDecodeError:
            raise Exception(f'coze_info.comment 不是有效的 JSON 字符串：{coze_info.comment}')

        model_config = comment_data.get(model_name.value, {}) if isinstance(comment_data, dict) else {}
        bot_id = model_config.get('agent_id') or model_config.get('bot_id')
        if not bot_id:
            raise Exception(f'未找到模型 {model_name.value} 对应的 bot/agent id')

        coze = self._create_coze_client(access_token)
        resp = coze.chat.create_and_poll(
            bot_id=bot_id,
            additional_messages=messages,
        )
        if getattr(resp.chat, 'status', None) == 'failed':
            error = Exception(getattr(resp.chat.last_error, 'msg', '') or getattr(resp.chat.last_error, 'message', ''))
            setattr(error, 'originCode', f"{getattr(resp.chat.last_error, 'code', '')}")  # type: ignore
            raise error
        return resp.messages[0].content
    
    async def tts(self, options: TTSOptions, coze_info: Optional[CozeInfo] = None) -> TTSResult:
        """
        文本转语音实现
        Args:
            options: TTS 选项
            coze_info: 可选的 Coze 配置信息
        Returns:
            TTS 结果
        """
        self.logger.info(f'开始 Coze TTS 文本转语音，文本长度：{len(options.text)}')
        
        last_error = None
        
        # 循环尝试不同的 Coze 配置，直到成功或全部失败
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 随机选择一个 Coze 配置
                selected_coze = coze_info or await self.pick_jwt()
                
                if not selected_coze or not selected_coze.id:
                    raise Exception('无法获取有效的 Coze 配置信息')
                
                self.logger.info(f'使用 Coze 配置 ID: {selected_coze.id}, 名称：{selected_coze.name}')
                
                # 获取 access token（同步方法，移除误用的 await）
                access_token = self.get_access_token(selected_coze)
                self.logger.info('获取 access token 成功')

                coze = self._create_coze_client(access_token)
                sdk_resp = coze.audio.speech.create(
                    input=options.text,
                    voice_id=options.voice,
                    speed=options.speed,
                    sample_rate=48000,
                    response_format='mp3',
                )
                audio_data = sdk_resp if isinstance(sdk_resp, (bytes, bytearray)) else sdk_resp.data
                
                self.logger.info(f'TTS 成功，获取音频大小：{len(audio_data)} 字节')
                
                return TTSResult(
                    data=audio_data,
                    duration=self.estimate_duration(options.text)
                )
                
            except Exception as error:
                last_error = error
                self.logger.error(f'TTS 调用失败（尝试 {attempt + 1}/{max_retries}）：{str(error)}')
                
                # 如果是配额限制错误，继续尝试下一个配置
                error_message = str(error).lower()
                if any(keyword in error_message for keyword in ['quota', 'limit', 'exceeded']):
                    if attempt < max_retries - 1:
                        continue
                
                # 非配额错误或达到最大重试次数，抛出异常
                if attempt == max_retries - 1:
                    raise error
        
        # 如果所有尝试都失败，抛出最后一个错误
        if last_error:
            raise last_error
