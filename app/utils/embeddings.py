import os
import uuid
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
import PyPDF2
import pandas as pd
from pathlib import Path


# Cache for embedding models to avoid reloading
_embedding_model_cache: Dict[str, SentenceTransformer] = {}


def get_embedding_model(model_name: str) -> SentenceTransformer:
    """Get or create a cached embedding model."""
    if model_name not in _embedding_model_cache:
        print(f"Loading embedding model: {model_name}...")
        _embedding_model_cache[model_name] = SentenceTransformer(model_name)
        print(f"Embedding model loaded successfully")
    return _embedding_model_cache[model_name]


class EmbeddingManager:
    def __init__(self, persist_directory: str = "./data/chroma", model_name: str = "all-MiniLM-L6-v2"):
        self.persist_directory = persist_directory
        self.model_name = model_name
        self.embedding_model = get_embedding_model(model_name)
        
        # Initialize ChromaDB
        os.makedirs(persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def embed_text(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        return self.embedding_model.encode(texts).tolist()
    
    def add_documents(self, texts: List[str], metadata: List[Dict[str, Any]] = None):
        """Add documents to the vector database."""
        if metadata is None:
            metadata = [{} for _ in texts]
        
        # Generate embeddings
        embeddings = self.embed_text(texts)
        
        # Generate IDs
        ids = [str(uuid.uuid4()) for _ in texts]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadata,
            ids=ids
        )
        
        return ids
    
    def query_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Query the vector database for similar documents."""
        query_embedding = self.embed_text([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results
    
    def load_pdf(self, file_path: str) -> List[str]:
        """Extract text from PDF file."""
        texts = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        texts.append(text)
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
        
        return texts
    
    def load_txt(self, file_path: str) -> List[str]:
        """Extract text from TXT file."""
        texts = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if content.strip():
                    texts.append(content)
        except Exception as e:
            print(f"Error reading TXT {file_path}: {e}")
        
        return texts
    
    def load_csv(self, file_path: str) -> List[str]:
        """Extract text from CSV file."""
        texts = []
        try:
            df = pd.read_csv(file_path)
            # Convert each row to a string representation
            for _, row in df.iterrows():
                text = " | ".join([f"{col}: {val}" for col, val in row.items()])
                texts.append(text)
        except Exception as e:
            print(f"Error reading CSV {file_path}: {e}")
        
        return texts
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks with overlap."""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at a sentence boundary
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            
            break_point = max(last_period, last_newline)
            
            if break_point > start + chunk_size // 2:
                chunk = text[start:start + break_point + 1]
                start = start + break_point + 1 - overlap
            else:
                start = end - overlap
            
            chunks.append(chunk.strip())
        
        return [chunk for chunk in chunks if chunk.strip()]
    
    def process_document(self, file_path: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Process a document file and return text chunks."""
        file_path = Path(file_path)
        
        if file_path.suffix.lower() == '.pdf':
            texts = self.load_pdf(str(file_path))
        elif file_path.suffix.lower() == '.txt':
            texts = self.load_txt(str(file_path))
        elif file_path.suffix.lower() == '.csv':
            texts = self.load_csv(str(file_path))
        else:
            print(f"Unsupported file type: {file_path.suffix}")
            return []
        
        # Chunk all texts
        all_chunks = []
        for text in texts:
            chunks = self.chunk_text(text, chunk_size, overlap)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def load_documents_from_directory(self, directory_path: str, chunk_size: int = 1000, overlap: int = 200):
        """Load and process all documents from a directory."""
        directory = Path(directory_path)
        all_chunks = []
        metadata = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt', '.csv']:
                chunks = self.process_document(str(file_path), chunk_size, overlap)
                
                for chunk in chunks:
                    all_chunks.append(chunk)
                    metadata.append({
                        "source": str(file_path),
                        "file_type": file_path.suffix.lower(),
                        "file_name": file_path.name
                    })
        
        if all_chunks:
            self.add_documents(all_chunks, metadata)
            print(f"Added {len(all_chunks)} chunks from {len(set(m['source'] for m in metadata))} files")
        
        return len(all_chunks)
