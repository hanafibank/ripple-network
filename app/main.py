from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.ripple import router as ripple_router
from app.core.config import get_settings

settings = get_settings()
WEB_DIR = Path(__file__).resolve().parent / "web"

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="XRPL testnet API for wallet creation, XRP transfers, and transaction lookup.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ripple_router)

if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


@app.get("/ui")
def ui():
    index_path = WEB_DIR / "index.html"
    if not index_path.exists():
        return {"error": "UI assets not found."}
    return FileResponse(index_path)


@app.get("/")
def health_check():
    return {
        "service": settings.app_name,
        "status": "ok",
        "network": "XRPL Testnet",
        "note": "XRPL testnet API is running.",
    }
