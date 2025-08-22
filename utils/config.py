import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Google Generative AI
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # ChromaDB
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")
    
    # ArXiv
    ARXIV_MAX_RESULTS = int(os.getenv("ARXIV_MAX_RESULTS", "50"))
    
    # Embeddings
    EMBEDDING_MODEL = "models/embedding-001"
    EMBEDDING_DIMENSION = 768  # Fixed for Google's embedding-001
    
    # Text Processing
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    # LLM
    LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    LLM_RETRIES = int(os.getenv("LLM_RETRIES", "3"))
    LLM_RETRY_DELAY = float(os.getenv("LLM_RETRY_DELAY", "1.5"))
    # RAG
    RETRIEVER_K = int(os.getenv("RETRIEVER_K", "5"))
    
    # Agent Workflow
    DEFAULT_PAPER_LIMIT = int(os.getenv("DEFAULT_PAPER_LIMIT", "20"))

# Global config instance
config = Config()

def validate_config():
    """Validate that required environment variables are set"""
    missing_vars = []
    
    if not config.GOOGLE_API_KEY:
        missing_vars.append("GOOGLE_API_KEY")
    
    if not config.DATABASE_URL:
        missing_vars.append("DATABASE_URL")
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True
