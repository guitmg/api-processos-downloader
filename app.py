"""
Main FastAPI application for PJe automation.
"""

import logging
import os
from contextlib import asynccontextmanager

from api.config import settings
from api.routes import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting PJe Automation API...")

    # Ensure data directory exists
    os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)

    logger.info("API started successfully")
    yield

    # Shutdown
    logger.info("Shutting down PJe Automation API...")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory for serving downloaded files
if os.path.exists(settings.DOWNLOAD_DIR):
    app.mount("/static", StaticFiles(directory=settings.DOWNLOAD_DIR), name="static")

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["processo"])


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "PJe Automation API",
        "version": settings.API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
