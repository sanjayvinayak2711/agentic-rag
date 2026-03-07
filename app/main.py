from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from fastapi.responses import FileResponse
from app.routes.query import router as query_router
from app.config import settings
=======
from .routes.query import router as query_router
from .config import settings
>>>>>>> 9b342ac18e14cbe90b7f59e18c3d2226b62c529a
import os
import webbrowser
import threading
import time


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="An agentic RAG (Retrieval-Augmented Generation) system for document Q&A"
)


# Include static files
app.mount("/static", StaticFiles(directory=settings.static_files_dir), name="static")


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(query_router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Initialize everything and open browser automatically"""
<<<<<<< HEAD
    print("Starting Agentic RAG...")
    
    # Initialize the RAG agent
    from app.services.agent import RAGAgent
    try:
        agent = RAGAgent()
        
        # Initialize database if docs directory exists
        docs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'docs')
        if os.path.exists(docs_dir):
            doc_count = agent.initialize_database(str(docs_dir))
            print(f"Database initialized with {doc_count} documents")
    except Exception as e:
        print(f"Warning: Could not initialize RAG agent - {e}")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(1.5)  # Wait 1.5 seconds for server to fully start
        try:
            webbrowser.open('http://localhost:8000')
            print("Browser opened: http://localhost:8000")
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("   Please open http://localhost:8000 manually")
=======
    print(" Starting Agentic RAG...")
    
    # Initialize the RAG agent
    from .services.agent import RAGAgent
    agent = RAGAgent()
    
    # Initialize database if docs directory exists
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'docs')
    if os.path.exists(docs_dir):
        doc_count = agent.initialize_database(str(docs_dir))
        print(f" Database initialized with {doc_count} documents")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(2)  # Wait 2 seconds for server to fully start
        try:
            webbrowser.open('http://localhost:8000')
            print(" Browser opened: http://localhost:8000")
        except Exception as e:
            print(f" Could not open browser: {e}")
>>>>>>> 9b342ac18e14cbe90b7f59e18c3d2226b62c529a
    
    # Start browser in a separate thread
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
<<<<<<< HEAD
    print("Agentic RAG is ready!")
    print("Frontend: http://localhost:8000")
    print("Backend: Running on port 8000")
=======
    print(" Agentic RAG is ready!")
    print(" Frontend: http://localhost:8000")
    print(" Backend: Running on port 8000")
>>>>>>> 9b342ac18e14cbe90b7f59e18c3d2226b62c529a


@app.get("/")
async def root():
<<<<<<< HEAD
    """Serve the main web interface"""
    index_path = os.path.join(settings.static_files_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
=======
    """Root endpoint"""
>>>>>>> 9b342ac18e14cbe90b7f59e18c3d2226b62c529a
    return {
        "message": "Agentic RAG API is running",
        "version": settings.app_version,
        "frontend": "http://localhost:8000",
        "status": "ready"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 50)
<<<<<<< HEAD
    print("Agentic RAG - One Click Start")
    print("=" * 50)
    
    try:
        # Run the server
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug
        )
    except KeyboardInterrupt:
        print("\nAgentic RAG stopped gracefully")
    except Exception as e:
        print(f"\nFailed to start Agentic RAG: {e}")
        input("Press Enter to exit...")
=======
    print(" Agentic RAG - Single File Startup")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
>>>>>>> 9b342ac18e14cbe90b7f59e18c3d2226b62c529a
