from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request, current_app

from ..services.analyze_service import AnalyzeService
from ..services.llm_service import LLMService
from ..clients.confluence_client import ConfluenceClient
from ..utils.html_cleaner import clean_html_to_text

bp = Blueprint("pages", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/health")
def health():
    return jsonify({"status": "ok"})

@bp.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}

    mode = (data.get("mode") or "").strip()
    target_value = (data.get("targetValue") or "").strip()
    keyword = (data.get("keyword") or "").strip()
    ai_extension = (data.get("aiExtension") or "").strip()
    
    if target_value:
        from urllib.parse import urlparse, parse_qs
        parsed_url = urlparse(target_value)
        if parsed_url.netloc and parsed_url.path:
            if parsed_url.path.endswith("viewpage.action"):
                query_params = parse_qs(parsed_url.query)
                if "pageId" in query_params:
                    target_value = query_params["pageId"][0]

    auth_type = (data.get("authType") or "basic").strip()
    username = data.get("username")
    password = data.get("password")
    token = data.get("token")

    conf_url = current_app.config["CONFLUENCE_BASE_URL"]
    
    if auth_type == "basic":
        if not username:
            username = current_app.config["DEFAULT_USERNAME"]
        if not password:
            password = current_app.config["DEFAULT_PASSWORD"]
        
        if not username or not password:
            return jsonify({"status": "error", "message": "缺少用户名或密码"}), 400
    else:
        if not token:
            token = current_app.config["DEFAULT_TOKEN"]
        
        if not token:
            return jsonify({"status": "error", "message": "缺少 Token"}), 400

    use_real_llm = bool(current_app.config["USE_REAL_LLM"])
    use_mock = not use_real_llm
    
    client = ConfluenceClient(
        base_url=conf_url,
        auth_type=auth_type,
        username=username,
        password=password,
        token=token,
        timeout_secs=int(current_app.config["CONFLUENCE_TIMEOUT_SECS"]),
        child_limit=int(current_app.config["CONFLUENCE_CHILD_LIMIT"]),
        search_limit=int(current_app.config["CONFLUENCE_SEARCH_LIMIT"]),
        use_mock=use_mock,
    )

    llm = LLMService(
        api_url=current_app.config["LLM_API_URL"],
        model=current_app.config["LLM_MODEL"],
        api_key=current_app.config.get("LLM_API_KEY"),
        temperature=float(current_app.config["LLM_TEMPERATURE"]),
        timeout_secs=int(current_app.config["LLM_TIMEOUT_SECS"]),
        input_max_chars=int(current_app.config["LLM_INPUT_MAX_CHARS"]),
        use_real_llm=use_real_llm,
        prompt_template=current_app.config["LLM_PROMPT_TEMPLATE"],
        mock_response=current_app.config["LLM_MOCK_RESPONSE"],
    )

    service = AnalyzeService(
        confluence_client=client,
        llm_service=llm,
        html_cleaner=clean_html_to_text,
        max_pages=int(current_app.config["MAX_PAGES"]),
    )

    try:
        result = service.run(mode=mode, target_value=target_value, keyword=keyword, ai_extension=ai_extension)
        status_code = 400 if result.get("status") == "error" else 200
        return jsonify(result), status_code
    except Exception as e:
        current_app.logger.exception("Analyze failed")
        return jsonify({"status": "error", "message": f"服务异常: {e.__class__.__name__}"}), 500
