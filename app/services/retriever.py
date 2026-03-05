from typing import List, Dict, Any, Optional
import os
from ..utils.embeddings import EmbeddingManager
from ..config import settings


class DocumentRetriever:
    def __init__(self):
        self.embedding_manager = EmbeddingManager(
            persist_directory=settings.chroma_persist_directory,
            model_name=settings.embedding_model
        )
        self.max_retrieved_docs = settings.max_retrieved_docs
    
    def initialize_database(self, docs_directory: str = None):
        """Initialize the vector database with documents from the specified directory."""
        if docs_directory is None:
            docs_directory = os.path.join(os.path.dirname(__file__), "../../data/docs")
        
        if not os.path.exists(docs_directory):
            print(f"Documents directory not found: {docs_directory}")
            return 0
        
        return self.embedding_manager.load_documents_from_directory(
            docs_directory,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap
        )
    
    def retrieve_documents(self, query: str, n_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a given query."""
        if n_results is None:
            n_results = self.max_retrieved_docs
        
        results = self.embedding_manager.query_documents(query, n_results)
        
        # Format results
        retrieved_docs = []
        if results and 'documents' in results and results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                metadata = results['metadatas'][0][i] if results['metadatas'] and i < len(results['metadatas'][0]) else {}
                distance = results['distances'][0][i] if results['distances'] and i < len(results['distances'][0]) else 0
                
                retrieved_docs.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity_score": 1 - distance  # Convert distance to similarity
                })
        
        return retrieved_docs
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        try:
            count = self.embedding_manager.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.embedding_manager.collection.name,
                "embedding_model": self.embedding_manager.model_name
            }
        except Exception as e:
            return {"error": str(e)}
    
    def add_document(self, text: str, metadata: Dict[str, Any] = None) -> str:
        """Add a single document to the database."""
        if metadata is None:
            metadata = {}
        
        doc_ids = self.embedding_manager.add_documents([text], [metadata])
        return doc_ids[0] if doc_ids else None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the database."""
        try:
            self.embedding_manager.collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False
