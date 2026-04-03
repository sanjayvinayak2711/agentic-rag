"""
Query Agent - Analyzes and processes user queries
"""

import re
from typing import Dict, Any
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class QueryAgent:
    """Agent responsible for query analysis and preprocessing"""
    
    def __init__(self):
        self.query_patterns = {
            "question": r"\b(what|how|why|when|where|who|which)\b",
            "comparison": r"\b(compare|difference|versus|vs)\b",
            "definition": r"\b(define|definition|meaning|what is)\b",
            "summary": r"\b(summarize|summary|overview)\b",
            "analysis": r"\b(analyze|analysis|examine)\b"
        }
    
    async def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the user query and extract key information"""
        try:
            # Basic preprocessing
            processed_query = self._preprocess_query(query)
            
            # Query type classification
            query_type = self._classify_query(processed_query)
            
            # Extract keywords and entities
            keywords = self._extract_keywords(processed_query)
            
            # Determine intent
            intent = self._determine_intent(processed_query, query_type)
            
            # Generate search terms
            search_terms = self._generate_search_terms(processed_query, keywords)
            
            analysis_result = {
                "original_query": query,
                "processed_query": processed_query,
                "query_type": query_type,
                "keywords": keywords,
                "intent": intent,
                "search_terms": search_terms,
                "complexity": self._assess_complexity(processed_query),
                "language": self._detect_language(processed_query)
            }
            
            logger.info(f"Query analysis completed: {query_type} - {intent}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing query: {str(e)}")
            # Return basic analysis if detailed analysis fails
            return {
                "original_query": query,
                "processed_query": self._preprocess_query(query),
                "query_type": "general",
                "keywords": [],
                "intent": "search",
                "search_terms": [query],
                "complexity": "medium",
                "language": "en"
            }
    
    def _preprocess_query(self, query: str) -> str:
        """Basic query preprocessing"""
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        
        # Remove special characters but keep important punctuation
        query = re.sub(r'[^\w\s\.\?\!\,\:\;]', '', query)
        
        return query
    
    def _classify_query(self, query: str) -> str:
        """Classify the query type"""
        for query_type, pattern in self.query_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                return query_type
        return "general"
    
    def _extract_keywords(self, query: str) -> list:
        """Extract important keywords from query"""
        # Simple keyword extraction - can be enhanced with NLP libraries
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did'}
        
        words = query.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _determine_intent(self, query: str, query_type: str) -> str:
        """Determine the user's intent"""
        intent_mapping = {
            "question": "seek_information",
            "comparison": "compare_items",
            "definition": "define_concept",
            "summary": "summarize_content",
            "analysis": "analyze_topic",
            "general": "search_information"
        }
        
        return intent_mapping.get(query_type, "search_information")
    
    def _generate_search_terms(self, query: str, keywords: list) -> list:
        """Generate search terms for retrieval"""
        search_terms = [query]  # Include full query
        
        # Add individual keywords
        search_terms.extend(keywords)
        
        # Add combinations of keywords (pairs)
        for i in range(len(keywords)):
            for j in range(i + 1, min(i + 3, len(keywords))):
                search_terms.append(f"{keywords[i]} {keywords[j]}")
        
        return list(set(search_terms))  # Remove duplicates
    
    def _assess_complexity(self, query: str) -> str:
        """Assess query complexity"""
        word_count = len(query.split())
        
        if word_count <= 5:
            return "low"
        elif word_count <= 15:
            return "medium"
        else:
            return "high"
    
    def _detect_language(self, query: str) -> str:
        """Simple language detection"""
        # Basic detection - can be enhanced with proper language detection library
        if any(char in query for char in 'áéíóúñü'):
            return "es"
        elif any(char in query for char in 'àâäëïîöùûüÿç'):
            return "fr"
        elif any(char in query for char in 'äöüß'):
            return "de"
        else:
            return "en"
