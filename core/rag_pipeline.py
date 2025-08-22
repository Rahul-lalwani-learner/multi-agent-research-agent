from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config import config
from utils.logger import logger
import os


def _format_contexts(contexts) -> str:
    formatted: List[str] = []
    for i, doc in enumerate(contexts, 1):
        meta = doc.metadata or {}
        title = meta.get("title") or "Unknown Title"
        arxiv_id = meta.get("arxiv_id") or "N/A"
        source = meta.get("source") or ""
        prefix = f"[{i}] {title} (arXiv:{arxiv_id})"
        formatted.append(prefix + "\n" + doc.page_content)
    return "\n\n".join(formatted)


def _build_llm() -> ChatGoogleGenerativeAI:
    if not config.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is required for RAG")
    os.environ["GOOGLE_API_KEY"] = config.GOOGLE_API_KEY
    # Use REST transport to avoid asyncio loop issues in Streamlit
    # Changed the model to gemini-2.5-flash
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2, transport="rest")


def answer_query(question: str, retriever=None, user_id: str = None, k: int = None) -> Dict[str, Any]:
    """
    Run retrieval-augmented generation over the stored corpus.
    
    Args:
        question: The user's question
        retriever: Optional retriever object (if not provided, will create user-specific retriever)
        user_id: User ID for isolation (optional, will use current user if not provided)
        k: Number of documents to retrieve
        
    Returns a dict: { answer, citations: [{title, arxiv_id, link}], contexts }
    """
    k = k or config.RETRIEVER_K

    # If no retriever provided, create a user-specific one
    if retriever is None:
        from core.vector_store import vector_store_manager
        retriever = vector_store_manager.get_retriever(user_id=user_id, k=k)

    # Retrieve top-k documents
    contexts = retriever.invoke(question)

    # Build prompt
    context_text = _format_contexts(contexts)
    system = (
        "You are a precise research assistant. Answer the user's question using the provided context only. "
        "Cite specific papers as [n] with title and arXiv id. If the answer is not in the context, say you don't know."
    )
    user = (
        f"Question:\n{question}\n\n"
        f"Context:\n{context_text}\n\n"
        "Instructions: Provide a concise answer followed by a bullet list of citations as \"[n] Title (arXiv:id)\"."
    )

    llm = _build_llm()
    resp = llm.invoke([{"role": "system", "content": system}, {"role": "user", "content": user}])
    answer_text = resp.content if hasattr(resp, "content") else str(resp)

    # Extract citations list from metadata of retrieved docs
    citations: List[Dict[str, str]] = []
    for i, doc in enumerate(contexts, 1):
        meta = doc.metadata or {}
        citations.append({
            "index": i,
            "title": meta.get("title") or "Unknown Title",
            "arxiv_id": meta.get("arxiv_id") or "",
            "link": meta.get("link") or (f"https://arxiv.org/abs/{meta.get('arxiv_id')}" if meta.get("arxiv_id") else ""),
        })

    return {
        "answer": answer_text,
        "citations": citations,
        "contexts": [{"text": d.page_content, "metadata": d.metadata} for d in contexts],
    }
