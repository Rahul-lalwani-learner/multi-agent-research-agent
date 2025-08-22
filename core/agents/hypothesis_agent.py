from typing import List
from utils.logger import logger
from .base_agent import ClusterSummary, HypothesisOut, get_llm


class HypothesisAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, run_id: str, summaries: List[ClusterSummary]) -> List[HypothesisOut]:
        if not summaries:
            return []

        system = (
            "Role: Hypothesis generator.\n"
            "Task: Propose testable, falsifiable hypotheses from cluster summaries.\n"
            "Rules:\n"
            "- Output a STRICT JSON array.\n"
            "- Each object keys: text (string), supporting_papers (list[str]).\n"
            "- No prose outside JSON."
        )

        human = "\n\n".join(
            [
                f"Cluster: {s.cluster_label}\nKey points: {s.key_points}\nLimitations: {s.limitations}\nReps: {s.representative_papers}"
                for s in summaries
            ]
        )

        logger.info("[HypothesisAgent] invoking LLM for hypotheses")
        resp = self.llm.invoke([("system", system), ("human", human + "\nReturn STRICT JSON array only.")])
        logger.info("[HypothesisAgent] LLM response received")
        text = resp.content if hasattr(resp, "content") else str(resp)

        import json, re
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if not match:
            logger.warning("HypothesisAgent returned no JSON; falling back to single hypothesis")
            return [HypothesisOut(text="No hypothesis generated", supporting_papers=[])]

        data = json.loads(match.group(0))
        outs: List[HypothesisOut] = []
        for item in data:
            try:
                outs.append(HypothesisOut(**item))
            except Exception:
                continue
        return outs


