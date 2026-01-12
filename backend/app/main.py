from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Nautical Gourmet Atlas API - Discover premium partners, discounts, and treasures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": settings.APP_NAME}


# Include API router with /v1 prefix
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
