from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

import markdown as md

from ..clients.confluence_client import ConfluenceClient
from .llm_service import LLMService

@dataclass
class AnalyzeService:
    confluence_client: ConfluenceClient
    llm_service: LLMService
    html_cleaner: Callable[[str], str]
    max_pages: int = 10

    def _build_pages_to_process(self, mode: str, target_value: str) -> List[Dict[str, str]]:
        mode = (mode or "").strip()

        if mode == "single":
            return [{"id": target_value, "title": "Target Page"}]

        if mode == "url":
            pages = [{"id": target_value, "title": "Parent Page"}]
            children, err = self.confluence_client.get_child_pages(target_value)
            if err:
                return []
            pages.extend(children)
            return pages

        if mode == "search":
            cql = target_value
            lower = target_value.lower()
            if ("text ~" not in lower) and ("title ~" not in lower):
                # 转义引号，避免CQL语法错误
                escaped_value = target_value.replace('"', '"')
                cql = f'text ~ "{escaped_value}"'
            pages, err = self.confluence_client.search_pages(cql)
            if err:
                return []
            return pages

        return []

    def run(self, mode: str, target_value: str, keyword: str, ai_extension: str = "") -> Dict:
        pages_to_process = self._build_pages_to_process(mode, target_value)

        if not pages_to_process:
            return {"status": "error", "message": "未找到任何页面，请检查认证信息、ID 或搜索条件。"}

        all_text_blocks: List[str] = []
        processed_count = 0

        max_pages = self.max_pages
        for page in pages_to_process[:max_pages]:
            title, html_body, err = self.confluence_client.get_page_content(page["id"])
            if err or not html_body:
                continue
            
            clean_text = self.html_cleaner(html_body)
            
            if clean_text.strip():
                all_text_blocks.append(f"Page Title: {title}\nContent:\n{clean_text}\n---")
                processed_count += 1

        if not all_text_blocks:
            if processed_count == 0:
                return {"status": "warning", "message": "成功连接Confluence，但未获取到任何页面内容。请检查页面ID是否正确，或页面是否为空。"}
            return {"status": "warning", "message": "成功获取页面，但页面内容清理后为空。"}

        full_context = "\n".join(all_text_blocks)
        llm_keyword = keyword if keyword else "全文核心内容"
        
        report_markdown = self.llm_service.summarize(full_context, llm_keyword, ai_extension)
        report_html = md.markdown(report_markdown, extensions=["fenced_code", "tables"])

        return {
            "status": "success",
            "processed_count": processed_count,
            "report": report_html,
            "report_markdown": report_markdown,
        }
