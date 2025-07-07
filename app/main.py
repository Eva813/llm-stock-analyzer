from dotenv import load_dotenv

load_dotenv()

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import router as v1_router
from app.configs.config import get_config
from app.utils.logger import log

config = get_config()

# Loggers.init_config(log_level=config.app.log_level) # Initialize logging configuration(If needed)

app = FastAPI(
    title=config.app.name,
    description=config.app.description,
    version=config.app.version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware with more specific settings for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "https://*.vercel.app",   # Vercel deployments
        "https://*.netlify.app",  # Netlify deployments
        "http://127.0.0.1:5500",
        "file://",  # Allow local file access for index.html
        # Add your specific frontend domain here
    ],
    allow_credentials=False,  # Set to False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


app.include_router(v1_router, prefix="/api/v1", tags=["llm-analysis"])


@app.get("/health")
def health_check() -> dict:
    """
    Health check endpoint for Cloud Run.

    Returns:
        dict: Service health status.
    """
    log.info({"event": "health_check"})
    return {"status": "ok", "service": "llm-stock-analyzer"}


@app.get("/")
def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        dict: API information.
    """
    return {
        "message": "LLM Stock Analyzer API",
        "version": config.app.version,
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1"
    }


# For local development
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", config.app.port))
    uvicorn.run(
        "app.main:app",
        host=config.app.host,
        port=port,
        reload=False,
        workers=1
    )
