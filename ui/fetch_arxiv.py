import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.arxiv_fetcher import fetch_and_store
from utils.logger import logger


def show_fetch_arxiv_page():
    st.header("📥 Fetch Papers from ArXiv")
    st.markdown("---")

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
                    embed_abstracts_only=embed_abstracts
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
