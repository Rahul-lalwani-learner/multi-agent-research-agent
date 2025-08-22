from core.vector_store import vector_store_manager

def delete_all_vector_store():
    """Delete all documents from the vector store."""
    try:
        if not vector_store_manager.chroma_client:
            vector_store_manager._initialize_chroma()
        collection = vector_store_manager.chroma_client.get_collection(vector_store_manager.collection_name)
        all_ids = collection.get()["ids"]
        if all_ids:
            collection.delete(ids=all_ids)
        return True
    except Exception as e:
        print(f"Error deleting all vector store data: {e}")
        return False
