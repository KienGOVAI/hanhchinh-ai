from fastapi import APIRouter

from app.core.settings import get_app_info

router = APIRouter()


@router.get("/system")
def system():
    return get_app_info()