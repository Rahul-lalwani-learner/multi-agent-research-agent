from typing import List, Dict
from utils.logger import logger
from .base_agent import Cluster, ClusterSummary, get_llm
from core.db import SessionLocal
from core.models import Paper
from sqlalchemy.orm import Session


class SummarizerAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, run_id: str, session: Session, clusters: List[Cluster]) -> List[ClusterSummary]:
        if not clusters:
            return []

        summaries: List[ClusterSummary] = []
        for cl in clusters:
            # build list of representative citations from DB
            papers: List[Paper] = (
                session.query(Paper)
                .filter(Paper.id.in_(cl.paper_ids))
                .all()
            )
            paper_refs = [
                f"{p.title} (arXiv:{p.arxiv_id})" if p.arxiv_id else f"{p.title}"
                for p in papers
            ]
            context = "\n".join([f"- {ref}" for ref in paper_refs])

            system = (
                "Role: Research summarizer.\n"
                "Task: For the cluster, produce structured summary.\n"
                "Rules:\n"
                "- Output STRICT JSON object with keys: key_points (5-8), limitations (2-4), representative_papers.\n"
                "- representative_papers: list[str] formatted as 'Title (arXiv:id)' when available.\n"
                "- Do NOT include explanations outside JSON."
            )
            human = (
                f"Cluster label: {cl.label}\n"
                f"Representative titles:\n{context}\n"
                "Return only JSON."
            )
            logger.info(f"[SummarizerAgent] invoking LLM for cluster '{cl.label}' with {len(paper_refs)} reps")
            resp = self.llm.invoke([("system", system), ("human", human)])
            logger.info("[SummarizerAgent] LLM response received")
            text = resp.content if hasattr(resp, "content") else str(resp)

            import json, re
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                logger.warning("Summarizer returned no JSON; using fallback")
                summaries.append(
                    ClusterSummary(
                        cluster_label=cl.label,
                        key_points=["Summary unavailable"],
                        representative_papers=paper_refs[:5],
                        limitations=["N/A"],
                    )
                )
                continue

            data = json.loads(match.group(0))
            summaries.append(
                ClusterSummary(
                    cluster_label=cl.label,
                    key_points=data.get("key_points", [])[:8],
                    representative_papers=data.get("representative_papers", paper_refs)[:8],
                    limitations=data.get("limitations", [])[:4],
                )
            )

        return summaries


