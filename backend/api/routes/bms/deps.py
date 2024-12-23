from fastapi import Depends, HTTPException, Request
from loguru import logger


ALLOWED_REFERER = "http://192.168.2.197:3333"


async def check_referer(request: Request):
    referer = request.headers.get("referer") or request.headers.get("origin")
    logger.info(referer, ALLOWED_REFERER, referer != ALLOWED_REFERER)
    if referer != ALLOWED_REFERER:
        raise HTTPException(status_code=403, detail="Access forbidden from this source")


checkReferer = Depends(check_referer)
