import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.vector_store import vector_store_manager
from core.rag_pipeline import answer_query
from core.user_manager import user_manager
from utils.logger import logger
from utils.config import config


def show_query_papers_page():
    st.header("❓ Query Papers (RAG)")
    st.markdown("---")
    
    # Get current user
    current_user_id = user_manager.get_current_user_id()
    current_username = user_manager.get_current_username()
    
    # Show user context
    if current_username:
        st.info(f"🔍 Searching in **{current_username}'s** paper collection")
    else:
        st.info(f"🔍 Searching in your paper collection (User ID: {current_user_id[:8]}...)")

    question = st.text_input("Ask a question about your stored papers:", placeholder="e.g., What are key innovations in UNet variants?")
    k = st.slider("Top-k contexts", 1, 10, config.RETRIEVER_K)

    if st.button("Get Answer"):
        if not question.strip():
            st.warning("Please enter a question")
            return
        
        with st.spinner("Retrieving and generating answer..."):
            try:
                # Get user-specific retriever
                retriever = vector_store_manager.get_retriever(user_id=current_user_id, k=k)
                result = answer_query(question, retriever, k=k)
                
                st.subheader("Answer")
                st.write(result["answer"]) 

                st.subheader("Citations")
                for c in result["citations"]:
                    label = f"[{c['index']}] {c['title']}"
                    if c.get("arxiv_id"):
                        label += f" (arXiv:{c['arxiv_id']})"
                    if c.get("link"):
                        st.markdown(f"- {label} — [{c['link']}]({c['link']})")
                    else:
                        st.markdown(f"- {label}")

                with st.expander("Show retrieved contexts"):
                    for i, ctx in enumerate(result["contexts"], 1):
                        meta = ctx.get("metadata", {})
                        title = meta.get("title") or "Unknown Title"
                        st.markdown(f"**[{i}] {title}**")
                        st.write(ctx.get("text", ""))
                        st.markdown("---")
            except Exception as e:
                st.error(f"❌ RAG error: {e}")
                logger.error(f"RAG error for user {current_user_id}: {e}")
