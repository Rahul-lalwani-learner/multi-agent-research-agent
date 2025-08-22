import streamlit as st
import tempfile
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from core.db import SessionLocal
from core.models import Paper, Chunk
from core.vector_store import vector_store_manager
from core.pdf_parser import extract_text_chunks
from utils.logger import logger


def show_upload_paper_page():
    st.header("📄 Upload PDF → Parse → Embed")
    st.markdown("---")

    uploaded = st.file_uploader("Choose a PDF file", type=["pdf"]) 
    title_input = st.text_input("Title (optional)")
    authors_input = st.text_input("Authors (comma-separated, optional)")

    if uploaded is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        st.info(f"Uploaded PDF")
        logger.info(f"Saved temp PDF to: {tmp_path}")
        
        if st.button("Parse & Embed"):
            with st.spinner("Parsing PDF and creating embeddings..."):
                session: Session = SessionLocal()
                try:
                    # Create or reuse a Paper record (source=upload)
                    paper = Paper(
                        arxiv_id=None,
                        title=title_input or uploaded.name,
                        authors=authors_input,
                        summary=None,
                        link=None,
                        pdf_url=None,
                        source="upload",
                        ingested=False,
                        embedded=False,
                    )
                    session.add(paper)
                    session.flush()

                    # Parse and chunk
                    chunks = extract_text_chunks(tmp_path)
                    st.write(f"Detected {len(chunks)} text chunks")

                    # Store chunks in DB and embed in Chroma
                    ids = []
                    for idx, text in enumerate(chunks):
                        chunk = Chunk(
                            paper_id=paper.id,
                            order=idx,
                            text=text,
                        )
                        session.add(chunk)
                        session.flush()

                        meta = {
                            "paper_id": paper.id,
                            "arxiv_id": paper.arxiv_id,
                            "title": paper.title,
                            "order": idx,
                            "source": "upload",
                        }
                        chroma_ids = vector_store_manager.add_texts(
                            texts=[text],
                            metadatas=[meta],
                            ids=[f"paper-{paper.id}-chunk-{idx}"]
                        )
                        if chroma_ids:
                            chunk.chroma_doc_id = chroma_ids[0]
                            ids.extend(chroma_ids)

                    paper.ingested = True
                    paper.embedded = True
                    session.commit()

                    st.success(f"✅ Stored {len(chunks)} chunks and {len(ids)} embeddings for paper: {paper.title}")
                    logger.info(f"✅ Stored {len(chunks)} chunks and {len(ids)} embeddings for paper: {paper.title}")
                except Exception as e:
                    session.rollback()
                    st.error(f"❌ Upload error: {e}")
                    logger.error(f"Upload pipeline error: {e}")
                finally:
                    session.close()
                
            # Cleanup temp file
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

    st.markdown("---")
    st.info("Tip: Provide title/authors for better citations.")
