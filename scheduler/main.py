import sys
import logging
from loguru import logger
from config.config import settings
from utils.scheduler_manager import SchedulerManager
from utils.custom_logging import InterceptHandler, format_record

def setup_logging():
    """配置日志"""
    # 配置loguru
    logger.configure(
        handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}]
    )
    logger.add(settings.LOG_DIR, encoding="utf-8", rotation="00:00")
    
    # 替换Python标准库的日志处理
    logging.getLogger().handlers = [InterceptHandler()]

def main():
    """主函数"""
    # 设置日志
    setup_logging()
    
    # 创建并启动调度器
    scheduler = SchedulerManager()
    scheduler.start()

if __name__ == "__main__":
    main()
