"""
Vector store for document embeddings using ChromaDB
"""

import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from backend.utils.logger import setup_logger
from backend.config import settings

logger = setup_logger(__name__)


class VectorStore:
    """Vector store using ChromaDB for document storage and retrieval"""
    
    def __init__(self):
        self.client = None
        self.collection = None
        self.collection_name = "documents"
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize ChromaDB client"""
        try:
            logger.info("Initializing ChromaDB client")
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB client: {str(e)}")
            raise
    
    async def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]]) -> List[str]:
        """Add documents to the vector store"""
        try:
            logger.info(f"Adding {len(texts)} documents to vector store")
            
            # Generate IDs for documents
            ids = [str(uuid.uuid4()) for _ in texts]
            
            # Add documents to collection
            self.collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Successfully added {len(texts)} documents")
            return ids
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise
    
    async def similarity_search(self, query_embedding: List[float], 
                              top_k: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        try:
            logger.info(f"Performing similarity search with top_k={top_k}")
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] and results['metadatas'][0] else {}
                    distance = results['distances'][0][i] if results['distances'] and results['distances'][0] else 1.0
                    
                    # Convert distance to similarity score (cosine distance to similarity)
                    similarity = 1 - distance
                    
                    if similarity >= threshold:
                        formatted_results.append({
                            "content": doc,
                            "metadata": metadata,
                            "score": similarity,
                            "id": results['ids'][0][i] if results['ids'] and results['ids'][0] else str(uuid.uuid4())
                        })
            
            logger.info(f"Found {len(formatted_results)} similar documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {str(e)}")
            raise
    
    async def metadata_search(self, filters: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search documents by metadata filters"""
        try:
            logger.info(f"Performing metadata search with filters: {filters}")
            
            # Build where clause for ChromaDB
            where_clause = self._build_where_clause(filters)
            
            # Get documents by metadata
            results = self.collection.get(
                where=where_clause,
                limit=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents']:
                for i, doc in enumerate(results['documents']):
                    metadata = results['metadatas'][i] if results['metadatas'] else {}
                    
                    formatted_results.append({
                        "content": doc,
                        "metadata": metadata,
                        "score": 1.0,  # Default score for metadata search
                        "id": results['ids'][i] if results['ids'] else str(uuid.uuid4())
                    })
            
            logger.info(f"Found {len(formatted_results)} documents by metadata")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in metadata search: {str(e)}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID"""
        try:
            results = self.collection.get(ids=[document_id])
            
            if results['documents'] and results['documents'][0]:
                return {
                    "content": results['documents'][0],
                    "metadata": results['metadatas'][0] if results['metadatas'] else {},
                    "id": document_id
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            raise
    
    async def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete documents from the vector store"""
        try:
            logger.info(f"Deleting {len(document_ids)} documents")
            
            self.collection.delete(ids=document_ids)
            
            logger.info("Documents deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            return False
    
    async def update_document(self, document_id: str, text: str, metadata: Dict[str, Any]) -> bool:
        """Update a document in the vector store"""
        try:
            logger.info(f"Updating document {document_id}")
            
            self.collection.update(
                ids=[document_id],
                documents=[text],
                metadatas=[metadata]
            )
            
            logger.info("Document updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return False
    
    def _build_where_clause(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build ChromaDB where clause from filters"""
        where_clause = {}
        
        for key, value in filters.items():
            if isinstance(value, str):
                where_clause[key] = {"$eq": value}
            elif isinstance(value, list):
                where_clause[key] = {"$in": value}
            elif isinstance(value, dict):
                where_clause[key] = value
            else:
                where_clause[key] = {"$eq": value}
        
        return where_clause
    
    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        try:
            count = self.collection.count()
            return {
                "document_count": count,
                "chunk_count": count,
                "collection_name": self.collection_name,
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {
                "document_count": 0,
                "chunk_count": 0,
                "collection_name": self.collection_name,
                "status": "error"
            }
    
    async def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            logger.info("Clearing collection")
            
            # Delete the collection and recreate it
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing collection: {str(e)}")
            return False
