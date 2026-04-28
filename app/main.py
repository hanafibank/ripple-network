from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.ripple import router as ripple_router
from app.core.config import get_settings

settings = get_settings()

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


@app.get("/")
def health_check():
    return {
        "service": settings.app_name,
        "status": "ok",
        "network": "XRPL Testnet",
        "note": "XRPL testnet API is running.",
    }
