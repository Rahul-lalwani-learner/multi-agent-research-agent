from typing import List
import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.config import config
from utils.logger import logger


def extract_text(pdf_path: str) -> str:
    """Extract raw text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        texts: List[str] = []
        for page_index in range(len(doc)):
            page = doc[page_index]
            texts.append(page.get_text("text"))
        doc.close()
        return "\n".join(texts)
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        raise


def chunk_text(text: str) -> List[str]:
    """Chunk long text using RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", ", ", " "]
    )
    chunks = splitter.split_text(text)
    # Filter out tiny whitespace-only chunks
    return [c.strip() for c in chunks if c.strip()]


def extract_text_chunks(pdf_path: str) -> List[str]:
    """
    End-to-end helper: parse a PDF and return text chunks.
    """
    text = extract_text(pdf_path)
    return chunk_text(text)
