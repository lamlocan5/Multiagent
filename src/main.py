import asyncio
import uvicorn
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html
import os

from src.api.routes import agents, rag, vision, audio
from src.api.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware, TracingMiddleware
from src.config.settings import settings
from src.utils.logging import setup_global_logging

# Configure logging
setup_global_logging()

# Create FastAPI application
app = FastAPI(
    title="Multiagent System API",
    description="API for a multiagent system with specialized agents for different tasks",
    version="0.1.0",
    docs_url=None,  # Disable default docs
    redoc_url=None, # Disable default redoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TracingMiddleware)

# Create uploads directory for static files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "audio"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "images"), exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(vision.router, prefix="/api/vision", tags=["Vision"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])

# Custom documentation endpoints
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Multiagent System API Documentation",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": app.version}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"detail": f"An unexpected error occurred: {str(exc)}"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    ) 