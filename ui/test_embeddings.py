import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.embeddings import embedding_manager
from core.vector_store import vector_store_manager
from utils.logger import logger

def show_test_embeddings_page():
    st.header("🧪 Phase 2: Embeddings & Vector Store Test")
    st.markdown("---")
    
    # Test embeddings
    st.subheader("🔤 Embeddings Test")
    
    if st.button("Test Embeddings"):
        with st.spinner("Testing embeddings..."):
            try:
                success = embedding_manager.test_embedding()
                if success:
                    st.success("✅ Embeddings working correctly!")
                    
                    # Show embedding example
                    test_text = "Machine learning is a subset of artificial intelligence."
                    embedding = embedding_manager.get_embedding(test_text)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Test Text:** {test_text}")
                        st.write(f"**Embedding Dimension:** {len(embedding)}")
                    
                    with col2:
                        st.write("**First 10 values:**")
                        st.code(embedding[:10])
                        
                else:
                    st.error("❌ Embeddings test failed")
                    
            except Exception as e:
                st.error(f"❌ Embeddings error: {e}")
    
    st.markdown("---")
    
    # Test vector store
    st.subheader("🗄️ Vector Store Test")
    
    if st.button("Test Vector Store"):
        with st.spinner("Testing vector store..."):
            try:
                success = vector_store_manager.test_vector_store()
                if success:
                    st.success("✅ Vector store working correctly!")
                    
                    # Show collection stats
                    stats = vector_store_manager.get_collection_stats()
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Collection", stats.get("collection_name", "N/A"))
                    with col2:
                        st.metric("Documents", stats.get("document_count", 0))
                    with col3:
                        st.metric("Storage", stats.get("persist_directory", "N/A"))
                        
                else:
                    st.error("❌ Vector store test failed")
                    
            except Exception as e:
                st.error(f"❌ Vector store error: {e}")
    
    st.markdown("---")
    
    # Interactive test
    st.subheader("🔍 Interactive Test")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Add test documents:**")
        test_texts = [
            "Machine learning algorithms can learn patterns from data.",
            "Deep learning uses neural networks with multiple layers.",
            "Natural language processing helps computers understand text.",
            "Computer vision enables machines to interpret images."
        ]
        
        if st.button("Add Test Documents"):
            with st.spinner("Adding test documents..."):
                try:
                    from langchain.schema import Document
                    
                    documents = [
                        Document(
                            page_content=text,
                            metadata={"source": "test", "topic": "AI", "test": True}
                        ) for text in test_texts
                    ]
                    
                    doc_ids = vector_store_manager.add_documents(documents)
                    st.success(f"✅ Added {len(doc_ids)} test documents")
                    
                except Exception as e:
                    st.error(f"❌ Error adding documents: {e}")
    
    with col2:
        st.write("**Search test documents:**")
        query = st.text_input("Enter search query:", "machine learning")
        topk = st.slider("Top-k", 1, 10, 5)
        use_mmr = st.checkbox("Use MMR (diversified) retrieval", value=True)
        only_test = st.checkbox("Filter to test docs only", value=False)
        
        if st.button("Search"):
            with st.spinner("Searching..."):
                try:
                    where = {"test": True} if only_test else None
                    if use_mmr:
                        retriever = vector_store_manager.get_retriever(k=topk, search_type="mmr")
                        # Note: retriever does not support filter, so we fallback to similarity when filtering is required
                        if where is None:
                            results = retriever.get_relevant_documents(query)
                        else:
                            results = vector_store_manager.similarity_search(query, k=topk, where_filter=where)
                    else:
                        results = vector_store_manager.similarity_search(query, k=topk, where_filter=where)
                    
                    st.write(f"**Found {len(results)} results:**")
                    for i, doc in enumerate(results, 1):
                        with st.expander(f"Result {i}"):
                            st.write(f"**Content:** {doc.page_content}")
                            st.write(f"**Metadata:** {doc.metadata}")
                            
                except Exception as e:
                    st.error(f"❌ Search error: {e}")
    
    st.markdown("---")
    
    # Cleanup
    st.subheader("🧹 Cleanup")
    if st.button("Clear Test Data"):
        with st.spinner("Clearing test data..."):
            try:
                deleted = vector_store_manager.clear_test_docs()
                st.success(f"✅ Cleared {deleted} test documents")
            except Exception as e:
                st.error(f"❌ Cleanup error: {e}")
    
    st.markdown("---")
    
    # Status summary
    st.subheader("📊 Status Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            embedding_manager.test_embedding()
            st.success("✅ Embeddings")
        except:
            st.error("❌ Embeddings")
    
    with col2:
        try:
            vector_store_manager.test_vector_store()
            st.success("✅ Vector Store")
        except:
            st.error("❌ Vector Store")
    
    with col3:
        try:
            stats = vector_store_manager.get_collection_stats()
            if "error" not in stats:
                st.success("✅ ChromaDB")
            else:
                st.error("❌ ChromaDB")
        except:
            st.error("❌ ChromaDB")
