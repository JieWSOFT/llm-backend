from sqlmodel import Session, select
from loguru import logger
from models.user import SysUser
from config.db import engine

def reset_user_daily_chances() -> None:
    """重置用户每日使用次数"""
    logger.info("开始重置用户每日使用次数")
    try:
        with Session(engine) as session:
            statement = select(SysUser).where(SysUser.llm_avaiable < 3)
            users = session.exec(statement).all()
            
            for user in users:
                user.llm_avaiable = 3
                
            session.add_all(users)
            session.commit()
            
        logger.info(f"重置完成,共重置 {len(users)} 个用户")
    except Exception as e:
        logger.error(f"重置用户使用次数失败: {e}")
        raise 