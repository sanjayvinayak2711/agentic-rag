from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    app_name: str = "Agentic RAG"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # OpenAI Settings
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    
    # Vector Database Settings
    chroma_persist_directory: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    
    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_retrieved_docs: int = 5
    
    # UI Settings
    static_files_dir: str = "./ui"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
