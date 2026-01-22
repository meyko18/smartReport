from __future__ import annotations

import os
from dataclasses import dataclass

@dataclass(frozen=True)
class BaseConfig:
    ENV_NAME: str = "base"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")

    CONFLUENCE_BASE_URL = "https://space.jaguarmicro.com"
    CONFLUENCE_TIMEOUT_SECS: int = int(os.getenv("CONFLUENCE_TIMEOUT_SECS", "10"))
    CONFLUENCE_CHILD_LIMIT: int = int(os.getenv("CONFLUENCE_CHILD_LIMIT", "50"))
    CONFLUENCE_SEARCH_LIMIT: int = int(os.getenv("CONFLUENCE_SEARCH_LIMIT", "20"))
    MAX_PAGES: int = int(os.getenv("MAX_PAGES", "10"))

    LLM_API_URL: str = os.getenv("LLM_API_URL", "https://api.example.com/llm")
    LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "your-internal-model-name")
    LLM_TIMEOUT_SECS: int = int(os.getenv("LLM_TIMEOUT_SECS", "60"))
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.3"))

    LLM_INPUT_MAX_CHARS: int = int(os.getenv("LLM_INPUT_MAX_CHARS", "15000"))

    LLM_PROMPT_TEMPLATE: str = os.getenv("LLM_PROMPT_TEMPLATE", """
你是一个专业的内容总结助手。请根据以下提供的 Confluence 页面内容，
提取与关键词 "{query_keywords}" 相关的所有重要信息、关键点和核心内容。

要求：
1. 形成一份简洁明了的总结，标题为《{query_keywords} 相关内容总结》。
2. 分事项呈现（使用 Markdown 列表），突出重点内容。
3. 保留原始内容的核心信息，去除冗余内容。
4. 如果内容无关，请直接忽略。

=== 内容开始 ===
{content}
=== 内容结束 ===
""")

    LLM_MOCK_RESPONSE: str = os.getenv("LLM_MOCK_RESPONSE", """### 📊 智能内容总结：{query_keywords}

> 模拟返回（未启用真实模型）

## 1. 核心内容

### 1.1 关键信息

- ✅ 提取了与关键词相关的核心信息点
- ✅ 识别了重要的事实和数据
- ✅ 整理了相关的概念和定义
- ✅ 总结了主要观点和结论

### 1.2 重要发现

- 📌 发现了内容中的关键趋势和模式
- 📌 识别了潜在的问题和挑战
- 📌 整理了相关的解决方案和建议
- 📌 提取了有价值的见解和启示

## 2. 结构总结

### 2.1 内容组织

- 📋 内容采用了清晰的层级结构
- 📋 包含了明确的标题和小标题
- 📋 使用了列表、表格等格式化元素
- 📋 内容逻辑连贯，易于理解

### 2.2 重点章节

- 📖 第一章：介绍了背景和目的
- 📖 第二章：详细阐述了核心概念
- 📖 第三章：分析了相关数据和案例
- 📖 第四章：提供了结论和建议

## 3. 总结要点

### 3.1 主要内容

- 💡 内容涵盖了多个方面的信息
- 💡 提供了详细的说明和解释
- 💡 包含了丰富的示例和案例
- 💡 提供了实用的指导和建议

### 3.2 价值与意义

- 🔍 内容具有较高的参考价值
- 🔍 提供了有深度的分析和见解
- 🔍 有助于理解相关领域的知识
- 🔍 为决策提供了有力的支持

## 4. 结论

本次总结从提供的内容中提取了与关键词相关的重要信息，包括核心内容、重要发现、结构总结和总结要点。这些信息有助于快速了解内容的主要内容和价值，为后续的学习和应用提供了有力的支持。

---

**总结生成时间**：2026-01-21
**总结生成人**：智能总结助手
**总结类型**：内容总结
**总结版本**：1.0.0
""")

    USE_REAL_LLM: bool = os.getenv("USE_REAL_LLM", "false").lower() == "true"
    
    DEFAULT_USERNAME: str = os.getenv("DEFAULT_USERNAME", "")
    DEFAULT_PASSWORD: str = os.getenv("DEFAULT_PASSWORD", "")
    DEFAULT_TOKEN: str = os.getenv("DEFAULT_TOKEN", "")

@dataclass(frozen=True)
class DevConfig(BaseConfig):
    ENV_NAME: str = "dev"
    DEBUG: bool = True

@dataclass(frozen=True)
class ProdConfig(BaseConfig):
    ENV_NAME: str = "prod"
    DEBUG: bool = False

def get_config():
    env = os.getenv("APP_ENV", "dev").lower()
    if env in ("prod", "production"):
        return ProdConfig
    return DevConfig
