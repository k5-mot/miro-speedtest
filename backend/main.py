#!/usr/bin/env python3
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from package.api import oauth, sticky_note, users
from package.api import health, oauth, sticky_note
from package.common import get_logger, get_settings

# from package.util import get_logger, get_settings

settings = get_settings()
logger = get_logger()

app = FastAPI(
    title="Miro REST API",
    version="1.0",
    description="",
)

# app.add_middleware(
#     SessionMiddleware,
#     secret_key=os.getenv("SECRET_KEY", "very_random_secret"),
#     session_cookie="miro_session",
# )
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "https://miro.com",
        "https://miro.com/app",
        "https://miro.com/app/dashboard",
        "https://miro.com/app/board",
        "https://miro-speedtest.pages.dev",
        "https://miro-speedtest.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(health.router, tags=["Health"], prefix="/api/health")
# app.include_router(users.router, tags=["Users"], prefix="/api/users")
app.include_router(oauth.router, tags=["OAuth"], prefix="/api/oauth")
app.include_router(
    sticky_note.router, tags=["Miro", "StickyNote"], prefix="/api/miro/sticky_note"
)

if __name__ == "__main__":
    import uvicorn

    FASTAPI_HOST = os.getenv("FASTAPI_HOST", "localhost")
    FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))
    uvicorn.run(
        app="main:app",
        host=FASTAPI_HOST,
        port=FASTAPI_PORT,
        reload=True,
    )
