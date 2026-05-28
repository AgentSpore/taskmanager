from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from foundercrisishub.api import health, crises, analytics
from foundercrisishub.core.db import init_db, get_db
from loguru import logger
import time

app = FastAPI(title="FounderCrisisHub")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.requests_served = 0
start_time = time.time()

@app.middleware("http")
async def count_requests(request, call_next):
    app.state.requests_served += 1
    response = await call_next(request)
    return response

@app.on_event("startup")
async def startup():
    await init_db()

app.include_router(health.router, prefix="/api")
app.include_router(crises.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
