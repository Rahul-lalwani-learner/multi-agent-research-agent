import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.arxiv_fetcher import fetch_and_store
from core.user_manager import user_manager
from utils.logger import logger


def show_fetch_arxiv_page():
    st.header("📥 Fetch Papers from ArXiv")
    st.markdown("---")
    
    # Show current user info
    user_id = user_manager.get_current_user_id()
    username = user_manager.get_current_username()
    if username:
        st.info(f"📥 Fetching papers for: **{username}** (ID: `{user_id[:8]}...`)")
    else:
        st.info(f"📥 User ID: `{user_id[:8]}...`")

    query = st.text_input("Search Query", placeholder="e.g., 'large language models' OR 'transformers'")
    if query:
        st.warning("⚠️ The more results you choose, the more time it will take to fetch and process them.")
    top_k = st.slider("Max results", 1, 50, 10)
    embed_abstracts = st.checkbox("Embed abstracts now (fast)", value=True)

    if st.button("Fetch & Store"):
        if not query.strip():
            st.warning("Please enter a search query")
            return
        
        with st.spinner("Fetching from ArXiv and saving to database..."):
            session: Session = SessionLocal()
            try:
                processed, embedded, titles = fetch_and_store(
                    query=query,
                    session=session,
                    top_k=top_k,
                    embed_abstracts_only=embed_abstracts,
                    user_id=user_id  # Pass user ID for isolation
                )
                st.success(f"✅ Processed {processed} papers. Embeddings added: {embedded}")
                if titles:
                    st.write("**Titles processed:**")
                    for i, t in enumerate(titles, 1):
                        st.write(f"{i}. {t}")
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"ArXiv fetch error: {e}")
            finally:
                session.close()

    st.markdown("---")
    st.info("Note: Full PDF parsing and embeddings will be available in Phase 4.")
