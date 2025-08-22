import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.config import config
from utils.logger import logger
from core.agents.planner_agent import ResearchPlanner


def show_agent_workflow_page():
    st.header("🤖 Multi-Agent Workflow")
    st.markdown("---")

    topic = st.text_input("Topic / scope", placeholder="e.g., foundation models for medical imaging")
    k = st.slider("Number of papers (k)", 5, 50, config.DEFAULT_PAPER_LIMIT)

    cluster_method = st.selectbox("Cluster method", ["auto (LLM)"], index=0)

    if st.button("Run Workflow"):
        if not topic.strip():
            st.warning("Please enter a topic")
            return
        with st.spinner("Running multi-agent workflow..."):
            try:
                planner = ResearchPlanner()
                result = planner.run_research_workflow(topic_query=topic, k=k)

                st.success(f"✅ Completed run: {result['run_id']}")

                # Clusters
                st.subheader("Clusters")
                for c in result["clusters"]:
                    st.markdown(f"**{c['label']}**")
                    st.write(c.get("rationale", ""))
                    st.caption(f"Papers: {c['paper_ids']}")
                    st.markdown("---")

                # Summaries
                st.subheader("Summaries")
                for s in result["summaries"]:
                    st.markdown(f"**{s['cluster_label']}**")
                    st.markdown("- Key points:")
                    for kp in s.get("key_points", []):
                        st.markdown(f"  - {kp}")
                    st.markdown("- Limitations:")
                    for lim in s.get("limitations", []):
                        st.markdown(f"  - {lim}")
                    st.markdown("- Representative papers:")
                    for rep in s.get("representative_papers", []):
                        st.markdown(f"  - {rep}")
                    st.markdown("---")

                # Hypotheses
                st.subheader("Hypotheses")
                for h in result["hypotheses"]:
                    st.markdown(f"- {h['text']}")
                    if h.get("supporting_papers"):
                        with st.expander("Supporting papers"):
                            for sp in h["supporting_papers"]:
                                st.markdown(f"  - {sp}")

                # Experiment Plans
                st.subheader("Experiment Plans")
                for p in result["plans"]:
                    st.markdown(f"**For hypothesis:** {p['hypothesis_text']}")
                    st.markdown("- Steps:")
                    for s in p.get("steps", []):
                        st.markdown(f"  - {s}")
                    st.markdown("- Datasets:")
                    for d in p.get("datasets", []):
                        st.markdown(f"  - {d}")
                    st.markdown("- Metrics:")
                    for m in p.get("metrics", []):
                        st.markdown(f"  - {m}")
                    st.markdown("- Risks:")
                    for r in p.get("risks", []):
                        st.markdown(f"  - {r}")

                # Logs
                if result.get("logs"):
                    with st.expander("Workflow logs"):
                        for line in result["logs"]:
                            st.code(line)

            except Exception as e:
                st.error(f"❌ Workflow error: {e}")
                logger.error(f"Workflow error: {e}")


