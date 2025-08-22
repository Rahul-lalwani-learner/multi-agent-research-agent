import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain.schema import Document
from utils.config import config
from utils.logger import logger
from core.embeddings import embedding_manager
from typing import List, Dict, Any, Optional
import os

class VectorStoreManager:
    """Manages ChromaDB vector store for the research assistant"""
    
    def __init__(self):
        self.chroma_client = None
        self.vector_store = None
        self.collection_name = "research_papers"
        # Don't initialize immediately - do it lazily when needed
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client and collection"""
        if self.vector_store is not None:
            return  # Already initialized
            
        try:
            # Ensure the persist directory exists
            os.makedirs(config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
            
            # Initialize ChromaDB client with persistence
            self.chroma_client = chromadb.PersistentClient(
                path=config.CHROMA_PERSIST_DIRECTORY,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize LangChain vector store (new package)
            self.vector_store = Chroma(
                client=self.chroma_client,
                collection_name=self.collection_name,
                embedding_function=embedding_manager.get_embedding_function(),
                persist_directory=config.CHROMA_PERSIST_DIRECTORY
            )
            
            logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def add_documents(self, documents: List[Document], metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add documents to the vector store
        
        Args:
            documents: List of LangChain Document objects
            metadata_list: Optional list of metadata dictionaries
            
        Returns:
            List of document IDs
        """
        try:
            if not self.vector_store:
                self._initialize_chroma()
            
            # Add documents to vector store
            doc_ids = self.vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> List[str]:
        """
        Add text chunks to the vector store
        
        Args:
            texts: List of text strings
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        try:
            if not self.vector_store:
                self._initialize_chroma()
            
            # Add texts to vector store
            doc_ids = self.vector_store.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} text chunks to vector store")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add texts to vector store: {e}")
            raise
    
    def similarity_search(self, query: str, k: int = None, where_filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Perform similarity search
        
        Args:
            query: Search query
            k: Number of results to return (defaults to config.RETRIEVER_K)
            
        Returns:
            List of similar documents
        """
        try:
            if not self.vector_store:
                self._initialize_chroma()
            
            k = k or config.RETRIEVER_K
            # Pass through optional metadata filter if provided
            try:
                results = self.vector_store.similarity_search(query, k=k, filter=where_filter)
            except TypeError:
                # Older langchain-chroma may not support filter kw; fallback without it
                results = self.vector_store.similarity_search(query, k=k)
            
            logger.debug(f"Found {len(results)} similar documents for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    def similarity_search_with_score(self, query: str, k: int = None, where_filter: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """
        Perform similarity search with scores
        
        Args:
            query: Search query
            k: Number of results to return (defaults to config.RETRIEVER_K)
            
        Returns:
            List of (document, score) tuples
        """
        try:
            if not self.vector_store:
                self._initialize_chroma()
            
            k = k or config.RETRIEVER_K
            try:
                results = self.vector_store.similarity_search_with_score(query, k=k, filter=where_filter)
            except TypeError:
                results = self.vector_store.similarity_search_with_score(query, k=k)
            
            logger.debug(f"Found {len(results)} similar documents with scores for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search with scores: {e}")
            raise
    
    def get_retriever(self, k: int = None, search_type: str = "similarity"):
        """
        Get a retriever object for use with LangChain chains
        
        Args:
            k: Number of results to return (defaults to config.RETRIEVER_K)
            search_type: Type of search ("similarity" or "mmr")
            
        Returns:
            Retriever object
        """
        try:
            if not self.vector_store:
                self._initialize_chroma()
            
            k = k or config.RETRIEVER_K
            
            retriever = self.vector_store.as_retriever(
                search_type=search_type,
                search_kwargs={"k": k}
            )
            
            logger.debug(f"Created retriever with k={k}, search_type={search_type}")
            return retriever
            
        except Exception as e:
            logger.error(f"Failed to create retriever: {e}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """
        Delete documents by IDs
        
        Args:
            ids: List of document IDs to delete
            
        Returns:
            True if successful
        """
        try:
            if not self.vector_store:
                self._initialize_chroma()
            
            # Delete from ChromaDB collection
            collection = self.chroma_client.get_collection(self.collection_name)
            collection.delete(ids=ids)
            
            logger.info(f"Deleted {len(ids)} documents from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    def clear_test_docs(self) -> int:
        """
        Delete all documents marked as test data
        (metadata test=True OR source='test').
        
        Returns:
            Number of documents deleted
        """
        try:
            if not self.chroma_client:
                self._initialize_chroma()
            
            collection = self.chroma_client.get_collection(self.collection_name)
            where_filter = {"$or": [{"test": True}, {"source": "test"}]}
            existing = collection.get(where=where_filter)
            ids = existing.get("ids", []) if isinstance(existing, dict) else existing.ids
            if not ids:
                return 0
            collection.delete(ids=ids)
            logger.info(f"Cleared {len(ids)} test documents from vector store")
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to clear test documents: {e}")
            return 0
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            if not self.chroma_client:
                self._initialize_chroma()
            
            collection = self.chroma_client.get_collection(self.collection_name)
            count = collection.count()
            
            stats = {
                "collection_name": self.collection_name,
                "document_count": count,
                "persist_directory": config.CHROMA_PERSIST_DIRECTORY
            }
            
            logger.debug(f"Collection stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def test_vector_store(self) -> bool:
        """
        Test the vector store functionality
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Test adding a document
            test_doc = Document(
                page_content="This is a test document for vector store functionality.",
                metadata={"test": True, "paper_id": 999}
            )
            
            doc_ids = self.add_documents([test_doc])
            
            # Test similarity search
            results = self.similarity_search("test document", k=1)
            
            # Clean up test document
            self.delete_documents(doc_ids)
            
            if results and len(results) > 0:
                logger.info("Vector store test successful")
                return True
            else:
                logger.error("Vector store test failed - no results returned")
                return False
                
        except Exception as e:
            logger.error(f"Vector store test failed: {e}")
            return False

# Global vector store manager instance - lazy initialization
vector_store_manager = VectorStoreManager()
