from typing import List, Optional
from pydantic import BaseModel
from utils.logger import logger
from utils.config import config

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception as _e:
    ChatGoogleGenerativeAI = None  # type: ignore


class Cluster(BaseModel):
    label: str
    paper_ids: List[int]
    rationale: str


class ClusterSummary(BaseModel):
    cluster_label: str
    key_points: List[str]
    representative_papers: List[str]  # "Title (arXiv:id)"
    limitations: List[str]


class HypothesisOut(BaseModel):
    text: str
    supporting_papers: List[str]  # "Title (arXiv:id)"


class ExperimentPlanOut(BaseModel):
    hypothesis_text: str
    steps: List[str]
    datasets: List[str]
    metrics: List[str]
    risks: List[str]


def get_llm(model: str = config.LLM_MODEL):
    """Shared helper to get a Gemini chat LLM for .invoke() calls."""
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError("langchain-google-genai not available")
    llm = ChatGoogleGenerativeAI(model=model, temperature=0.2, transport="rest")
    logger.debug(f"Initialized LLM: {model}")
    return llm


