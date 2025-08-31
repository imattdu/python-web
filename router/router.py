from flask import request, jsonify, g

from app import app
from client.httpclient.session_pool_request import global_session_pool_http_client
from common.exception_x.exception import ExceptionX, wrap_exception_x

from common.logger.logger import info
from common.trace import trace
from render.json import json as json_x


@app.before_request
def log_before_request_info():
    # 尝试获取 JSON 请求体，如果没有就为空
    headers = {}
    for k, v in request.headers.items():
        headers[k] = v
        print(k, v)
    t = trace.Trace(headers)
    g.setdefault('trace', t)
    try:
        body = request.get_json(silent=True)
    except Exception as e:
        err = str(e)
        body = None

    info('_com_request_in', {
        'uri': request.path,
        'url': request.url,
        'body': body,
    })


@app.after_request
def log_after_request_info(response):
    info('_com_request_out', {
        "method": request.method,
        "path": request.path,
        "response_data": response.get_data(as_text=True)[:500]})
    return response


@app.get("/")
def index():
    info('abc', {
        'a': {
            'f1': 123,
        }
    })
    result, exc = global_session_pool_http_client.get('http://127.0.0.1:8001/444?a=123&b=3')
    return json_x({
        'ping': 'pong'
    }, exception=exc)


@app.get("/t1")
def t1():
    return json_x({
        't1': 't1'
    })
