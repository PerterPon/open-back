"""
基础 LLM 类
"""

import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

# 导入配置管理器
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from core.config.index import get_config


class BaseLLM(ABC):
    """基础 LLM 抽象类"""
    
    def __init__(self):
        self.name: str = 'baseLLM'
        self.llm_config: Dict[str, Any] = {}
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f'LLM.{self.name}')
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
        """初始化 LLM 配置"""
        config = get_config()
        llm_configs = config.get('llm', {})
        self.llm_config = llm_configs.get(self.name, {})
        self.logger.info(f"LLM {self.name} 初始化完成")
    
    @abstractmethod
    async def completions(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        文本补全接口
        Args:
            content: 输入文本
            options: 可选参数
        Returns:
            生成的文本
        """
        pass
    
    async def completions_stream(self, content: str, options: Optional[Dict[str, Any]] = None) -> str:
        """
        流式文本补全接口（默认实现调用普通补全）
        Args:
            content: 输入文本
            options: 可选参数
        Returns:
            生成的文本
        """
        return await self.completions(content, options)
