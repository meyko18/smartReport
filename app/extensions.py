from __future__ import annotations

import logging
import sys
from flask import Flask

def configure_logging(app: Flask) -> None:
    level = logging.DEBUG if app.config.get("DEBUG") else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s"
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)

    app.logger.setLevel(level)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
