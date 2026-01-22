from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import time
import requests

@dataclass
class ConfluenceClient:
    base_url: str
    auth_type: str = "basic"
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

    timeout_secs: int = 10
    child_limit: int = 50
    search_limit: int = 20
    use_mock: bool = False

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

        if self.auth_type == "token" and self.token:
            clean_token = str(self.token).replace("Bearer ", "").strip()
            self.session.headers.update({"Authorization": f"Bearer {clean_token}"})
        elif self.username and self.password:
            self.session.auth = (self.username, self.password)

    def get_page_content(self, page_id: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        if self.use_mock:
            title = f"测试页面 {page_id}"
            html_body = "<p>这是一个测试页面的内容。</p><h2>项目进展</h2><ul><li>完成了需求分析</li><li>设计了系统架构</li><li>实现了核心功能</li></ul><h2>待办事项</h2><ul><li>编写单元测试</li><li>进行系统测试</li><li>部署到生产环境</li></ul>"
            return title, html_body, None
        
        url = f"{self.base_url}/rest/api/content/{page_id}?expand=body.storage"
        try:
            r = self.session.get(url, timeout=self.timeout_secs)

            if r.status_code == 404:
                result = (None, None, f"Page {page_id} not found")
            elif r.status_code == 401:
                result = (None, None, "Unauthorized")
            else:
                r.raise_for_status()
                data = r.json()
                title = data.get("title", "No Title")
                html_body = (data.get("body", {}) or {}).get("storage", {}).get("value", "")
                result = (title, html_body, None)
        except requests.RequestException as e:
            result = (None, None, f"Request failed: {e.__class__.__name__}")
        
        return result

    def get_child_pages(self, parent_id: str) -> Tuple[List[Dict[str, str]], Optional[str]]:
        if self.use_mock:
            pages = [
                {"id": f"{parent_id}-1", "title": f"子页面 1 - {parent_id}"},
                {"id": f"{parent_id}-2", "title": f"子页面 2 - {parent_id}"},
                {"id": f"{parent_id}-3", "title": f"子页面 3 - {parent_id}"}
            ]
            return pages, None
        
        url = f"{self.base_url}/rest/api/content/{parent_id}/child/page?limit={self.child_limit}"
        try:
            r = self.session.get(url, timeout=self.timeout_secs)
            if r.status_code == 401:
                result = ([], "Unauthorized")
            else:
                r.raise_for_status()
                results = (r.json() or {}).get("results", [])
                pages = [{"id": str(p["id"]), "title": str(p.get("title", ""))} for p in results if "id" in p]
                result = (pages, None)
        except requests.RequestException as e:
            result = ([], f"Request failed: {e.__class__.__name__}")
        
        return result

    def search_pages(self, cql: str) -> Tuple[List[Dict[str, str]], Optional[str]]:
        if self.use_mock:
            pages = [
                {"id": "search-1", "title": "搜索结果页面 1"},
                {"id": "search-2", "title": "搜索结果页面 2"},
                {"id": "search-3", "title": "搜索结果页面 3"}
            ]
            return pages, None
        
        url = f"{self.base_url}/rest/api/content/search"
        params = {"cql": cql, "limit": self.search_limit}
        try:
            r = self.session.get(url, params=params, timeout=self.timeout_secs)
            if r.status_code == 401:
                result = ([], "Unauthorized")
            else:
                r.raise_for_status()
                results = (r.json() or {}).get("results", [])
                pages = [{"id": str(p["id"]), "title": str(p.get("title", ""))} for p in results if "id" in p]
                result = (pages, None)
        except requests.RequestException as e:
            result = ([], f"Request failed: {e.__class__.__name__}")
        
        return result
