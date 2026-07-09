from fastapi import APIRouter

from app.core.config import APP_NAME, APP_VERSION

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION,
    }