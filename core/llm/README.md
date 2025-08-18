# Coze Like LLM 模块

## 概述

这是一个基于 Coze API 的大语言模型 Python 实现，从 Node.js 项目 `lh-tts` 迁移而来。该模块提供了与 Coze 平台集成的文本生成和对话功能。

## 功能特性

- 🤖 **多模型支持**：支持多种 Coze 模型类型（DOUBAO_THINKING、DOUBAO_16_THINKING 等）
- 🔄 **自动配置选择**：从数据库中随机选择可用的 Coze 配置
- 🛡️ **容错机制**：支持配额限制时自动切换配置
- 📊 **完整日志**：详细的操作日志和错误跟踪
- 🔧 **易于扩展**：模块化设计，支持添加新的功能

## 文件结构

```
core/llm/
├── __init__.py              # 模块初始化
├── types.py                 # 类型定义和枚举
├── base.py                  # 基础 LLM 抽象类
├── coze_jwt.py             # Coze JWT TTS 实现
├── coze_like.py            # 主要的 LLM 实现类
├── test_coze_like.py       # 测试文件
├── example.py              # 使用示例
└── README.md               # 本文档

core/mysql/
├── coze_info.py            # Coze 配置信息数据访问层
├── index_tts.py            # TTS 数据库连接（新增）
└── ...
```

## 依赖要求

在项目根目录的 `requirements.txt` 中已包含所需依赖：

```
PyJWT>=2.8.0
cryptography>=41.0.0
requests>=2.31.0
```

## 数据库配置

确保 `config/default.yaml` 中包含 TTS 数据库配置：

```yaml
mysql:
  main:
    host: your_main_host
    port: 13306
    username: your_main_user
    password: your_main_password
    database: your_main_db
  tts:
    host: your_tts_host
    port: 13306
    username: your_tts_user
    password: your_tts_password
    database: your_tts_db
```

## 数据库表结构

需要在 TTS 数据库中创建 `coze_info` 表：

```sql
CREATE TABLE `coze_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gmt_create` datetime DEFAULT CURRENT_TIMESTAMP,
  `gmt_modify` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `name` varchar(255) DEFAULT NULL,
  `phone` varchar(50) DEFAULT NULL,
  `app_id` varchar(255) DEFAULT NULL,
  `aud` varchar(255) DEFAULT NULL,
  `private_key` text,
  `key_id` varchar(255) DEFAULT NULL,
  `region` varchar(50) DEFAULT NULL,
  `comment` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 使用方法

### 基本用法

```python
import asyncio
from core.llm.coze_like import create_coze_like_llm
from core.llm.types import ELLMType

async def main():
    # 创建并初始化 LLM 实例
    llm = await create_coze_like_llm(ELLMType.DOUBAO_THINKING)
    
    # 进行对话
    response = await llm.completions("你好，请介绍一下你自己")
    print(f"回复：{response}")

# 运行
asyncio.run(main())
```

### 高级用法

```python
from core.llm.coze_like import LLMCozeLike
from core.llm.types import ELLMType

async def advanced_example():
    # 手动创建实例
    llm = LLMCozeLike(ELLMType.DOUBAO_16_THINKING)
    await llm.init()
    
    # 批量处理
    questions = ["问题1", "问题2", "问题3"]
    
    for question in questions:
        try:
            answer = await llm.completions(question)
            print(f"Q: {question}")
            print(f"A: {answer}\n")
        except Exception as e:
            print(f"处理失败：{e}")

asyncio.run(advanced_example())
```

## 支持的模型类型

```python
class ELLMType(Enum):
    DEEPSEEK = 'deepseek'
    DEEPSEEK0528 = 'deepseek0528'
    VOLCEENGINE_DEEPSEEK_NETWORK = 'volcengineDeepSeekNetwork'
    DOUBAO_THINKING = 'doubao15Thinking'
    DOUBAO_16_THINKING = 'doubao16Thinking'
    OPENAI = 'openai'
    DOUBAO = 'doubao15pro'
```

## 配置说明

### Coze 配置信息

每个 Coze 配置需要包含以下信息：

- `name`: 配置名称
- `app_id`: Coze 应用 ID
- `aud`: JWT audience
- `private_key`: RSA 私钥（用于 JWT 签名）
- `key_id`: 密钥 ID
- `region`: 区域设置
- `comment`: JSON 格式的额外配置，包含各模型的 agent_id

### comment 字段格式

```json
{
  "doubao15Thinking": {
    "agent_id": "your_agent_id_1"
  },
  "doubao16Thinking": {
    "agent_id": "your_agent_id_2"
  }
}
```

## 测试

运行测试文件验证功能：

```bash
# 基础功能测试
python3 core/llm/test_coze_like.py

# 使用示例
python3 core/llm/example.py
```

## 错误处理

系统包含完善的错误处理机制：

1. **配置验证**：自动验证 Coze 配置的完整性
2. **网络重试**：支持网络请求失败时的重试机制
3. **配额管理**：配额限制时自动切换到其他配置
4. **详细日志**：记录所有关键操作和错误信息

## 扩展功能

### TTS 功能

虽然主要用于文本生成，但也保留了 TTS 相关的接口：

```python
from core.llm.types import TTSOptions

# TTS 选项
options = TTSOptions(
    text="要转换的文本",
    speed=1.0,
    voice="语音ID"
)

# 调用 TTS（需要实现完整的 TTS 功能）
# result = await llm.coze_jwt_tts.tts(options)
```

### 工作空间和机器人管理

```python
# 获取工作空间列表
workspaces = await llm.list_workspaces()

# 获取机器人列表
bots = await llm.list_bots(coze_info, space_id)

# 创建新机器人
new_bot = await llm.create_bot(coze_info, space_id, "机器人名称")
```

## 注意事项

1. **网络连接**：需要稳定的网络连接访问 Coze API
2. **配置管理**：确保数据库中有有效的 Coze 配置信息
3. **API 限制**：注意 Coze API 的调用频率和配额限制
4. **私钥安全**：妥善保管 RSA 私钥，不要泄露到代码仓库

## 从 Node.js 迁移的变化

1. **异步处理**：使用 Python 的 `async/await` 语法
2. **类型系统**：使用 `dataclass` 和 `typing` 模块
3. **日志系统**：使用 Python 标准的 `logging` 模块
4. **数据库访问**：适配项目现有的 MySQL 连接池
5. **错误处理**：使用 Python 的异常处理机制

## 版本历史

- **v1.0**: 初始版本，从 Node.js 项目迁移核心功能
- 支持文本补全和流式对话
- 集成数据库配置管理
- 完整的错误处理和日志记录

---

**作者**: AI Assistant  
**最后更新**: 2025-08-13
