from sqlmodel import Session, create_engine, select
from config.config import settings


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
