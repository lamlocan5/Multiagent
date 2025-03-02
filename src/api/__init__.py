from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.api.routes import rag, vision, audio, agents

app = FastAPI(
    title="Multi-Agent System API",
    description="A sophisticated multi-agent system with RAG, reasoning, vision, audio, web search, and more",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag.router, prefix="/api/rag", tags=["RAG"])
app.include_router(vision.router, prefix="/api/vision", tags=["Vision"])
app.include_router(audio.router, prefix="/api/audio", tags=["Audio"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Multi-Agent System API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
