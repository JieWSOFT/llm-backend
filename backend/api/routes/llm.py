from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse

from api.deps import CurrentLLMUser, CurrentUser, SessionDep
from llm.main import create_essay_chain
from api.type import ApiResponse


router = APIRouter(tags=["llm"], prefix="/llm")
# 作文
essaychain = create_essay_chain()


# 流式生成作文 (HTTP)
@router.get("/essay/streaming",summary='流式调用生成作文')
def streaming_endpoint(current_user: CurrentLLMUser, topic: str, length: int = 500):
    # 异步生成器
    async def generate():
        async for chunk in essaychain.astream({"topic": topic, "length": length}):
            yield chunk.content  # 逐步返回生成内容

    return StreamingResponse(generate(), media_type="text/plain")


# 一次性生成作文 (HTTP)
@router.get("/essay/generate", response_model=ApiResponse[str],summary="直接生成作文")
async def generate_once(
    current_user: CurrentLLMUser,
    topic: str,
    length: int = 500,
) -> ApiResponse[str]:
    # 生成完整内容
    result = await essaychain.ainvoke({"topic": topic, "length": length})
    return ApiResponse(code=200, data=result.content)


# 获取llm服务可用次数
@router.get("/llmAvailable",summary="获取可用的llm服务可用次数")
def get_llm_available(current_user: CurrentUser) -> ApiResponse[int]:
    return ApiResponse(data=current_user.llm_avaiable)


# 增加llm服务可用次数
@router.post("/llmAvailable",summary="增加LLM的可调用次数")
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
