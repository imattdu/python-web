# 请求前日志打印
from datetime import datetime

from flask import request, jsonify

from app import app
from client.httpclient.session_pool_request import global_session_pool_http_client as http_cli
from common.logger.logger import get_logger

logger = get_logger()


@app.before_request
def log_before_request_info():
    # 尝试获取 JSON 请求体，如果没有就为空
    try:
        body = request.get_json(silent=True)
    except Exception:
        body = None

    logger.info({
        "tag": "_com_request_in",
        "method": request.method,
        "path": request.path,
        "args": request.args.to_dict(),
        "body": body if body is not None else request.get_data(as_text=True)[:500]  # 限制长度避免过大
    })


@app.after_request
def log_after_request_info(response):
    logger.info({
        "tag": "_com_request_out",
        "method": request.method,
        "path": request.path,
        "response_data": response.get_data(as_text=True)[:500]  # 可选截断，避免日志过大
    })
    return response


@app.route("/")
def index():
    http_cli.get('xxx')

    return jsonify({
        'ping': 'pong'
    })
