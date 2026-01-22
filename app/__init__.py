from __future__ import annotations

import logging
from flask import Flask

from dotenv import load_dotenv
load_dotenv()

from .config import get_config
from .extensions import configure_logging
from .routes.pages import bp as pages_bp

def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates")

    app.config.from_object(get_config())

    configure_logging(app)

    app.register_blueprint(pages_bp)

    logging.getLogger(__name__).info("App created with config=%s", app.config.get("ENV_NAME"))
    return app
