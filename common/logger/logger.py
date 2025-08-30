import json
import sys
import os
from datetime import datetime
from loguru import logger  # 必须导入 loguru

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 日志文件名，按天切割
log_file = os.path.join(LOG_DIR, f"m.log.{datetime.now().strftime('%Y%m%d%H')}")
warn_log_file = os.path.join(LOG_DIR, f"m.log.wf.{datetime.now().strftime('%Y%m%d%H')}")

# 移除默认 logger
logger.remove()

# 文件输出（JSON 格式，按大小切割，保留 7 天）
logger.add(
    log_file,
    rotation="1 hour",  # 日志文件大于 10 MB 切割
    retention="7 days",  # 保留最近 7 天
    level="INFO",
    filter=lambda record: record["level"].name == "INFO",  # 只记录 INFO
    format="{message}",
    serialize=True  # JSON 格式
)

# 文件输出（JSON 格式，按大小切割，保留 7 天）
logger.add(
    warn_log_file,
    rotation="1 hour",  # 日志文件大于 10 MB 切割
    retention="7 days",  # 保留最近 7 天
    level="WARNING",
    format="{message}",
    serialize=True  # JSON 格式
)


def get_logger():
    return logger
