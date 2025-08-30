from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from common.logger.logger import get_logger

logger = get_logger()


def task():
    logger.info(f"定时任务执行时间: {datetime.now()}")


# 创建后台调度器
scheduler = BackgroundScheduler()
scheduler.add_job(task, 'interval', seconds=30)  # 每 10 秒执行一次
# 或者每天固定时间执行
# scheduler.add_job(task, 'cron', hour=1, minute=0)
scheduler.start()
