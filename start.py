from core.config import settings

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app="main:app",
        host=settings.SEVER_HOST,
        port=settings.SEVER_PORT,
        reload=True,
    )
