from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from core.config import settings
# 初始化 LangChain 的 ChatOpenAI 模型
chat_llm = ChatOpenAI(
    model= settings.MODEL,
    base_url= settings.BASE_URL,
    api_key= settings.API_KEY,
)


def create_essay_chain():
    template = PromptTemplate(
        input_variables=["content", "length"],
        template="""你是一个的作文创作家。
        以下为作文要求标准：1.题意切合，结构严谨。2、感情真挚，语言流畅。3.深刻，引用的资料丰富。4.有文采，有创新。5.可以引经据典，或者使用身边的小故事去描述某一个特质。
        现在作文的大致内容是{content}，请以此内容为基础，写一篇{length}字的作文。字数不能多太多也不能太少""",
    )
    chain = template | chat_llm
    logger.info(f'当前使用的LLM模型为  MODEL={settings.MODEL}  BASE_URL={settings.BASE_URL}')
    return chain
