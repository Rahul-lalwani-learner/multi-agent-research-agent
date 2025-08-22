"""
Database migration script to add user isolation to existing data
"""
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from core.db import engine, SessionLocal
from core.models import Paper, Chunk, ClusterResult, Hypothesis, ExperimentPlan
from utils.logger import logger
import uuid

def run_migration():
    """Run database migration to add user_id columns and migrate existing data"""
    
    logger.info("Starting database migration for user isolation...")
    
    session = SessionLocal()
    
    try:
        # Check if user_id columns already exist
        with engine.connect() as conn:
            # Check papers table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'papers' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                logger.info("Adding user_id column to papers table...")
                conn.execute(text("ALTER TABLE papers ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_papers_user_id ON papers(user_id)"))
                conn.commit()
                
                # Assign a default user_id to existing papers
                default_user_id = str(uuid.uuid4())
                logger.info(f"Assigning default user_id {default_user_id} to existing papers...")
                conn.execute(text("UPDATE papers SET user_id = :user_id WHERE user_id IS NULL"), 
                           {"user_id": default_user_id})
                conn.commit()
                
                # Make user_id NOT NULL after migration
                conn.execute(text("ALTER TABLE papers ALTER COLUMN user_id SET NOT NULL"))
                conn.commit()
            
            # Check chunks table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'chunks' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                logger.info("Adding user_id column to chunks table...")
                conn.execute(text("ALTER TABLE chunks ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_chunks_user_id ON chunks(user_id)"))
                conn.commit()
                
                # Update chunks with user_id from their associated papers
                conn.execute(text("""
                    UPDATE chunks 
                    SET user_id = papers.user_id 
                    FROM papers 
                    WHERE chunks.paper_id = papers.id AND chunks.user_id IS NULL
                """))
                conn.commit()
                
                # Make user_id NOT NULL after migration
                conn.execute(text("ALTER TABLE chunks ALTER COLUMN user_id SET NOT NULL"))
                conn.commit()
            
            # Check cluster_results table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'cluster_results' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                logger.info("Adding user_id column to cluster_results table...")
                conn.execute(text("ALTER TABLE cluster_results ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_cluster_results_user_id ON cluster_results(user_id)"))
                conn.commit()
                
                # Assign default user_id to existing cluster results
                conn.execute(text("UPDATE cluster_results SET user_id = :user_id WHERE user_id IS NULL"), 
                           {"user_id": default_user_id})
                conn.commit()
                
                # Make user_id NOT NULL after migration
                conn.execute(text("ALTER TABLE cluster_results ALTER COLUMN user_id SET NOT NULL"))
                conn.commit()
            
            # Check hypotheses table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'hypotheses' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                logger.info("Adding user_id column to hypotheses table...")
                conn.execute(text("ALTER TABLE hypotheses ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_hypotheses_user_id ON hypotheses(user_id)"))
                conn.commit()
                
                # Assign default user_id to existing hypotheses
                conn.execute(text("UPDATE hypotheses SET user_id = :user_id WHERE user_id IS NULL"), 
                           {"user_id": default_user_id})
                conn.commit()
                
                # Make user_id NOT NULL after migration
                conn.execute(text("ALTER TABLE hypotheses ALTER COLUMN user_id SET NOT NULL"))
                conn.commit()
            
            # Check experiment_plans table
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'experiment_plans' AND column_name = 'user_id'
            """))
            
            if not result.fetchone():
                logger.info("Adding user_id column to experiment_plans table...")
                conn.execute(text("ALTER TABLE experiment_plans ADD COLUMN user_id VARCHAR"))
                conn.execute(text("CREATE INDEX ix_experiment_plans_user_id ON experiment_plans(user_id)"))
                conn.commit()
                
                # Assign default user_id to existing experiment plans
                conn.execute(text("UPDATE experiment_plans SET user_id = :user_id WHERE user_id IS NULL"), 
                           {"user_id": default_user_id})
                conn.commit()
                
                # Make user_id NOT NULL after migration
                conn.execute(text("ALTER TABLE experiment_plans ALTER COLUMN user_id SET NOT NULL"))
                conn.commit()
            
            # Remove the old unique constraint on arxiv_id and create new composite index
            try:
                conn.execute(text("DROP INDEX IF EXISTS ix_papers_arxiv_id"))
                conn.execute(text("CREATE INDEX ix_papers_user_arxiv ON papers(user_id, arxiv_id)"))
                conn.commit()
                logger.info("Updated arxiv_id indexing for user isolation")
            except Exception as e:
                logger.warning(f"Could not update arxiv_id indexing: {e}")
        
        logger.info("Database migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    success = run_migration()
    if success:
        print("✅ Migration completed successfully!")
    else:
        print("❌ Migration failed!")
        sys.exit(1)
