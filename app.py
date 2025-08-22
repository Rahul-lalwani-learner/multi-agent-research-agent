import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import config, validate_config
from utils.logger import logger
from core.db import init_db, test_db_connection
from ui.test_embeddings import show_test_embeddings_page
from ui.fetch_arxiv import show_fetch_arxiv_page
from ui.upload_paper import show_upload_paper_page
from ui.query_papers import show_query_papers_page

# Page configuration
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🔬 Multi-Agent Research Assistant")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["🏠 Home", "🧪 Test Phase 2", "📥 Fetch ArXiv", "📄 Upload PDF", "❓ Query Papers", "🤖 Agent Workflow"]
    )
    
    # Status indicators in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Status")
    
    # Check configuration
    try:
        validate_config()
        st.sidebar.success("✅ Config Valid")
    except ValueError as e:
        st.sidebar.error(f"❌ Config Error: {e}")
        st.error("Please set up your environment variables in a .env file")
        return
    
    # Check database connection
    if test_db_connection():
        st.sidebar.success("✅ Database Connected")
    else:
        st.sidebar.error("❌ Database Error")
        st.error("Cannot connect to database. Please check your DATABASE_URL")
        return
    
    # Initialize database tables
    try:
        init_db()
        st.sidebar.success("✅ Database Initialized")
    except Exception as e:
        st.sidebar.error("❌ Database Init Failed")
        st.error(f"Failed to initialize database: {e}")
        return
    
    # Test Phase 2 components (lazy initialization)
    try:
        from core.embeddings import embedding_manager
        from core.vector_store import vector_store_manager
        
        st.sidebar.info("🔄 Embeddings Ready (lazy init)")
        st.sidebar.info("🔄 ChromaDB Ready (lazy init)")
            
    except Exception as e:
        st.sidebar.error("❌ Phase 2 Failed")
        logger.error(f"Phase 2 import error: {e}")
    
    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "🧪 Test Phase 2":
        show_test_phase2_page()
    elif page == "📥 Fetch ArXiv":
        show_fetch_arxiv_page()
    elif page == "📄 Upload PDF":
        show_upload_paper_page()
    elif page == "❓ Query Papers":
        show_query_papers_page()
    elif page == "🤖 Agent Workflow":
        show_agent_workflow_page()

def show_home_page():
    st.header("Welcome to the Research Assistant")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### What this app can do:
        
        🔍 **Paper Discovery**: Fetch research papers from ArXiv using natural language queries
        
        📚 **Smart Storage**: Store papers and their metadata in PostgreSQL, with full-text embeddings in ChromaDB
        
        🤖 **Multi-Agent Analysis**: Run an intelligent pipeline that:
        - Clusters papers by topic
        - Generates structured summaries
        - Proposes testable hypotheses
        - Designs experimental plans
        
        💬 **RAG-powered Q&A**: Ask questions about your research corpus and get answers with citations
        
        ### Tech Stack:
        - **Frontend**: Streamlit
        - **LLM**: Google Gemini (via LangChain)
        - **Vector DB**: ChromaDB
        - **Database**: Railway PostgreSQL
        - **PDF Parsing**: PyMuPDF
        """)
    
    with col2:
        st.info("""
        **Quick Start:**
        1. Set up your `.env` file with API keys
        2. Fetch some papers from ArXiv
        3. Upload a PDF to parse & embed
        4. Ask questions on the Query page
        5. Run the multi-agent workflow
        """)
        
        st.warning("""
        **Note**: Phase 5 (RAG Q&A) is now available.
        """)

# def show_upload_pdf_page():
#     # Overridden by ui.upload_paper.show_upload_paper_page
#     pass

# def show_query_papers_page():
#     # Overridden by ui.query_papers.show_query_papers_page
#     pass

def show_test_phase2_page():
    show_test_embeddings_page()

def show_agent_workflow_page():
    st.header("🤖 Multi-Agent Workflow")
    st.info("This feature will be implemented in Phase 6")
    
    topic = st.text_input("Research Topic", placeholder="e.g., 'machine learning in healthcare'")
    paper_limit = st.slider("Number of Papers", 5, 50, 20)
    
    if st.button("Run Workflow"):
        st.info("Multi-agent workflow will be implemented in Phase 6")

if __name__ == "__main__":
    main()
