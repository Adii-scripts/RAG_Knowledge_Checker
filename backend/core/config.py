"""
Configuration settings for the RAG Knowledge Base
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
import os
# Try to load .env from multiple locations
env_paths = [
    ".env",  # Current directory
    "../.env",  # Parent directory
    os.path.join(os.path.dirname(__file__), "../../.env"),  # Project root
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        break
else:
    load_dotenv()  # Fallback to default behavior


class Settings(BaseSettings):
    """Application settings"""
    
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = "gpt-3.5-turbo"  # More accessible model
    embedding_model: str = "text-embedding-ada-002"  # More accessible embedding model
    max_tokens: int = int(os.getenv("MAX_TOKENS", "2000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.1"))
    
    # Vector Database Configuration
    chroma_persist_directory: str = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    collection_name: str = "knowledge_base"
    
    # Document Processing Configuration
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "50"))
    
    # RAG Configuration
    top_k_results: int = int(os.getenv("TOP_K_RESULTS", "5"))
    similarity_threshold: float = 0.7
    
    # API Configuration
    api_title: str = "RAG Knowledge Base Search Engine"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready Knowledge-Base Search Engine with RAG capabilities"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
    
    def validate_openai_key(self) -> bool:
        """Validate OpenAI API key is present"""
        return bool(self.openai_api_key and self.openai_api_key.startswith("sk-"))


# Global settings instance
settings = Settings()

# Validate critical settings
if not settings.validate_openai_key():
    raise ValueError("Invalid or missing OpenAI API key. Please set OPENAI_API_KEY in your .env file")