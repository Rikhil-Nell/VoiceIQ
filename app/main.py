# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, logs, chat, health
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/auth")
    app.include_router(logs.router, prefix="/logs")
    app.include_router(chat.router, prefix="/chat")
    app.include_router(health.router)

    return app

app = create_app()
