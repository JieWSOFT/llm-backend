from typing import Annotated
from fastapi import Depends, HTTPException, status
from api.deps import SessionDep, TokenDep, get_current_user
from model import SysUser


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


CurrentLLMUser = Annotated[SysUser, Depends(get_current_llm_user)]
