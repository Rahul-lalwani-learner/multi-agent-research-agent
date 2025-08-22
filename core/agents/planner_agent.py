from typing import Dict, List
from uuid import uuid4
from sqlalchemy.orm import Session
from utils.logger import logger
from core.db import SessionLocal
from core.models import Paper, ClusterResult, Hypothesis as HypothesisModel, ExperimentPlan as ExperimentPlanModel
from core.arxiv_fetcher import fetch_and_store
from .cluster_agent import ClusterAgent
from .summarizer_agent import SummarizerAgent
from .hypothesis_agent import HypothesisAgent
from .experiment_agent import ExperimentAgent
from .base_agent import Cluster, ClusterSummary, HypothesisOut, ExperimentPlanOut


class ResearchPlanner:
    def __init__(self):
        self.cluster_agent = ClusterAgent()
        self.summarizer_agent = SummarizerAgent()
        self.hypothesis_agent = HypothesisAgent()
        self.experiment_agent = ExperimentAgent()
        self.logs: List[str] = []

    def _ensure_corpus(self, session: Session, topic_query: str, top_k: int) -> None:
        existing = session.query(Paper).count()
        if existing >= top_k:
            return
        try:
            processed, embedded, _ = fetch_and_store(
                query=topic_query,
                session=session,
                top_k=top_k,
                embed_abstracts_only=True,
            )
            msg = f"Corpus ensured. processed={processed}, embedded={embedded}"
            logger.info(msg)
            self.logs.append(msg)
        except Exception as e:
            msg = f"Corpus ensure failed or partial: {e}"
            logger.warning(msg)
            self.logs.append(msg)

    def persist_all(
        self,
        session: Session,
        run_id: str,
        clusters: List[Cluster],
        hypotheses: List[HypothesisOut],
        plans: List[ExperimentPlanOut],
    ) -> None:
        # persist clusters
        for c in clusters:
            row = ClusterResult(
                run_id=run_id,
                cluster_label=c.label,
                paper_ids_csv=",".join(str(pid) for pid in c.paper_ids),
                rationale=c.rationale,
            )
            session.add(row)
        session.flush()

        # persist hypotheses
        hyp_rows: List[HypothesisModel] = []
        for h in hypotheses:
            row = HypothesisModel(
                run_id=run_id,
                text=h.text,
                supports="\n".join(h.supporting_papers),
            )
            session.add(row)
            hyp_rows.append(row)
        session.flush()

        # persist plans (no FK constraint defined; store hypothesis_id as index mapping)
        for p in plans:
            # naive map by text match
            hyp_id = None
            for hr in hyp_rows:
                if hr.text == p.hypothesis_text:
                    hyp_id = hr.id
                    break
            row = ExperimentPlanModel(
                run_id=run_id,
                hypothesis_id=hyp_id or 0,
                plan=(
                    "Steps:\n- " + "\n- ".join(p.steps) +
                    "\n\nDatasets:\n- " + "\n- ".join(p.datasets) +
                    "\n\nMetrics:\n- " + "\n- ".join(p.metrics) +
                    "\n\nRisks:\n- " + "\n- ".join(p.risks)
                ),
            )
            session.add(row)
        session.commit()

    def run_research_workflow(self, topic_query: str, k: int = 20) -> Dict:
        run_id = str(uuid4())
        session: Session = SessionLocal()
        try:
            self._ensure_corpus(session, topic_query, k)

            self.logs.append(f"Clustering {k} papers for topic '{topic_query}'")
            clusters: List[Cluster] = self.cluster_agent.run(run_id=run_id, session=session, topic=topic_query, limit=k)
            summaries: List[ClusterSummary] = self.summarizer_agent.run(run_id=run_id, session=session, clusters=clusters)
            hypotheses: List[HypothesisOut] = self.hypothesis_agent.run(run_id=run_id, summaries=summaries)
            plans: List[ExperimentPlanOut] = self.experiment_agent.run(run_id=run_id, hypotheses=hypotheses)

            self.persist_all(session, run_id, clusters, hypotheses, plans)

            return {
                "run_id": run_id,
                "clusters": [c.dict() for c in clusters],
                "summaries": [s.dict() for s in summaries],
                "hypotheses": [h.dict() for h in hypotheses],
                "plans": [p.dict() for p in plans],
                "logs": self.logs,
            }
        finally:
            session.close()
