from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.deps import CurrentUser
from llm.main import create_essay_chain
from api.type import ApiResponse


router = APIRouter(tags=["llm"], prefix="/llm")
# 作文
essaychain = create_essay_chain()


# 流式生成作文 (HTTP)
@router.get("/streaming")
def streaming_endpoint(current_user: CurrentUser, topic: str, length: int = 500):
    # 异步生成器
    async def generate():
        async for chunk in essaychain.astream({"topic": topic, "length": length}):
            yield chunk.content  # 逐步返回生成内容

    return StreamingResponse(generate(), media_type="text/plain")


# 一次性生成作文 (HTTP)
@router.get("/generate", response_model=ApiResponse[str])
async def generate_once(
    current_user: CurrentUser,
    topic: str,
    length: int = 500,
)->ApiResponse[str]:
    # 生成完整内容
    result = await essaychain.ainvoke({"topic": topic, "length": length})
    return ApiResponse(code=200, data=result.content)


# 获取llm服务可用次数
@router.get("/llmAvailable")
def get_llm_available(current_user: CurrentUser)->ApiResponse[int]:
    return ApiResponse(data=current_user.llm_avaiable)