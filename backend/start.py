from core.config import settings

if __name__ == "__main__":
    # 初始化模板
    import uvicorn
    uvicorn.run(
        app="main:app",
        host=settings.SEVER_HOST,
        port=2132,
        workers=4,
        reload=False if settings.ENVIRONMENT == "production" else True,
    )
