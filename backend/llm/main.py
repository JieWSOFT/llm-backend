import re
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
import yaml
from core.config import settings
from typing import Sequence
from model import LLMTemplate

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
    input_variables = (parseTemplateParams(_template),)
    print(input_variables)
    template = PromptTemplate(input_variables=input_variables, template=_template)
    chain = template | chat_llm
    logger.info(
        f"当前使用的LLM模型为  MODEL={settings.MODEL}  BASE_URL={settings.BASE_URL}"
    )
    return chain


templates: Sequence[LLMTemplate] = []


def setTemplates(_templates: Sequence[LLMTemplate]):
    global templates
    templates = _templates


def getTemplate(type: str) -> str:
    global templates
    template: str = ""
    for temp in list(templates):
        if temp.type == type:
            template = temp.template
    return template


def load_config(content):
    yaml_config = yaml.full_load(content)
    settings.BASE_URL = yaml_config["BASE_URL"]
    settings.MODEL = yaml_config["MODEL"]
    settings.API_KEY = yaml_config["API_KEY"]


def on_config_change(args):
    content = args["raw_content"]
    load_config(content)
    logger.info(f'配置变更 当前使用的LLM模型为  MODEL={settings.MODEL}  BASE_URL={settings.BASE_URL}')
    global chat_llm
    chat_llm = ChatOpenAI(
        model=settings.MODEL,
        base_url=settings.BASE_URL,
        api_key=settings.API_KEY,
    )
