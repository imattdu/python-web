import logging

from app import app
from app import router
from common.logger.logger import get_logger
from app.task import task

if __name__ == "__main__":
    app.logger.disabled = True
    # 禁用 werkzeug 的请求日志
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.disabled = True
    app.run(debug=False, port=8001)
