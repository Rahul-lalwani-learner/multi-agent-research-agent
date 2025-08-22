from core.vector_store import vector_store_manager
from typing import Optional

def delete_all_vector_store():
    """Delete all documents from the vector store."""
    try:
        if not vector_store_manager.chroma_client:
            vector_store_manager._initialize_chroma()
        
        # Get all collections and delete their contents
        collections = vector_store_manager.chroma_client.list_collections()
        for collection in collections:
            try:
                all_ids = collection.get()["ids"]
                if all_ids:
                    collection.delete(ids=all_ids)
            except Exception as e:
                print(f"Error deleting from collection {collection.name}: {e}")
        return True
    except Exception as e:
        print(f"Error deleting all vector store data: {e}")
        return False

def delete_user_vector_store(user_id: str):
    """Delete all documents from a user's vector store."""
    try:
        deleted_count = vector_store_manager.clear_user_data(user_id)
        # Return True if deletion was successful (even if no data existed to delete)
        return True
    except Exception as e:
        print(f"Error deleting user vector store data for {user_id}: {e}")
        return False

def get_user_vector_stats(user_id: str):
    """Get vector store statistics for a specific user."""
    try:
        return vector_store_manager.get_collection_stats(user_id)
    except Exception as e:
        print(f"Error getting vector stats for user {user_id}: {e}")
        return {"error": str(e)}
