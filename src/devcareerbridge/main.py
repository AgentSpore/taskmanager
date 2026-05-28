from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from starlette.requests import Request
from devcareerbridge.api import health
from devcareerbridge.core import config, db
from devcareerbridge.core.db import get_db, init_db

middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]),
]

app = FastAPI(title="DevCareerBridge", middleware=middleware)

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.middleware("http")
async def request_counter(request: Request, call_next):
    if not hasattr(app.state, "requests_served"):
        app.state.requests_served = 0
    app.state.requests_served += 1
    response = await call_next(request)
    return response

app.include_router(health.router, prefix="/api")
# Domain routers would be added here, e.g., app.include_router(user.router, prefix="/api/users")
