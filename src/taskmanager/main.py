from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .api.health import router as health_router
from .api.tasks import router as tasks_router
from .core.db import init_db
from .core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.start_time = None
    app.state.requests_served = 0
    yield

app = FastAPI(
    title="TaskManager",
    description="AI-powered task management system",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_counter(request, call_next):
    app.state.requests_served += 1
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup_event():
    await init_db()

app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(tasks_router, prefix="/api", tags=["tasks"])