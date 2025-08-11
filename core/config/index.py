# 这个文件的作用是读取配置文件，配置文件的目录在 config 目录下，文件名是 config.yaml
# 读取 default.yaml，转换成一个 json 结构，然后放在内存里面，暴露一个 getConfig 方法，返回所有的配置信息，调用的时候判断一下，如果当前未加载过，则加载，如果加载过，则直接返回

import os
import yaml
import json
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器，负责读取和管理配置文件"""
    
    def __init__(self):
        self._config: Optional[Dict[str, Any]] = None
        self._config_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'default.yaml')
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件并转换为字典"""
        try:
            if not os.path.exists(self._config_file_path):
                raise FileNotFoundError(f"配置文件不存在：{self._config_file_path}")
            
            with open(self._config_file_path, 'r', encoding='utf-8') as file:
                config_data = yaml.safe_load(file)
                
            if config_data is None:
                return {}
                
            return config_data
        except yaml.YAMLError as e:
            raise ValueError(f"YAML 文件格式错误：{e}")
        except Exception as e:
            raise Exception(f"读取配置文件失败：{e}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取配置信息
        如果配置未加载过，则加载配置文件；如果已加载过，则直接返回缓存的配置
        """
        if self._config is None:
            self._config = self._load_config()
        
        return self._config.copy()  # 返回副本，避免外部修改影响内部状态
    
    def reload_config(self) -> Dict[str, Any]:
        """重新加载配置文件"""
        self._config = None
        return self.get_config()
    
    def get_config_as_json(self) -> str:
        """获取配置信息的 JSON 字符串表示"""
        config = self.get_config()
        return json.dumps(config, ensure_ascii=False, indent=2)


# 创建全局配置管理器实例
_config_manager = ConfigManager()


def get_config() -> Dict[str, Any]:
    """
    获取配置信息的便捷函数
    返回所有配置信息
    """
    return _config_manager.get_config()


def reload_config() -> Dict[str, Any]:
    """
    重新加载配置文件的便捷函数
    """
    return _config_manager.reload_config()


def get_config_as_json() -> str:
    """
    获取配置信息的 JSON 字符串表示的便捷函数
    """
    return _config_manager.get_config_as_json()


# 示例用法
if __name__ == "__main__":
    # 获取配置
    config = get_config()
    print("配置信息：")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    
    # 获取特定配置项
    mysql_config = config.get('mysql', {})
    print(f"\nMySQL 配置：")
    print(f"主机：{mysql_config.get('host')}")
    print(f"端口：{mysql_config.get('port')}")
    print(f"数据库：{mysql_config.get('database')}")

