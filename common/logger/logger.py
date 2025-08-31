import json
import sys
import os
from datetime import datetime
from typing import Any

from flask import g, has_app_context
from loguru import logger  # 必须导入 loguru

from common.trace.trace import Trace

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件名，按天切割
log_file = os.path.join(LOG_DIR, f"m.log.{datetime.now().strftime('%Y%m%d%H')}")
warn_log_file = os.path.join(LOG_DIR, f"m.log.wf.{datetime.now().strftime('%Y%m%d%H')}")

# 移除默认 logger
logger.remove()


# 自定义 patch，把 Flask g.trace 注入 extra
def upsert_record(record):
    t = record["extra"]["trace"]
    if t:
        record["extra"]["trace"] = str(t)
    print(record['extra'])


logger.configure(
    extra={"trace": None, 'tag': '_undef'},
    patcher=upsert_record
)

# 文件输出（JSON 格式，按大小切割，保留 7 天）
logger.add(
    log_file,
    rotation="1 hour",  # 日志文件大于 10 MB 切割
    retention="7 days",  # 保留最近 7 天
    level="INFO",
    filter=lambda record: record["level"].name == "INFO",  # 只记录 INFO
    format="[{level}][{time:YYYY-MM-DD HH:mm:ss}]||[{name}@{function}():{line}] {extra[tag]}||{extra[trace]}||{message}",
    serialize=False  # JSON 格式
)

# 文件输出（JSON 格式，按大小切割，保留 7 天）
logger.add(
    warn_log_file,
    rotation="1 hour",  # 日志文件大于 10 MB 切割
    retention="7 days",  # 保留最近 7 天
    level="WARNING",
    format="[{level}][{time:YYYY-MM-DD HH:mm:ss}]||[{name}@{function}():{line}] {extra[tag]}||{extra[trace]}||{message}",
    serialize=False  # JSON 格式
)


def get_logger():
    return logger


def _msg(msg: any):
    if isinstance(msg, dict):
        return "||".join(f"{k}={json.dumps(v, separators=(',', ':'))}" for k, v in msg.items())
    else:
        # 如果不是 dict，直接转成字符串
        return str(msg)


def _prepare_extra(t: str, **kwargs):
    kwargs['tag'] = t
    if 'trace' not in kwargs:
        trace = Trace()
        if has_app_context():
            trace = getattr(g, "trace", trace)
        kwargs['trace'] = trace
    return kwargs


def info(t: str, message: any, **kwargs):
    kwargs = _prepare_extra(t, **kwargs)
    logger.bind(**kwargs).opt(depth=1).info(_msg(message))


def warning(t: str, message: any, **kwargs):
    kwargs = _prepare_extra(t, **kwargs)
    logger.bind(**kwargs).opt(depth=1).warning(_msg(message))
