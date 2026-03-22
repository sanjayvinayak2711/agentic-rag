"""
Embedding generation for documents and queries
"""

import asyncio
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.utils.logger import setup_logger
from backend.config import settings

logger = setup_logger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using sentence transformers"""
    
    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.device = settings.EMBEDDING_DEVICE
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None, 
                self.model.encode,
                text
            )
            return embedding.tolist()  # Convert numpy array to list
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                self.model.encode,
                texts
            )
            return embeddings.tolist()  # Convert numpy arrays to lists
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 0
    
    async def similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts"""
        try:
            embedding1 = await self.generate_embedding(text1)
            embedding2 = await self.generate_embedding(text2)
            
            # Calculate cosine similarity
            similarity = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            return float(similarity)
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
