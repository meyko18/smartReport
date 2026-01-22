from __future__ import annotations

from bs4 import BeautifulSoup

_SOUP_PARSER = "html.parser"
_CLEAN_NODES = ["script", "style", "ac:structured-macro"]

def clean_html_to_text(html_content: str) -> str:
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, _SOUP_PARSER)

    for node in soup(_CLEAN_NODES):
        node.extract()

    text = soup.get_text(separator="\n")
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
    return "\n".join(lines)
