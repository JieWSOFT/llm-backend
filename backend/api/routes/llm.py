from typing import Sequence
from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from loguru import logger
from api.deps import CurrentLLMUser, CurrentUser, SessionDep
from model import LLMTemplate
from llm.main import create_chain
from api.type import ApiResponse, LLMRequestBody

router = APIRouter(tags=["llm"], prefix="/llm")
templates: Sequence[LLMTemplate]


def setTemplates(_templates: Sequence[LLMTemplate]):
    templates = _templates


def getTemplate(type: str) -> str:
    template: str = ""
    for temp in list(templates):
        if temp.type == type:
            template = temp.template
    return template


# 流式生成作文 (HTTP)
@router.post("/streaming", summary="根据类型和参数流式生成")
def streaming_endpoint(current_user: CurrentLLMUser, body: LLMRequestBody):
    template = getTemplate(body.type)

    if not template:
        return ApiResponse(code=500, message="未获取相对应的模板")

    chain = create_chain(template)

    # 异步生成器
    async def generate():
        async for chunk in chain.astream(body.params):
            yield chunk.content  # 逐步返回生成内容

    return StreamingResponse(generate(), media_type="text/plain")


# 一次性生成作文 (HTTP)
@router.post(
    "/generate", response_model=ApiResponse[str], summary="根据类型和参数直接生成"
)
async def generate_once(
    current_user: CurrentLLMUser, body: LLMRequestBody
) -> ApiResponse[str]:
    template = getTemplate(body.type)

    if not template:
        return ApiResponse(code=500, message="未获取相对应的模板")

    chain = create_chain(template)
    # 生成完整内容
    result = await chain.ainvoke(body.params)
    return ApiResponse(code=200, data=result.content)


# 获取llm服务可用次数
@router.get("/llmAvailable", summary="获取可用的llm服务可用次数")
def get_llm_available(current_user: CurrentUser) -> ApiResponse[int]:
    return ApiResponse(data=current_user.llm_avaiable)


# 增加llm服务可用次数
@router.post("/llmAvailable", summary="增加LLM的可调用次数")
def add_llm_available_num(
    session: SessionDep,
    current_user: CurrentUser,
    count: int = Body(1, embed=True, title="增加的调用次数"),
) -> ApiResponse:
    if not current_user.llm_avaiable:
        current_user.llm_avaiable = count
    else:
        current_user.llm_avaiable = count + current_user.llm_avaiable
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return ApiResponse(code=200)
