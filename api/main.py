from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database import close_pool, create_pool
from api.routers import analytics, gyms, occupancy


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()
    yield
    await close_pool()


app = FastAPI(title="WF Analyzer API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(gyms.router, prefix="/api")
app.include_router(occupancy.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok"}
