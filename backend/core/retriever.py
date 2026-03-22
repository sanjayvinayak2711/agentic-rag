"""
Retriever component for document retrieval and ranking
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from backend.utils.logger import setup_logger
from backend.core.embeddings import EmbeddingGenerator
from backend.core.vector_store import VectorStore

logger = setup_logger(__name__)


class Retriever:
    """Advanced retriever with multiple retrieval strategies"""
    
    def __init__(self):
        self.embedding_generator = EmbeddingGenerator()
        self.vector_store = VectorStore()
        
    async def retrieve(self, query: str, strategy: str = "hybrid", 
                      top_k: int = 5, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Retrieve documents using specified strategy"""
        try:
            logger.info(f"Retrieving documents using {strategy} strategy")
            
            if strategy == "semantic":
                return await self._semantic_retrieval(query, top_k)
            elif strategy == "keyword":
                return await self._keyword_retrieval(query, top_k, filters)
            elif strategy == "hybrid":
                return await self._hybrid_retrieval(query, top_k, filters)
            else:
                raise ValueError(f"Unknown retrieval strategy: {strategy}")
                
        except Exception as e:
            logger.error(f"Error in retrieval: {str(e)}")
            raise
    
    async def _semantic_retrieval(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Semantic retrieval using embeddings"""
        try:
            # Generate query embedding
            query_embedding = await self.embedding_generator.generate_embedding(query)
            
            # Search vector store
            results = await self.vector_store.similarity_search(
                query_embedding.tolist(),
                top_k=top_k
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic retrieval: {str(e)}")
            raise
    
    async def _keyword_retrieval(self, query: str, top_k: int, 
                               filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Keyword-based retrieval"""
        try:
            # Extract keywords from query
            keywords = self._extract_keywords(query)
            
            # Build metadata filters for keyword search
            if not filters:
                filters = {}
            
            # Search in content (this is a simplified approach)
            # In practice, you might want to use a full-text search engine
            all_docs = await self.vector_store.metadata_search(filters, top_k * 2)
            
            # Score documents based on keyword matches
            scored_docs = []
            for doc in all_docs:
                score = self._calculate_keyword_score(doc["content"], keywords)
                if score > 0:
                    doc["score"] = score
                    scored_docs.append(doc)
            
            # Sort by score and return top_k
            scored_docs.sort(key=lambda x: x["score"], reverse=True)
            return scored_docs[:top_k]
            
        except Exception as e:
            logger.error(f"Error in keyword retrieval: {str(e)}")
            raise
    
    async def _hybrid_retrieval(self, query: str, top_k: int, 
                              filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Hybrid retrieval combining semantic and keyword approaches"""
        try:
            # Get semantic results
            semantic_results = await self._semantic_retrieval(query, top_k)
            
            # Get keyword results
            keyword_results = await self._keyword_retrieval(query, top_k, filters)
            
            # Combine and re-score results
            combined_results = self._combine_results(semantic_results, keyword_results)
            
            # Return top_k results
            return combined_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error in hybrid retrieval: {str(e)}")
            raise
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        # Simple keyword extraction
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'}
        
        words = query.lower().split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _calculate_keyword_score(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword matching score"""
        content_lower = content.lower()
        score = 0.0
        
        for keyword in keywords:
            if keyword in content_lower:
                # Count occurrences
                occurrences = content_lower.count(keyword)
                score += occurrences * 0.1
        
        return score
    
    def _combine_results(self, semantic_results: List[Dict[str, Any]], 
                        keyword_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine and re-score results from different retrieval methods"""
        combined = {}
        
        # Add semantic results
        for result in semantic_results:
            doc_id = result["id"]
            combined[doc_id] = result.copy()
            combined[doc_id]["semantic_score"] = result["score"]
            combined[doc_id]["keyword_score"] = 0.0
        
        # Add keyword results
        for result in keyword_results:
            doc_id = result["id"]
            if doc_id in combined:
                combined[doc_id]["keyword_score"] = result["score"]
            else:
                combined[doc_id] = result.copy()
                combined[doc_id]["semantic_score"] = 0.0
                combined[doc_id]["keyword_score"] = result["score"]
        
        # Calculate combined score
        for doc_id, doc in combined.items():
            # Weighted combination (semantic: 0.7, keyword: 0.3)
            combined_score = (doc["semantic_score"] * 0.7 + doc["keyword_score"] * 0.3)
            doc["score"] = combined_score
        
        # Convert back to list and sort
        results = list(combined.values())
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    async def rerank_results(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Re-rank retrieval results based on query relevance"""
        try:
            if not results:
                return results
            
            # Calculate relevance scores for each result
            for result in results:
                relevance_score = await self._calculate_relevance(query, result)
                result["relevance_score"] = relevance_score
            
            # Sort by relevance score
            results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in reranking: {str(e)}")
            return results
    
    async def _calculate_relevance(self, query: str, result: Dict[str, Any]) -> float:
        """Calculate relevance score for a single result"""
        try:
            content = result["content"]
            
            # Semantic similarity
            semantic_sim = await self.embedding_generator.similarity(query, content)
            
            # Keyword overlap
            query_words = set(query.lower().split())
            content_words = set(content.lower().split())
            keyword_overlap = len(query_words.intersection(content_words)) / len(query_words) if query_words else 0
            
            # Combined relevance score
            relevance = semantic_sim * 0.7 + keyword_overlap * 0.3
            
            return relevance
            
        except Exception as e:
            logger.error(f"Error calculating relevance: {str(e)}")
            return 0.0
