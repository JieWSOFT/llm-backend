import logging
import sys
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from sqlmodel import Session, select
from config.db import engine
from config.config import settings
from model import SysUser
from custom_logging import format_record


def my_job():
    logger.info(f"开始重置用户每日三次机会的任务：--------start---------------")
    # 重置 每天给用户三次机会
    with Session(engine) as session:
        statement = select(SysUser).where(SysUser.llm_avaiable < 3)
        users = session.exec(statement).all()
        for user in users:
            user.llm_avaiable = 3
        session.add_all(users)
        session.commit()
        logger.info(f"开始重置用户每日三次机会的任务：--------end---------------")


jobstores = {
    "pt": SQLAlchemyJobStore(
        url=str(settings.SQLALCHEMY_DATABASE_URI), tablename="my_tasks"
    ),
    "default": MemoryJobStore(),
}
executors = {"default": ThreadPoolExecutor(10), "processpool": ProcessPoolExecutor(3)}
job_defaults = {
    "coalesce": False,  # 堆积后只执行最后一个
    "max_instances": 1,  # 最大的实例只能存在一个
}
scheduler = BlockingScheduler(
    jobstores=jobstores, executors=executors, job_defaults=job_defaults
)
logger.configure(
    handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}]
)
logger.add(settings.LOG_DIR, encoding="utf-8", rotation="9:46")
scheduler._logger = logger
trigger = CronTrigger(hour=0, minute=0, second=0)
scheduler.add_job(my_job, trigger, id="daily_task")


def main():
    logger.info("定时任务启动")
    scheduler.start()

if __name__ == "__main__":
    main()
