import logging

from flask import Flask

from app import app
from router import router
from task import task

if __name__ == "__main__":
    app.logger.disabled = True
    # 禁用 werkzeug 的请求日志
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.disabled = True
    app.run(debug=True, port=8001)
