import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from routes import router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up...")
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Papers Please API",
    description="API for managing academic papers from arXiv",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router, prefix="/api")  # All routes will be under /api/v1

@app.get("/")
async def root():
    return {
        "message": "Papers Please API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": "/api/"
    }

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
