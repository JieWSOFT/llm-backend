import re
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from core.config import settings

# 初始化 LangChain 的 ChatOpenAI 模型
chat_llm = ChatOpenAI(
    model=settings.MODEL,
    base_url=settings.BASE_URL,
    api_key=settings.API_KEY,
)


def parseTemplateParams(template: str):
    # 使用正则表达式提取花括号中的内容
    result = re.findall(r"\{(.*?)\}", template)
    if result:
        return result
    else:
        return []


# """"""
def create_chain(_template: str):
    template = PromptTemplate(
        input_variables=parseTemplateParams(_template), template=_template
    )
    chain = template | chat_llm
    logger.info(
        f"当前使用的LLM模型为  MODEL={settings.MODEL}  BASE_URL={settings.BASE_URL}"
    )
    return chain
