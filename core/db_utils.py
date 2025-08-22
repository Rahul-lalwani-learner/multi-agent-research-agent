from core.db import SessionLocal
from core.models import Paper, Chunk, ClusterResult, Hypothesis, ExperimentPlan
from typing import Optional

def delete_all_data():
    """Delete all data from all tables in the correct order."""
    session = SessionLocal()
    try:
        session.query(Chunk).delete()
        session.query(Paper).delete()
        session.query(ClusterResult).delete()
        session.query(Hypothesis).delete()
        session.query(ExperimentPlan).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error deleting all data: {e}")
        return False
    finally:
        session.close()

def delete_user_data(user_id: str):
    """Delete all data for a specific user from all tables in the correct order."""
    session = SessionLocal()
    try:
        session.query(Chunk).filter(Chunk.user_id == user_id).delete()
        session.query(Paper).filter(Paper.user_id == user_id).delete()
        session.query(ClusterResult).filter(ClusterResult.user_id == user_id).delete()
        session.query(Hypothesis).filter(Hypothesis.user_id == user_id).delete()
        session.query(ExperimentPlan).filter(ExperimentPlan.user_id == user_id).delete()
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error deleting user data for {user_id}: {e}")
        return False
    finally:
        session.close()

def get_user_papers(user_id: str, limit: Optional[int] = None):
    """Get all papers for a specific user."""
    session = SessionLocal()
    try:
        query = session.query(Paper).filter(Paper.user_id == user_id)
        if limit:
            query = query.limit(limit)
        return query.all()
    except Exception as e:
        print(f"Error getting papers for user {user_id}: {e}")
        return []
    finally:
        session.close()

def get_user_stats(user_id: str):
    """Get statistics for a specific user."""
    session = SessionLocal()
    try:
        stats = {
            "papers": session.query(Paper).filter(Paper.user_id == user_id).count(),
            "chunks": session.query(Chunk).filter(Chunk.user_id == user_id).count(),
            "cluster_results": session.query(ClusterResult).filter(ClusterResult.user_id == user_id).count(),
            "hypotheses": session.query(Hypothesis).filter(Hypothesis.user_id == user_id).count(),
            "experiment_plans": session.query(ExperimentPlan).filter(ExperimentPlan.user_id == user_id).count(),
        }
        return stats
    except Exception as e:
        print(f"Error getting stats for user {user_id}: {e}")
        return {}
    finally:
        session.close()
