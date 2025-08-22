from core.db import SessionLocal
from core.models import Paper, Chunk, ClusterResult, Hypothesis, ExperimentPlan

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
