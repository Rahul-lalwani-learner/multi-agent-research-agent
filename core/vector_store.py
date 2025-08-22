__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
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
    """Manages ChromaDB vector store for the research assistant with user isolation"""
    
    def __init__(self):
        self.chroma_client = None
        self.vector_stores = {}  # Cache for user-specific vector stores
        self.default_collection_name = "research_papers"
        # Don't initialize immediately - do it lazily when needed
    
    def _initialize_chroma(self):
        """Initialize ChromaDB client"""
        if self.chroma_client is not None:
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
            
            logger.info("ChromaDB client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _get_user_vector_store(self, user_id: str) -> Chroma:
        """Get or create a user-specific vector store"""
        if not self.chroma_client:
            self._initialize_chroma()
        
        # Use user_manager to get collection name if available
        try:
            from core.user_manager import user_manager
            collection_name = user_manager.get_user_collection_name(user_id)
        except ImportError:
            # Fallback if user_manager not available
            import hashlib
            user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
            collection_name = f"research_papers_user_{user_hash}"
        
        if collection_name not in self.vector_stores:
            # Get or create collection
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine", "user_id": user_id}
            )
            
            # Initialize LangChain vector store
            vector_store = Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=embedding_manager.get_embedding_function(),
                persist_directory=config.CHROMA_PERSIST_DIRECTORY
            )
            
            self.vector_stores[collection_name] = vector_store
            logger.info(f"ChromaDB initialized with user collection: {collection_name}")
        
        return self.vector_stores[collection_name]
    
    def get_vector_store(self, user_id: Optional[str] = None) -> Chroma:
        """Get vector store for a specific user"""
        if user_id is None:
            # Try to get current user from user_manager
            try:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            except ImportError:
                raise ValueError("user_id is required when user_manager is not available")
        
        return self._get_user_vector_store(user_id)
    
    def add_documents(self, documents: List[Document], user_id: Optional[str] = None, metadata_list: Optional[List[Dict[str, Any]]] = None) -> List[str]:
        """
        Add documents to the user's vector store
        
        Args:
            documents: List of LangChain Document objects
            user_id: User ID for isolation (optional, will use current user if not provided)
            metadata_list: Optional list of metadata dictionaries
            
        Returns:
            List of document IDs
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Add user_id to metadata for each document
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            for doc in documents:
                if doc.metadata is None:
                    doc.metadata = {}
                doc.metadata["user_id"] = user_id
            
            # Add documents to vector store
            doc_ids = vector_store.add_documents(documents)
            
            logger.info(f"Added {len(documents)} documents to vector store for user {user_id}")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise
    
    def add_texts(self, texts: List[str], user_id: Optional[str] = None, metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None) -> List[str]:
        """
        Add text chunks to the user's vector store
        
        Args:
            texts: List of text strings
            user_id: User ID for isolation (optional, will use current user if not provided)
            metadatas: Optional list of metadata dictionaries
            ids: Optional list of document IDs
            
        Returns:
            List of document IDs
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Add user_id to metadata for each text
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            if metadatas is None:
                metadatas = [{"user_id": user_id} for _ in texts]
            else:
                for metadata in metadatas:
                    metadata["user_id"] = user_id
            
            # Add texts to vector store
            doc_ids = vector_store.add_texts(
                texts=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(texts)} text chunks to vector store for user {user_id}")
            return doc_ids
            
        except Exception as e:
            logger.error(f"Failed to add texts to vector store: {e}")
            raise
    
    def similarity_search(self, query: str, user_id: Optional[str] = None, k: int = None, where_filter: Optional[Dict[str, Any]] = None) -> List[Document]:
        """
        Perform similarity search for a specific user
        
        Args:
            query: Search query
            user_id: User ID for isolation (optional, will use current user if not provided)
            k: Number of results to return (defaults to config.RETRIEVER_K)
            where_filter: Additional metadata filters
            
        Returns:
            List of similar documents
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Get user_id for filtering
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            k = k or config.RETRIEVER_K
            
            # Add user_id filter to ensure user isolation
            user_filter = {"user_id": {"$eq": user_id}}
            if where_filter:
                # Combine filters using $and
                combined_filter = {"$and": [user_filter, where_filter]}
            else:
                combined_filter = user_filter
            
            # Pass through optional metadata filter if provided
            try:
                results = vector_store.similarity_search(query, k=k, filter=combined_filter)
            except TypeError:
                # Older langchain-chroma may not support filter kw; fallback without it
                results = vector_store.similarity_search(query, k=k)
                # Manual filtering if automatic filtering failed
                results = [doc for doc in results if doc.metadata.get("user_id") == user_id]
            
            logger.debug(f"Found {len(results)} similar documents for user {user_id}, query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search: {e}")
            raise
    
    def similarity_search_with_score(self, query: str, user_id: Optional[str] = None, k: int = None, where_filter: Optional[Dict[str, Any]] = None) -> List[tuple]:
        """
        Perform similarity search with scores for a specific user
        
        Args:
            query: Search query
            user_id: User ID for isolation (optional, will use current user if not provided)
            k: Number of results to return (defaults to config.RETRIEVER_K)
            where_filter: Additional metadata filters
            
        Returns:
            List of (document, score) tuples
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Get user_id for filtering
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            k = k or config.RETRIEVER_K
            
            # Add user_id filter to ensure user isolation
            user_filter = {"user_id": {"$eq": user_id}}
            if where_filter:
                combined_filter = {"$and": [user_filter, where_filter]}
            else:
                combined_filter = user_filter
            
            try:
                results = vector_store.similarity_search_with_score(query, k=k, filter=combined_filter)
            except TypeError:
                results = vector_store.similarity_search_with_score(query, k=k)
                # Manual filtering if automatic filtering failed
                results = [(doc, score) for doc, score in results if doc.metadata.get("user_id") == user_id]
            
            logger.debug(f"Found {len(results)} similar documents with scores for user {user_id}, query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Failed to perform similarity search with scores: {e}")
            raise
    
    def get_retriever(self, user_id: Optional[str] = None, k: int = None, search_type: str = "similarity"):
        """
        Get a retriever object for use with LangChain chains for a specific user
        
        Args:
            user_id: User ID for isolation (optional, will use current user if not provided)
            k: Number of results to return (defaults to config.RETRIEVER_K)
            search_type: Type of search ("similarity" or "mmr")
            
        Returns:
            Retriever object
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Get user_id for filtering
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            k = k or config.RETRIEVER_K
            
            # Create search kwargs with user filter
            search_kwargs = {
                "k": k,
                "filter": {"user_id": {"$eq": user_id}}
            }
            
            try:
                retriever = vector_store.as_retriever(
                    search_type=search_type,
                    search_kwargs=search_kwargs
                )
            except TypeError:
                # Fallback if filter not supported
                retriever = vector_store.as_retriever(
                    search_type=search_type,
                    search_kwargs={"k": k}
                )
            
            logger.debug(f"Created retriever for user {user_id} with k={k}, search_type={search_type}")
            return retriever
            
        except Exception as e:
            logger.error(f"Failed to create retriever: {e}")
            raise
    
    def delete_documents(self, ids: List[str], user_id: Optional[str] = None) -> bool:
        """
        Delete documents by IDs for a specific user
        
        Args:
            ids: List of document IDs to delete
            user_id: User ID for isolation (optional, will use current user if not provided)
            
        Returns:
            True if successful
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Get user_id for security check
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            # Get user's collection
            collection_name = None
            try:
                from core.user_manager import user_manager
                collection_name = user_manager.get_user_collection_name(user_id)
            except ImportError:
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
                collection_name = f"research_papers_user_{user_hash}"
            
            # Delete from ChromaDB collection
            collection = self.chroma_client.get_collection(collection_name)
            collection.delete(ids=ids)
            
            logger.info(f"Deleted {len(ids)} documents from vector store for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False
    
    def clear_user_data(self, user_id: Optional[str] = None) -> int:
        """
        Delete all documents for a specific user
        
        Args:
            user_id: User ID for isolation (optional, will use current user if not provided)
            
        Returns:
            Number of documents deleted
        """
        try:
            # Get user_id
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            # Get user's collection name
            try:
                from core.user_manager import user_manager
                collection_name = user_manager.get_user_collection_name(user_id)
            except ImportError:
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
                collection_name = f"research_papers_user_{user_hash}"
            
            if not self.chroma_client:
                self._initialize_chroma()
            
            try:
                collection = self.chroma_client.get_collection(collection_name)
                existing = collection.get()
                ids = existing.get("ids", []) if isinstance(existing, dict) else existing.ids
                if ids:
                    collection.delete(ids=ids)
                    logger.info(f"Cleared {len(ids)} documents from vector store for user {user_id}")
                    return len(ids)
                else:
                    logger.info(f"No documents to clear from vector store for user {user_id}")
                    return 0
            except Exception as collection_error:
                # Collection doesn't exist or is empty - this is fine
                logger.info(f"No collection found for user {user_id} - nothing to clear")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to clear user data: {e}")
            return 0
            return 0
    
    def clear_test_docs(self, user_id: Optional[str] = None) -> int:
        """
        Delete all documents marked as test data for a specific user
        (metadata test=True OR source='test').
        
        Args:
            user_id: User ID for isolation (optional, will use current user if not provided)
            
        Returns:
            Number of documents deleted
        """
        try:
            vector_store = self.get_vector_store(user_id)
            
            # Get user_id
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            # Get user's collection name
            try:
                from core.user_manager import user_manager
                collection_name = user_manager.get_user_collection_name(user_id)
            except ImportError:
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
                collection_name = f"research_papers_user_{user_hash}"
            
            collection = self.chroma_client.get_collection(collection_name)
            where_filter = {
                "$and": [
                    {"user_id": {"$eq": user_id}},
                    {"$or": [{"test": True}, {"source": "test"}]}
                ]
            }
            existing = collection.get(where=where_filter)
            ids = existing.get("ids", []) if isinstance(existing, dict) else existing.ids
            if not ids:
                return 0
            collection.delete(ids=ids)
            logger.info(f"Cleared {len(ids)} test documents from vector store for user {user_id}")
            return len(ids)
        except Exception as e:
            logger.error(f"Failed to clear test documents: {e}")
            return 0
    
    def get_collection_stats(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about the user's vector store collection
        
        Args:
            user_id: User ID for isolation (optional, will use current user if not provided)
            
        Returns:
            Dictionary with collection statistics
        """
        try:
            # Get user_id
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            # Get user's collection name
            try:
                from core.user_manager import user_manager
                collection_name = user_manager.get_user_collection_name(user_id)
            except ImportError:
                import hashlib
                user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
                collection_name = f"research_papers_user_{user_hash}"
            
            if not self.chroma_client:
                self._initialize_chroma()
            
            try:
                collection = self.chroma_client.get_collection(collection_name)
                count = collection.count()
                
                stats = {
                    "collection_name": collection_name,
                    "user_id": user_id,
                    "document_count": count,
                    "persist_directory": config.CHROMA_PERSIST_DIRECTORY
                }
            except Exception:
                # Collection doesn't exist
                stats = {
                    "collection_name": collection_name,
                    "user_id": user_id,
                    "document_count": 0,
                    "persist_directory": config.CHROMA_PERSIST_DIRECTORY
                }
            
            logger.debug(f"Collection stats for user {user_id}: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def test_vector_store(self, user_id: Optional[str] = None) -> bool:
        """
        Test the vector store functionality for a specific user
        
        Args:
            user_id: User ID for isolation (optional, will use current user if not provided)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user_id
            if user_id is None:
                from core.user_manager import user_manager
                user_id = user_manager.get_current_user_id()
            
            # Test adding a document
            test_doc = Document(
                page_content="This is a test document for vector store functionality.",
                metadata={"test": True, "paper_id": 999, "user_id": user_id}
            )
            
            doc_ids = self.add_documents([test_doc], user_id=user_id)
            
            # Test similarity search
            results = self.similarity_search("test document", user_id=user_id, k=1)
            
            # Clean up test document
            self.delete_documents(doc_ids, user_id=user_id)
            
            if results and len(results) > 0:
                logger.info(f"Vector store test successful for user {user_id}")
                return True
            else:
                logger.error(f"Vector store test failed for user {user_id} - no results returned")
                return False
                
        except Exception as e:
            logger.error(f"Vector store test failed for user {user_id}: {e}")
            return False

# Global vector store manager instance - lazy initialization
vector_store_manager = VectorStoreManager()
