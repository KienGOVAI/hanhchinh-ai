from fastapi import FastAPI

app = FastAPI(
    title="Hành Chính AI",
    description="Trợ lý AI dành cho cơ quan hành chính Việt Nam",
    version="0.0.1"
)


@app.get("/")
def home():
    return {
        "project": "Hành Chính AI",
        "status": "Running",
        "version": "0.0.1",
        "message": "Chào mừng bạn đến với Hành Chính AI!"
    }