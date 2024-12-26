from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.base import ConflictingIdError
from loguru import logger
from config.config import settings
from tasks.user_tasks import reset_user_daily_chances

class SchedulerManager:
    def __init__(self):
        self.scheduler = self._create_scheduler()
        self._init_jobs()

    def _create_scheduler(self) -> BlockingScheduler:
        """创建并配置调度器"""
        jobstores = {
            "default": MemoryJobStore(),
            "persistent": SQLAlchemyJobStore(
                url=str(settings.SQLALCHEMY_DATABASE_URI), 
                tablename="scheduler_jobs"
            )
        }
        
        executors = {
            "default": ThreadPoolExecutor(10),
            "processpool": ProcessPoolExecutor(3)
        }
        
        job_defaults = {
            "coalesce": False,  # 堆积后只执行最后一个
            "max_instances": 1,  # 最大实例只能存在一个
            "misfire_grace_time": 60  # 任务错过执行时间的容错时间(秒)
        }

        return BlockingScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults
        )

    def _init_jobs(self) -> None:
        """初始化所有定时任务"""
        # 每天0点重置用户机会
        self.add_daily_job(
            "reset_daily_chances",
            reset_user_daily_chances,
            "0 0 * * *",  # 分 时 日 月 周
            jobstore="persistent",  # 使用持久化存储
            replace_existing=True   # 如果任务已存在则替换
        )
        
        # 这里可以添加更多定时任务...

    def _get_next_run_time(self, job) -> str:
        """获取任务的下次执行时间"""
        try:
            if hasattr(job, 'next_run_time'):
                return job.next_run_time.strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else "未调度"
            elif hasattr(job, '_get_run_times'):
                next_time = job._get_run_times(1)
                return next_time[0].strftime("%Y-%m-%d %H:%M:%S") if next_time else "未调度"
            return "未知"
        except Exception as e:
            logger.warning(f"获取任务执行时间失败: {e}")
            return "未知"

    def add_daily_job(
        self, 
        job_id: str,
        func,
        cron: str,
        jobstore: str = "default",
        replace_existing: bool = False,
        **kwargs
    ) -> None:
        """添加定时任务"""
        try:
            # 如果任务已存在且不替换，则跳过
            if not replace_existing and self.scheduler.get_job(job_id, jobstore):
                job = self.scheduler.get_job(job_id, jobstore)
                next_run = self._get_next_run_time(job)
                logger.info(f"任务已存在且不替换: {job_id}, 下次执行时间: {next_run}")
                return

            # 如果任务已存在且需要替换，先移除旧任务
            if replace_existing and self.scheduler.get_job(job_id, jobstore):
                self.scheduler.remove_job(job_id, jobstore)
                logger.info(f"移除已存在的任务: {job_id}")

            # 解析 cron 表达式
            cron_parts = cron.split()
            if len(cron_parts) == 5:  # 标准 cron 格式: 分 时 日 月 周
                self.scheduler.add_job(
                    func,
                    "cron",
                    id=job_id,
                    minute=cron_parts[0],
                    hour=cron_parts[1],
                    day=cron_parts[2],
                    month=cron_parts[3],
                    day_of_week=cron_parts[4],
                    jobstore=jobstore,
                    replace_existing=replace_existing,
                    **kwargs
                )
                # 获取并打印下次执行时间
                job = self.scheduler.get_job(job_id, jobstore)
                next_run = self._get_next_run_time(job)
                logger.info(f"添加定时任务成功: {job_id}, cron: {cron}, 下次执行时间: {next_run}")
            else:
                raise ValueError(f"无效的cron表达式: {cron}")
        except Exception as e:
            logger.error(f"添加定时任务失败 {job_id}: {e}")

    def start(self) -> None:
        """启动调度器"""
        try:
            # 打印所有任务的下次执行时间
            for job in self.scheduler.get_jobs():
                next_run = self._get_next_run_time(job)
                logger.info(f"任务 {job.id} 下次执行时间: {next_run}")
            
            logger.info("调度器启动")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()
        except Exception as e:
            logger.error(f"调度器启动失败: {e}")
            raise

    def stop(self) -> None:
        """停止调度器"""
        try:
            self.scheduler.shutdown()
            logger.info("调度器已停止")
        except Exception as e:
            logger.error(f"调度器停止失败: {e}") 