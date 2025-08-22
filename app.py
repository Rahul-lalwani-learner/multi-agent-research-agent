import streamlit as st
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.config import config, validate_config
from utils.logger import logger
from core.db import init_db, test_db_connection

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
        ["🏠 Home", "📥 Fetch ArXiv", "📄 Upload PDF", "❓ Query Papers", "🤖 Agent Workflow"]
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
    
    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "📥 Fetch ArXiv":
        show_fetch_arxiv_page()
    elif page == "📄 Upload PDF":
        show_upload_pdf_page()
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
        3. Try the RAG Q&A feature
        4. Run the multi-agent workflow
        """)
        
        st.warning("""
        **Note**: This is Phase 1 of development. 
        Some features are still being implemented.
        """)

def show_fetch_arxiv_page():
    st.header("📥 Fetch Papers from ArXiv")
    st.info("This feature will be implemented in Phase 3")
    
    # Placeholder form
    with st.form("arxiv_fetch"):
        query = st.text_input("Search Query", placeholder="e.g., 'machine learning' OR 'deep learning'")
        max_results = st.slider("Maximum Results", 1, 50, 10)
        load_pdfs = st.checkbox("Download and parse PDFs (slower)", value=False)
        
        submitted = st.form_submit_button("Fetch Papers")
        
        if submitted:
            st.info("ArXiv fetching will be implemented in Phase 3")

def show_upload_pdf_page():
    st.header("📄 Upload PDF")
    st.info("This feature will be implemented in Phase 4")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        st.info("PDF parsing and embedding will be implemented in Phase 4")

def show_query_papers_page():
    st.header("❓ Query Papers")
    st.info("This feature will be implemented in Phase 5")
    
    question = st.text_input("Ask a question about your research papers:")
    
    if st.button("Get Answer"):
        st.info("RAG-powered Q&A will be implemented in Phase 5")

def show_agent_workflow_page():
    st.header("🤖 Multi-Agent Workflow")
    st.info("This feature will be implemented in Phase 6")
    
    topic = st.text_input("Research Topic", placeholder="e.g., 'machine learning in healthcare'")
    paper_limit = st.slider("Number of Papers", 5, 50, 20)
    
    if st.button("Run Workflow"):
        st.info("Multi-agent workflow will be implemented in Phase 6")

if __name__ == "__main__":
    main()
