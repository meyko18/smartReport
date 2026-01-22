from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple
import time
import requests

@dataclass
class LLMService:
    api_url: str
    model: str
    api_key: str | None = None
    temperature: float = 0.3
    timeout_secs: int = 60
    input_max_chars: int = 15000
    use_real_llm: bool = False
    prompt_template: str = ""
    mock_response: str = ""

    def summarize(self, text_data: str, query_keywords: str, ai_extension: str = "") -> str:
        if not text_data.strip():
            return "未获取到有效内容，无法生成报告。"

        truncated = text_data[: self.input_max_chars]

        template = self.prompt_template
        if ai_extension:
            template = template.replace("=== 内容开始 ===", f"=== 内容开始 ===\n\n额外要求：{ai_extension}\n")
        
        prompt = template.format(
            query_keywords=query_keywords,
            content=truncated
        )

        if not self.use_real_llm:
            response = self.mock_response.format(query_keywords=query_keywords)
            if ai_extension:
                response += f"\n\n## 5. AI扩展指令执行情况\n\n- ℹ️ 已应用AI扩展指令：{ai_extension}\n- ℹ️ 指令已嵌入到prompt中，影响了生成结果\n- ℹ️ 在真实模型中，指令会指导AI生成更符合要求的内容"
        else:
            if not self.api_url or self.api_url in ("", "https://api.example.com/llm"):
                response = self.mock_response.format(query_keywords=query_keywords)
                if ai_extension:
                    response += f"\n\n## 5. AI扩展指令执行情况\n\n- ℹ️ 已应用AI扩展指令：{ai_extension}\n- ℹ️ 提示：您未配置 LLM_API_URL，已自动切换到模拟模式\n"
            else:
                headers = {
                    "Content-Type": "application/json",
                }

                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"

                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": self.temperature,
                }

                try:
                    resp = requests.post(
                        self.api_url,
                        headers=headers,
                        json=payload,
                        timeout=self.timeout_secs,
                    )

                    resp.raise_for_status()
                    data = resp.json()
                    response = data["choices"][0]["message"]["content"]
                except requests.exceptions.MissingSchema:
                    return f"错误：LLM_API_URL 格式无效，请检查配置。当前值：{self.api_url}"
                except requests.exceptions.RequestException as e:
                    return f"错误：调用 LLM 服务失败：{str(e)}"
        
        return response
