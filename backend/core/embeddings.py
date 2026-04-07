"""
Embedding generation using Gemini API (lightweight, no heavy ML models)
"""

import asyncio
from typing import List
import numpy as np
import google.generativeai as genai
from backend.utils.logger import setup_logger
from backend.config import settings

logger = setup_logger(__name__)

# Configure Gemini API
def configure_gemini():
    """Configure Gemini with available API key"""
    api_keys = settings.get_api_keys("gemini")
    if api_keys:
        genai.configure(api_key=api_keys[0])
        return True
    return False

# Initialize on module load (lazy - will retry if key not available yet)
_gemini_configured = False

def ensure_gemini_configured():
    global _gemini_configured
    if not _gemini_configured:
        _gemini_configured = configure_gemini()
    return _gemini_configured


class EmbeddingGenerator:
    """Generates embeddings using Gemini API (lightweight, cloud-based)"""
    
    def __init__(self):
        self.model_name = "models/embedding-001"
        self._use_mock = not ensure_gemini_configured()
        if self._use_mock:
            logger.warning("No Gemini API key found - using mock embeddings for testing")
        else:
            logger.info(f"Embedding generator ready (Gemini API-based)")
    
    def _mock_embedding(self, text: str) -> List[float]:
        """Generate deterministic mock embedding for testing without API key"""
        # Create a deterministic 768-dim embedding based on text hash
        import hashlib
        hash_val = hashlib.md5(text.encode()).hexdigest()
        # Generate 768 dimensions from hash chunks
        embedding = []
        for i in range(0, len(hash_val), 2):
            val = int(hash_val[i:i+2], 16) / 255.0  # Normalize to 0-1
            embedding.append(val)
        # Pad to 768 dimensions
        while len(embedding) < 768:
            embedding.extend(embedding[:min(768-len(embedding), len(embedding))])
        return embedding[:768]
    
    async def generate_embedding(self, text: str, is_query: bool = False) -> List[float]:
        """Generate embedding for a single text using Gemini API or mock"""
        try:
            if self._use_mock:
                return self._mock_embedding(text)
            
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(model=self.model_name, content=text)["embedding"]
            )
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}, falling back to mock")
            return self._mock_embedding(text)
    
    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding specifically for queries"""
        return await self.generate_embedding(query, is_query=True)
    
    async def generate_document_embedding(self, text: str) -> List[float]:
        """Generate embedding specifically for documents"""
        return await self.generate_embedding(text, is_query=False)
    
    async def generate_embeddings(self, texts: List[str], is_query: bool = False) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            embeddings = []
            for text in texts:
                embedding = await self.generate_embedding(text, is_query=is_query)
                embeddings.append(embedding)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            # Return mock embeddings for all
            return [self._mock_embedding(text) for text in texts]
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings (Gemini embedding-001 is 768d)"""
        return 768
    
    async def similarity(self, text1: str, text2: str, text1_is_query: bool = False) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            embedding1 = await self.generate_embedding(text1, is_query=text1_is_query)
            embedding2 = await self.generate_embedding(text2, is_query=False)
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
