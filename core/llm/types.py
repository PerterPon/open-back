"""
LLM 相关的类型定义和枚举
"""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime


class ELLMType(Enum):
    """LLM 类型枚举"""
    DEEPSEEK = 'deepseek'
    DEEPSEEK0528 = 'deepseek0528'
    VOLCEENGINE_DEEPSEEK_NETWORK = 'volcengineDeepSeekNetwork'
    DOUBAO_THINKING = 'doubao15Thinking'
    DOUBAO_16_THINKING = 'doubao16Thinking'
    OPENAI = 'openai'
    DOUBAO = 'doubao15pro'


@dataclass
class CozeInfo:
    """Coze 配置信息"""
    id: Optional[int] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    app_id: Optional[str] = None
    aud: Optional[str] = None
    private_key: Optional[str] = None
    key_id: Optional[str] = None
    region: Optional[str] = None
    gmt_create: Optional[datetime] = None
    gmt_modify: Optional[datetime] = None
    comment: Optional[str] = None

    @property
    def app_id_property(self) -> Optional[str]:
        """兼容原始的appId属性名"""
        return self.app_id

    @property
    def private_key_property(self) -> Optional[str]:
        """兼容原始的privateKey属性名"""
        return self.private_key

    @property
    def key_id_property(self) -> Optional[str]:
        """兼容原始的keyId属性名"""
        return self.key_id


@dataclass
class LLMMessage:
    """LLM 消息"""
    role: str  # 'user' | 'system' | 'assistant'
    content: str


@dataclass
class TTSOptions:
    """TTS 选项"""
    text: str
    speed: float = 1.0
    voice: str = ""


@dataclass
class TTSResult:
    """TTS 结果"""
    data: bytes
    duration: float


class CozeAPIVoiceName(Enum):
    """Coze API 语音名称"""
    WANWANXIAOHE = '7426720361753968677'
    WENNUANAHU = '7426720361753952293'
    QINQIENVSHENG = '7481299960424775734'
