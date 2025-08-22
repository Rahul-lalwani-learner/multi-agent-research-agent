from typing import List
from .base_agent import HypothesisOut, ExperimentPlanOut, get_llm


class ExperimentAgent:
    def __init__(self):
        self.llm = get_llm()

    def run(self, run_id: str, hypotheses: List[HypothesisOut]) -> List[ExperimentPlanOut]:
        if not hypotheses:
            return []

        plans: List[ExperimentPlanOut] = []
        for h in hypotheses:
            system = (
                "Role: Experiment designer.\n"
                "Task: Create a concise, actionable plan for the hypothesis.\n"
                "Rules: Output STRICT JSON object with keys: steps (5-8), datasets (2-4), metrics (2-4), risks (2-4).\n"
                "No text outside JSON."
            )
            human = f"Hypothesis: {h.text}\nSupporting papers: {h.supporting_papers}\nReturn STRICT JSON only."
            from utils.logger import logger as _logger
            _logger.info("[ExperimentAgent] invoking LLM for plan")
            resp = self.llm.invoke([("system", system), ("human", human)])
            _logger.info("[ExperimentAgent] LLM response received")
            text = resp.content if hasattr(resp, "content") else str(resp)

            import json, re
            match = re.search(r"\{[\s\S]*\}", text)
            if not match:
                plans.append(
                    ExperimentPlanOut(
                        hypothesis_text=h.text,
                        steps=["No plan generated"], datasets=[], metrics=[], risks=[],
                    )
                )
                continue
            data = json.loads(match.group(0))
            plans.append(
                ExperimentPlanOut(
                    hypothesis_text=h.text,
                    steps=data.get("steps", [])[:8],
                    datasets=data.get("datasets", [])[:4],
                    metrics=data.get("metrics", [])[:4],
                    risks=data.get("risks", [])[:4],
                )
            )

        return plans


