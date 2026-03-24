from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router

app = FastAPI(
    title="Rock Fragmentation Analysis API",
    description="Analyze post-blast images for particle size distribution and blast optimization",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "service": "Rock Fragmentation Analysis",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/api/v1/analyze_image",
            "/api/v1/compute_psd",
            "/api/v1/insights",
            "/api/v1/health",
        ],
    }
