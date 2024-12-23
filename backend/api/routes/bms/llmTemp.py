from fastapi import APIRouter, Query
from loguru import logger
from sqlalchemy import func
from sqlmodel import desc, select

from api.type import ApiResponse, PageBody
from api.routes.bms.deps import checkReferer
from api.deps import SessionDep
from api.routes.bms.type import llmTempBody
from model import LLMTemplate


router = APIRouter(tags=["bms"], prefix="/bms/llm")


@router.get("/temp/list", dependencies=[checkReferer], summary="获取模板列表分页")
def getTempList(
    session: SessionDep,
    pageSize: int = Query(10, ge=1, le=100, description="每一页条数"),
    page: int = Query(1, ge=1, description="第几页"),
):
    page = page - 1
    # 构造查询
    statement = select(func.count(LLMTemplate.id))
    total_count = session.exec(statement).first()
    statement = (
        select(LLMTemplate)
        .order_by(desc(LLMTemplate.createTime))
        .offset(page)
        .limit(pageSize)
    )
    results = session.exec(statement).all()
    return ApiResponse(code=200, data=PageBody(total=total_count, list=results))


@router.post("/temp/create", dependencies=[checkReferer], summary="添加模板")
def addTemp(session: SessionDep, body: llmTempBody):
    temp = LLMTemplate(template=body.template, type=body.type)
    session.add(temp)
    session.commit()
    session.refresh(temp)
    return ApiResponse(code=200, data="")


@router.put("/temp/update", dependencies=[checkReferer], summary="修改模板")
def updateTemp(session: SessionDep, body: llmTempBody):
    if not body.id:
        return ApiResponse(code=500, data="缺少ID")
    statement = select(LLMTemplate).where(LLMTemplate.id == body.id)
    item = session.exec(statement).first()

    if not item:
        return ApiResponse(code=500, data="没有这条纪录去修改")

    if body.template:
        item.template = body.template

    if body.type:
        item.type = body.type

    session.add(item)
    session.commit()
    session.refresh(item)
    return ApiResponse(code=200, data="")


@router.delete("/temp/delete", dependencies=[checkReferer], summary="根据ID删除")
def deleteTemp(session: SessionDep, id=Query(description="模板ID")):
    statement = select(LLMTemplate).where(LLMTemplate.id == int(id))
    item = session.exec(statement).first()
    if not item:
        return ApiResponse(code=500, data="没有这条纪录去删除")
    session.delete(item)
    session.commit()
    return ApiResponse(code=200, data="")
