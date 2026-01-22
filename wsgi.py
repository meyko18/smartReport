import sys
import os
from app import create_app

import logging
class WerkzeugFilter(logging.Filter):
    def filter(self, record):
        return "This is a development server" not in record.getMessage()

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.addFilter(WerkzeugFilter())
werkzeug_logger.setLevel(logging.INFO)

app = create_app()

if __name__ == "__main__":
    import os
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        print("* Running on http://127.0.0.1:3001")
        print("* Running on http://10.1.88.72:3001 (LAN)")
    
    app.run(host="0.0.0.0", port=3001, debug=False)
