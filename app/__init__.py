from flask import Flask, logging

app = Flask(__name__)

# 禁止 werkzeug 请求日志
# logging.getLogger('werkzeug').disabled = True
# app.logger.disabled = True
