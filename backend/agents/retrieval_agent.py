"""
Retrieval Agent - Handles document retrieval and similarity search
"""

from typing import List, Dict, Any
import numpy as np
from backend.utils.logger import setup_logger
from backend.core.vector_store import VectorStore
from backend.core.embeddings import EmbeddingGenerator
from backend.config import settings

logger = setup_logger(__name__)


class RetrievalAgent:
    """Agent responsible for document retrieval and similarity search"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.embedding_generator = EmbeddingGenerator()
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
        
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents based on query"""
        try:
            logger.info(f"Retrieving documents for query: {query}")
            
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Search vector store with at least 3 results
            results = await self.vector_store.similarity_search(
                query_embedding,
                top_k=max(5, top_k),  # Get more results for better matching
                threshold=0.05  # Very low threshold to get more relevant content
            )
            
            # If no results with threshold, try without threshold
            if not results:
                logger.warning("No results with threshold, trying without threshold")
                results = await self.vector_store.similarity_search(
                    query_embedding,
                    top_k=max(5, top_k),
                    threshold=0.0
                )
            
            # Process and format results
            processed_results = []
            for result in results:
                processed_result = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "score": result["score"],
                    "chunk_id": result["id"]
                }
                processed_results.append(processed_result)
            
            logger.info(f"Retrieved {len(processed_results)} documents")
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in document retrieval: {str(e)}")
            raise
    
    async def retrieve_by_metadata(self, filters: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """Retrieve documents based on metadata filters"""
        try:
            logger.info(f"Retrieving documents with metadata filters: {filters}")
            
            results = await self.vector_store.metadata_search(filters, top_k)
            
            processed_results = []
            for result in results:
                processed_result = {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "score": result.get("score", 1.0),
                    "chunk_id": result["id"]
                }
                processed_results.append(processed_result)
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Error in metadata retrieval: {str(e)}")
            raise
    
    async def hybrid_search(self, query: str, filters: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform hybrid search combining semantic and metadata search"""
        try:
            # Semantic search
            semantic_results = await self.retrieve(query, top_k)
            
            # Metadata search if filters provided
            metadata_results = []
            if filters:
                metadata_results = await self.retrieve_by_metadata(filters, top_k)
            
            # Combine and deduplicate results
            all_results = semantic_results + metadata_results
            unique_results = []
            seen_ids = set()
            
            for result in all_results:
                if result["chunk_id"] not in seen_ids:
                    unique_results.append(result)
                    seen_ids.add(result["chunk_id"])
            
            # Sort by score and return top_k
            unique_results.sort(key=lambda x: x["score"], reverse=True)
            
            return unique_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {str(e)}")
            raise
    
    async def get_document_by_id(self, document_id: str) -> Dict[str, Any]:
        """Retrieve a specific document by ID"""
        try:
            result = await self.vector_store.get_document(document_id)
            
            if result:
                return {
                    "content": result["content"],
                    "metadata": result["metadata"],
                    "chunk_id": result["id"]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving document by ID: {str(e)}")
            raise
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval statistics"""
        try:
            stats = self.vector_store.get_stats()
            return {
                "total_documents": stats.get("document_count", 0),
                "total_chunks": stats.get("chunk_count", 0),
                "index_status": "ready",
                "similarity_threshold": self.similarity_threshold
            }
        except Exception as e:
            logger.error(f"Error getting retrieval stats: {str(e)}")
            return {
                "total_documents": 0,
                "total_chunks": 0,
                "index_status": "error",
                "similarity_threshold": self.similarity_threshold
            }
