from typing import List, Dict, Any, Set
from sqlalchemy.orm import Session
from utils.logger import logger
from core.models import Paper
from core.vector_store import vector_store_manager
from .base_agent import Cluster, get_llm


class ClusterAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, run_id: str, session: Session, topic: str, limit: int = 20, user_id: str = None) -> List[Cluster]:
        if user_id is None:
            raise ValueError("user_id is required for user isolation")
            
        # Prefer semantic pre-filter via Chroma to keep results on-topic
        candidate_ids: List[int] = []
        try:
            results = vector_store_manager.similarity_search(topic, user_id=user_id, k=max(limit * 3, limit))
            seen: Set[int] = set()
            for doc in results:
                meta = getattr(doc, "metadata", {}) or {}
                pid = meta.get("paper_id")
                if isinstance(pid, int) and pid not in seen:
                    seen.add(pid)
                    candidate_ids.append(pid)
            logger.debug(f"ClusterAgent semantic prefilter collected {len(candidate_ids)} paper_ids for user {user_id}")
        except Exception as e:
            logger.warning(f"ClusterAgent semantic prefilter failed: {e}")

        q = session.query(Paper).filter(Paper.title.isnot(None), Paper.user_id == user_id)
        if candidate_ids:
            q = q.filter(Paper.id.in_(candidate_ids))
        else:
            # Fallback: simple keyword filter on title/summary
            like = f"%{topic}%"
            try:
                from sqlalchemy import or_
                q = q.filter(or_(Paper.title.ilike(like), Paper.summary.ilike(like)))
            except Exception:
                pass

        papers: List[Paper] = (
            q.order_by(Paper.published_at.desc().nullslast(), Paper.id.desc())
             .limit(limit)
             .all()
        )
        if not papers:
            logger.warning("No papers available for clustering after topical filtering")
            return []

        items: List[Dict[str, Any]] = []
        for p in papers:
            items.append({
                "id": p.id,
                "arxiv_id": p.arxiv_id or "",
                "title": p.title,
                "summary": (p.summary or "")[:2000],
                "link": p.link or "",
            })

        system = (
            "Role: Research organizer.\n"
            "Task: Group provided papers (IDs and metadata) into 2-6 coherent, on-topic clusters.\n"
            "Rules:\n"
            "- Consider only on-topic items for the given topic.\n"
            "- Use titles and abstracts.\n"
            "- Output STRICT JSON array with objects having keys: label, paper_ids, rationale.\n"
            "- label: short string; paper_ids: list[int] (from provided IDs); rationale: 1-3 sentences.\n"
            "- Do NOT include any extra keys or text outside JSON."
        )
        user = {
            "topic": topic,
            "papers": items,
        }

        prompt = [
            ("system", system),
            ("human", f"Topic: {topic}\nPapers JSON:\n{items}\nReturn STRICT JSON array only. Ignore off-topic items.")
        ]

        logger.info(f"[ClusterAgent] invoking LLM for run with {len(items)} items topic='{topic}'")
        resp = self.llm.invoke(prompt)
        logger.info("[ClusterAgent] LLM response received")
        text = resp.content if hasattr(resp, "content") else str(resp)

        # Attempt to locate JSON array
        import json, re
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            logger.error("Clustering LLM did not return JSON array")
            return []
        data = json.loads(match.group(0))

        clusters: List[Cluster] = []
        for c in data:
            try:
                clusters.append(Cluster(**c))
            except Exception as e:
                logger.warning(f"Skipping bad cluster item: {e}")
        return clusters


