"""
Coze JWT TTS 实现
基于 Coze API 的文本转语音和对话功能
"""

import json
import random
import logging
import requests
import asyncio
from typing import Optional, Dict, Any, List
import math

# 导入项目模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.llm.types import CozeInfo, ELLMType, TTSOptions, TTSResult
from core.mysql.coze_info import get_all_coze_infos


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
        
        try:
            # 这里需要实现 JWT token 获取逻辑
            # 由于 Python 没有直接对应的 @coze/api 库，我们需要手动实现 JWT 签名
            import jwt
            import time
            
            # 构建 JWT payload
            now = int(time.time())
            payload = {
                'iss': coze_info.app_id,
                'aud': coze_info.aud,
                'iat': now,
                'exp': now + 3600,  # 1小时后过期
                'jti': f"{coze_info.app_id}_{now}"
            }
            
            # 使用私钥签名 JWT
            token = jwt.encode(
                payload,
                coze_info.private_key,
                algorithm='RS256',
                headers={'kid': coze_info.key_id}
            )
            
            # 调用 Coze API 获取 access token
            auth_url = f"{self.base_url}/api/permission/oauth2/token"
            auth_data = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': token
            }
            
            response = requests.post(auth_url, json=auth_data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            access_token = result.get('access_token')
            
            if not access_token:
                raise Exception(f'获取 access token 失败：{result}')
            
            self.logger.info('获取 access token 成功')
            return access_token
            
        except Exception as error:
            self.logger.error(f'获取 Access Token 失败：{str(error)}')
            raise error
    
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
        
        # 获取访问令牌
        access_token = self.get_access_token(coze_info)
        
        # 解析 comment 中的配置信息
        comment_data = {}
        try:
            if coze_info.comment:
                comment_data = json.loads(coze_info.comment)
        except json.JSONDecodeError as error:
            raise Exception(f'coze_info.comment 不是有效的 JSON 字符串：{coze_info.comment}')
        
        # 获取对应模型的 bot_id
        model_config = comment_data.get(model_name.value, {})
        bot_id = model_config.get('agent_id')
        
        if not bot_id:
            raise Exception(f'未找到模型 {model_name.value} 对应的 bot_id')
        
        # 调用 Coze 对话 API
        chat_url = f"{self.base_url}/v3/chat"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        chat_data = {
            'bot_id': bot_id,
            'user_id': 'user_001',  # 可以根据需要自定义
            'additional_messages': [
                {
                    'role': 'user',
                    'content': message
                }
            ],
            'stream': False
        }
        
        try:
            response = requests.post(chat_url, headers=headers, json=chat_data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # 解析响应获取机器人回复
            messages = result.get('messages', [])
            if messages:
                # 获取最后一条助手消息
                for msg in reversed(messages):
                    if msg.get('role') == 'assistant':
                        return msg.get('content', '')
            
            raise Exception('未获取到有效的机器人回复')
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Coze API 请求失败：{e}')
            raise Exception(f'Coze API 请求失败：{e}')
    
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
                
                # 获取 access token
                access_token = await self.get_access_token(selected_coze)
                self.logger.info('获取 access token 成功')
                
                # 调用 TTS API
                tts_url = f"{self.base_url}/v1/audio/speech"
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                tts_data = {
                    'input': options.text,
                    'voice_id': options.voice,
                    'speed': options.speed,
                    'sample_rate': 48000,
                    'response_format': 'mp3'
                }
                
                response = requests.post(tts_url, headers=headers, json=tts_data, timeout=60)
                response.raise_for_status()
                
                # 处理音频数据
                audio_data = response.content
                
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
