from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routes.query import router as query_router
from .config import settings
import os


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An agentic RAG (Retrieval-Augmented Generation) system for document Q&A"
)


@app.on_event("startup")
async def startup_event():
    """Initialize models and resources on application startup."""
    print("Starting up application...")
    
    # Pre-load embedding model to avoid slow first requests
    try:
        from .utils.embeddings import get_embedding_model
        print("Pre-loading embedding model...")
        model = get_embedding_model(settings.embedding_model)
        print("Embedding model pre-loaded successfully")
    except Exception as e:
        print(f"Warning: Could not pre-load embedding model: {e}")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(query_router, prefix="/api", tags=["query"])

# Mount static files for UI
if os.path.exists(settings.static_files_dir):
    app.mount("/static", StaticFiles(directory=settings.static_files_dir), name="static")
    
    # Serve index.html at root
    @app.get("/", include_in_schema=False)
    async def read_index():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(settings.static_files_dir, "index.html"))
else:
    @app.get("/")
    async def root():
        """Root endpoint that serves the UI."""
        return {
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "docs": "/docs",
            "ui": f"/static/index.html" if os.path.exists(settings.static_files_dir) else None
        }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
