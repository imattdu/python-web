from flask import jsonify, g

from common.exception_x.exception import ExceptionX, wrap_exception_x
from common.trace.trace import Trace


def json(data, exception: Exception = None):
    trace = g.get('trace', Trace())
    exception = wrap_exception_x(exception)
    return jsonify({
        'trace_id': trace.trace_id,
        'code': exception.code,
        'message': exception.message,
        'data': data
    })
