from typing import List, Tuple, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from langchain_community.utilities import ArxivAPIWrapper
from langchain.schema import Document

from utils.logger import logger
from utils.config import config
from core.db import SessionLocal
from core.models import Paper, Chunk
from core.vector_store import vector_store_manager


def _safe_get(meta: dict, keys: List[str], default=None):
    for k in keys:
        if k in meta and meta[k] is not None:
            return meta[k]
    return default


def _extract_arxiv_fields(doc: Document) -> dict:
    meta = doc.metadata or {}
    entry_id = _safe_get(meta, ["entry_id", "Entry ID", "id", "link"], "")
    arxiv_id = None
    if entry_id:
        try:
            tail = entry_id.split("/abs/")[-1]
            arxiv_id = tail.replace("v", "v").split("v")[0] if "v" in tail else tail
        except Exception:
            arxiv_id = entry_id

    published = _safe_get(meta, ["Published", "published", "published_at"]) or None
    if isinstance(published, str):
        try:
            published = datetime.fromisoformat(published.replace("Z", "+00:00"))
        except Exception:
            published = None

    title = _safe_get(meta, ["Title", "title"]) or doc.page_content[:120]
    authors = _safe_get(meta, ["Authors", "authors"]) or ""
    summary = _safe_get(meta, ["Summary", "summary"]) or doc.page_content
    link = entry_id

    pdf_url = _safe_get(meta, ["pdf_url", "PdfUrl"]) or None
    if not pdf_url:
        try:
            links = _safe_get(meta, ["links"]) or []
            for l in links:
                if isinstance(l, dict) and l.get("type") == "application/pdf":
                    pdf_url = l.get("href")
                    break
        except Exception:
            pdf_url = None

    return {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": ", ".join(authors) if isinstance(authors, list) else authors,
        "summary": summary,
        "published_at": published,
        "link": link,
        "pdf_url": pdf_url,
    }


def fetch_from_arxiv(query: str, top_k: int) -> List[Document]:
    # Ensure arXiv API is asked for exactly top_k results
    wrapper = ArxivAPIWrapper(
        load_max_docs=top_k,
        top_k_results=top_k,
    )
    logger.info(f"Fetching up to {top_k} papers from arXiv for query: {query}")
    docs = wrapper.load(query)
    # Safety slice in case provider returns more
    docs = docs[:top_k]
    logger.info(f"Fetched {len(docs)} papers from arXiv")
    return docs


def upsert_paper(session: Session, fields: dict, user_id: str) -> Tuple[Paper, bool]:
    arxiv_id = fields.get("arxiv_id")
    paper = None
    created = False
    if arxiv_id:
        # Check for existing paper for this user and arxiv_id
        paper = session.query(Paper).filter(
            Paper.arxiv_id == arxiv_id,
            Paper.user_id == user_id
        ).one_or_none()
    if paper is None:
        paper = Paper(
            user_id=user_id,  # Add user_id for isolation
            arxiv_id=arxiv_id,
            title=fields.get("title", "Untitled"),
            authors=fields.get("authors", ""),
            summary=fields.get("summary", ""),
            published_at=fields.get("published_at"),
            link=fields.get("link"),
            pdf_url=fields.get("pdf_url"),
            source="arxiv",
        )
        session.add(paper)
        session.flush()
        created = True
    else:
        paper.title = fields.get("title", paper.title)
        paper.authors = fields.get("authors", paper.authors)
        paper.summary = fields.get("summary", paper.summary)
        paper.published_at = fields.get("published_at", paper.published_at)
        paper.link = fields.get("link", paper.link)
        paper.pdf_url = fields.get("pdf_url", paper.pdf_url)
    return paper, created


def embed_abstract(session: Session, paper: Paper, user_id: str) -> Optional[str]:
    if not paper.summary:
        return None
    # Create a chunk record for the abstract
    chunk = Chunk(
        user_id=user_id,  # Add user_id for isolation
        paper_id=paper.id,
        order=0,
        text=paper.summary,
    )
    session.add(chunk)
    session.flush()

    meta = {
        "user_id": user_id,  # Add user_id to metadata
        "paper_id": paper.id,
        "arxiv_id": paper.arxiv_id,
        "title": paper.title,
        "order": 0,
        "source": "arxiv",
    }
    ids = vector_store_manager.add_texts(
        texts=[paper.summary], 
        metadatas=[meta], 
        ids=[f"paper-{paper.id}-abs"],
        user_id=user_id  # Pass user_id to vector store
    )
    if ids and len(ids) > 0:
        chunk.chroma_doc_id = ids[0]
    paper.ingested = True
    paper.embedded = True
    return chunk.chroma_doc_id


def fetch_and_store(query: str, session: Session, top_k: int = 10, embed_abstracts_only: bool = True, user_id: str = None) -> Tuple[int, int, List[str]]:
    """
    Fetch papers from arXiv and upsert into DB. Optionally embed abstracts now.

    Args:
        query: Search query for arXiv
        session: Database session
        top_k: Maximum number of papers to fetch
        embed_abstracts_only: Whether to embed abstracts immediately
        user_id: User ID for isolation (required)

    Returns:
        (num_processed, num_embeddings_added, titles)
    """
    if user_id is None:
        raise ValueError("user_id is required for user isolation")
    
    docs = fetch_from_arxiv(query, top_k)
    processed = 0
    embedded = 0
    titles: List[str] = []
    for doc in docs:
        try:
            fields = _extract_arxiv_fields(doc)
            paper, created = upsert_paper(session, fields, user_id)
            session.commit()
            processed += 1
            titles.append(paper.title)

            if embed_abstracts_only and paper.summary:
                # Avoid re-embedding duplicates
                if not paper.embedded:
                    embed_abstract(session, paper, user_id)
                    session.commit()
                    embedded += 1
        except Exception as e:
            session.rollback()
            logger.error(f"Failed processing a paper: {e}")
            continue

    logger.info(f"Processed {processed} papers; embedded {embedded} abstracts for user {user_id}.")
    return processed, embedded, titles
