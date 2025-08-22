from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class Paper(Base):
    __tablename__ = "papers"
    
    id = Column(Integer, primary_key=True)
    arxiv_id = Column(String, unique=True, index=True)        # e.g. 2401.01234
    title = Column(Text, nullable=False)
    authors = Column(Text)                                     # "A, B, C"
    summary = Column(Text)                                     # arXiv abstract
    published_at = Column(DateTime(timezone=True))
    link = Column(String)                                      # arXiv entry_id
    pdf_url = Column(String, nullable=True)
    source = Column(String, default="arxiv")                   # arxiv/upload
    ingested = Column(Boolean, default=False)                  # text parsed?
    embedded = Column(Boolean, default=False)                  # vectors done?
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chunks = relationship("Chunk", back_populates="paper", cascade="all, delete-orphan")

class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True)
    paper_id = Column(Integer, ForeignKey("papers.id"), index=True)
    order = Column(Integer)                                    # chunk order
    text = Column(Text)
    # embedding is stored in Chroma; keep a ref if desired:
    chroma_doc_id = Column(String, index=True, nullable=True)

    paper = relationship("Paper", back_populates="chunks")

class ClusterResult(Base):
    __tablename__ = "cluster_results"
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)                        # workflow run
    cluster_label = Column(String)
    paper_ids_csv = Column(Text)                               # "1,2,3"
    rationale = Column(Text)

class Hypothesis(Base):
    __tablename__ = "hypotheses"
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    text = Column(Text)                                        # hypothesis text
    supports = Column(Text)                                    # cited papers

class ExperimentPlan(Base):
    __tablename__ = "experiment_plans"
    
    id = Column(Integer, primary_key=True)
    run_id = Column(String, index=True)
    hypothesis_id = Column(Integer, index=True)
    plan = Column(Text)                                        # steps, metrics
