from utils.nacos_helper import NacosHelper
from core.config import settings

nacos_endpoint = "127.0.0.1:8848"
nacos_namespace_id = ""
nacos_group_name = "DEFAULT_GROUP"
# nacos_username = 'nacos'
# nacos_password = 'nacos'
nacos_data_id = "ai_model"
service_name = "llm-backend"
service_port = 3332
beat_interval = 30

nacos = NacosHelper(nacos_endpoint, nacos_namespace_id)
nacos.set_service(service_name, service_port, nacos_group_name)
nacos.register()

if __name__ == "__main__":
    # 初始化模板
    import uvicorn
    uvicorn.run(
        app="main:app",
        host=settings.SEVER_HOST,
        port=settings.SEVER_PORT,
        workers=4,
        reload=False if settings.ENVIRONMENT == "production" else True,
    )