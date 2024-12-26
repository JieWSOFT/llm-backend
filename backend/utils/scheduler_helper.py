from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger


class SchedulerHelper:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.jobs = {}  # 存储所有的任务引用

    def start(self):
        """启动调度器"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("调度器启动成功")

    def stop(self):
        """停止调度器"""
        if self.scheduler.running:
            try:
                self.scheduler.shutdown()
                logger.info("调度器已停止")
            except Exception as e:
                logger.error(f"停止调度器失败: {e}")

    def add_job(self, job_id: str, func, trigger: str, **trigger_args):
        """添加定时任务"""
        if not self.scheduler.running:
            logger.warning("调度器未启动，无法添加任务")
            return None

        # 如果任务已存在，先移除
        if job_id in self.jobs:
            self.remove_job(job_id)

        # 添加新任务
        job = self.scheduler.add_job(func, trigger, id=job_id, **trigger_args)
        self.jobs[job_id] = job
        logger.info(f"添加任务成功: {job_id}")
        return job

    def remove_job(self, job_id: str):
        """移除定时任务"""
        if job_id in self.jobs:
            try:
                self.scheduler.remove_job(job_id)
                del self.jobs[job_id]
                logger.info(f"移除任务成功: {job_id}")
            except Exception as e:
                logger.error(f"移除任务失败 {job_id}: {e}")

    def __del__(self):
        """析构函数，确保调度器被正确关闭"""
        self.stop() 