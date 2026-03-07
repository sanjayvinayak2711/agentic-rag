from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import tempfile
from starlette.concurrency import run_in_threadpool
from app.services.agent import RAGAgent
from app.config import settings

router = APIRouter()

# Lazy initialization of agent
_agent = None

def get_agent() -> RAGAgent:
    """Get or create the RAG agent instance."""
    global _agent
    if _agent is None:
        _agent = RAGAgent()
    return _agent


class QueryRequest(BaseModel):
    query: str
    use_context: bool = True


class QueryResponse(BaseModel):
    query: str
    response: str
    context_used: bool
    retrieved_documents: List[Dict[str, Any]]
    sources: List[str]


class DocumentRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None


class StatsResponse(BaseModel):
    total_documents: int
    collection_name: str
    embedding_model: str


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest, agent: RAGAgent = Depends(get_agent)):
    """Query the RAG system with a user question."""
    try:
        result = agent.generate_response(request.query, request.use_context)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@router.post("/documents", response_model=Dict[str, str])
async def add_document(request: DocumentRequest, agent: RAGAgent = Depends(get_agent)):
    """Add a single document to the RAG system."""
    try:
        doc_id = agent.add_document(request.text, request.metadata)
        return {"document_id": doc_id, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")


@router.post("/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...), agent: RAGAgent = Depends(get_agent)):
    """Upload and process a document file."""
    temp_file_path = None
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Process the document in a thread pool to avoid blocking the event loop
            chunks = await run_in_threadpool(
                agent.retriever.embedding_manager.process_document,
                temp_file_path
            )
            
            if chunks:
                # Add chunks to database in a thread pool
                metadata = [{"source": file.filename, "file_type": os.path.splitext(file.filename)[1]} for _ in chunks]
                doc_ids = await run_in_threadpool(
                    agent.retriever.embedding_manager.add_documents,
                    chunks,
                    metadata
                )
                
                return {
                    "status": "success",
                    "filename": file.filename,
                    "chunks_processed": len(chunks),
                    "document_ids": doc_ids
                }
            else:
                return {"status": "error", "message": "No content could be extracted from the file"}
        
        except Exception as e:
            print(f"Error processing document {file.filename}: {e}")
            raise HTTPException(status_code=400, detail=f"Error processing document: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in upload_document: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/stats", response_model=StatsResponse)
async def get_database_stats(agent: RAGAgent = Depends(get_agent)):
    """Get statistics about the document database."""
    try:
        stats = agent.get_database_stats()
        if "error" in stats:
            raise HTTPException(status_code=500, detail=stats["error"])
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@router.post("/initialize", response_model=Dict[str, Any])
async def initialize_database(agent: RAGAgent = Depends(get_agent), docs_directory: Optional[str] = None):
    """Initialize the database with documents from the specified directory."""
    try:
        if docs_directory is None:
            docs_directory = os.path.join(os.path.dirname(__file__), "../../data/docs")
        
        doc_count = agent.initialize_database(docs_directory)
        
        return {
            "status": "success",
            "documents_processed": doc_count,
            "directory": docs_directory
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initializing database: {str(e)}")


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, agent: RAGAgent = Depends(get_agent)):
    """Delete a document from the database."""
    try:
        success = agent.retriever.delete_document(doc_id)
        if success:
            return {"status": "success", "document_id": doc_id}
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
