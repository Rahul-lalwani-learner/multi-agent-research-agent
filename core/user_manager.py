"""
User management and session handling for multi-user isolation
"""
import streamlit as st
import hashlib
import uuid
from typing import Optional
from utils.logger import logger


class UserManager:
    """Manages user sessions and provides user isolation for the research assistant"""
    
    def __init__(self):
        self.session_key = "user_id"
        self.username_key = "username"
    
    def get_current_user_id(self) -> str:
        """Get the current user ID from session state"""
        if self.session_key not in st.session_state:
            # Generate a new user ID if none exists
            user_id = str(uuid.uuid4())
            st.session_state[self.session_key] = user_id
            logger.info(f"Generated new user ID: {user_id}")
        
        return st.session_state[self.session_key]
    
    def get_current_username(self) -> Optional[str]:
        """Get the current username from session state"""
        return st.session_state.get(self.username_key, None)
    
    def set_username(self, username: str) -> None:
        """Set the username for the current session"""
        st.session_state[self.username_key] = username
        logger.info(f"Set username: {username}")
    
    def get_user_collection_name(self, user_id: Optional[str] = None) -> str:
        """Get the ChromaDB collection name for a specific user"""
        if user_id is None:
            user_id = self.get_current_user_id()
        
        # Create a deterministic collection name based on user ID
        # Use first 8 characters of hash for readability while ensuring uniqueness
        user_hash = hashlib.md5(user_id.encode()).hexdigest()[:8]
        return f"research_papers_user_{user_hash}"
    
    def get_user_db_filter(self, user_id: Optional[str] = None) -> str:
        """Get the user ID for database filtering"""
        if user_id is None:
            user_id = self.get_current_user_id()
        return user_id
    
    def clear_user_session(self) -> None:
        """Clear the current user session"""
        if self.session_key in st.session_state:
            del st.session_state[self.session_key]
        if self.username_key in st.session_state:
            del st.session_state[self.username_key]
        logger.info("Cleared user session")
    
    def switch_user(self, new_user_id: str, username: Optional[str] = None) -> None:
        """Switch to a different user"""
        st.session_state[self.session_key] = new_user_id
        if username:
            st.session_state[self.username_key] = username
        logger.info(f"Switched to user: {new_user_id} ({username})")


# Global user manager instance
user_manager = UserManager()
