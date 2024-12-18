from fastapi import APIRouter, Body, HTTPException
from loguru import logger
import requests
from sqlmodel import Session, select
from api.deps import SessionDep, CurrentUser
from api.type import ApiResponse
from core.config import settings
from core.security import create_access_token
import uuid

from model import SysUser, UserAction

router = APIRouter(tags=["wx"], prefix="/wx")


def CreateUser(session: Session, openId):
    user = SysUser(openId=openId, username=str(uuid.uuid4())[:10])
    session.add(user)
    session.commit()
    session.refresh(user)
    user2 = session.exec(select(SysUser).where(SysUser.openId == openId)).first()
    userConfig = UserAction(userId=user2.id, username=user.username)
    session.add(userConfig)
    session.commit()
    session.refresh(userConfig)
    return user2


@router.post("/login", summary="微信code登录")
def wxLogin(
    session: SessionDep,
    code: str = Body(1, title="微信code", embed=True),
):
    logger.info(f"微信登录鉴权----start----code: {code}")
    appId = settings.WX_APP_ID
    appSecret = settings.WX_APP_SECRET
    url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={appSecret}&js_code={code}&grant_type=authorization_code"
    response = requests.get(url)
    data = response.json()
    if "errcode" in data:
        raise HTTPException(status_code=400, detail=data["errmsg"])
    openId = data["openid"]
    statement = select(SysUser).where(SysUser.openId == openId)
    session_user = session.exec(statement).first()
    if not session_user:
        logger.info(f"微信登录鉴权----pendding----用户不存在 创建用户----code: {code}")
        session_user = CreateUser(session, openId)
    else:
        logger.info(f"微信登录鉴权----pendding----用户存在----code: {code}")
    logger.info(f"微信登录鉴权----end----code: {code}")
    token = create_access_token(f"{openId}#{session_user.id}")
    return ApiResponse(code=200, data=token)


@router.get("getUserInfo", summary="获取微信用户信息")
def wxUserInfo(
    current_user: CurrentUser,
) -> ApiResponse:

    return ApiResponse(code=200, data=current_user.model_dump(exclude={"openId"}))


@router.post("shareAddAvailableCounts", summary="分享添加次数")
def wxShareAddAvailableCounts(
    current_user: CurrentUser,
    session: SessionDep,
) -> ApiResponse:
    statement = select(UserAction).where(current_user.id)
    sessionAction = session.exec(statement).first()
    if not sessionAction.shareCount:
        # 如果没有分享过才增加分享次数
        action = UserAction(
            id=sessionAction.id, username=sessionAction.username, shareCount=1
        )
        current_user.llm_avaiable += 3
        session.add(action)
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return ApiResponse(code=200, data="")
    else:
        return ApiResponse(code=500, data="该用户已经用过分享获取次数的机会")
