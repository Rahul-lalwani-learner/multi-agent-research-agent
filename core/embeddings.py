from langchain_google_genai import GoogleGenerativeAIEmbeddings
from utils.config import config
from utils.logger import logger
from typing import List, Optional
import os

class EmbeddingManager:
    """Manages Google Gemini embeddings for the research assistant"""
    
    def __init__(self):
        self.embedding_model = None
        # Don't initialize immediately - do it lazily when needed
    
    def _initialize_embeddings(self):
        """Initialize the Google Generative AI embeddings"""
        if self.embedding_model is not None:
            return  # Already initialized
            
        try:
            if not config.GOOGLE_API_KEY:
                raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
            # Set the API key for Google Generative AI
            os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
            
            # Use REST transport to avoid asyncio event loop requirements in Streamlit
            self.embedding_model = GoogleGenerativeAIEmbeddings(
                model=config.EMBEDDING_MODEL,
                task_type="retrieval_document",
                transport="rest"
            )
            
            logger.info(f"Embeddings initialized with model: {config.EMBEDDING_MODEL} (transport=rest)")
            
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text string
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            if not self.embedding_model:
                self._initialize_embeddings()
            
            embedding = self.embedding_model.embed_query(text)
            logger.debug(f"Generated embedding of dimension: {len(embedding)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple text strings
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            if not self.embedding_model:
                self._initialize_embeddings()
            
            embeddings = self.embedding_model.embed_documents(texts)
            logger.debug(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def get_embedding_function(self):
        """
        Get the embedding function for use with ChromaDB
        
        Returns:
            The embedding function object
        """
        if not self.embedding_model:
            self._initialize_embeddings()
        
        return self.embedding_model
    
    def test_embedding(self) -> bool:
        """
        Test the embedding functionality
        
        Returns:
            True if successful, False otherwise
        """
        try:
            test_text = "This is a test embedding."
            embedding = self.get_embedding(test_text)
            
            if len(embedding) == config.EMBEDDING_DIMENSION:
                logger.info("Embedding test successful")
                return True
            else:
                logger.error(f"Embedding dimension mismatch. Expected: {config.EMBEDDING_DIMENSION}, Got: {len(embedding)}")
                return False
                
        except Exception as e:
            logger.error(f"Embedding test failed: {e}")
            return False

# Global embedding manager instance - lazy initialization
embedding_manager = EmbeddingManager()
