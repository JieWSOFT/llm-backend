from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select
from core import security
from core.db import engine
from core.config import settings
from model import SysUser, TokenPayload
from loguru import logger

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> SysUser:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    user = session.get(SysUser, token_data.sub.split("#")[1])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_llm_user(session: SessionDep, token: TokenDep) -> SysUser:
    user = get_current_user(session, token)
    if not user.llm_avaiable:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="您没有可用的消费额度了",
        )
    # 如果存在就数量减一
    user.llm_avaiable = user.llm_avaiable - 1
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


CurrentUser = Annotated[SysUser, Depends(get_current_user)]
CurrentLLMUser = Annotated[SysUser, Depends(get_current_llm_user)]
