from fastapi import FastAPI

from app.api.health import router as health_router

from app.core.config import APP_NAME, APP_VERSION
app = FastAPI(
    title=APP_NAME,
    description="Trợ lý AI dành cho cơ quan hành chính Việt Nam",
    version=APP_VERSION,
)

app.include_router(health_router)
from app.api.system import router as system_router
app.include_router(system_router)
@app.get("/")
def home():
    return {
    "project": APP_NAME,
    "status": "Running",
    "version": APP_VERSION,
    "message": "Chào mừng bạn đến với Hành Chính AI!"
}
