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
from ui.agent_workflow import show_agent_workflow_page as show_agent_workflow_page_impl

# Page configuration
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global styles and small UI helpers
def inject_styles():
    st.markdown(
        """
        <style>
        .main .block-container { padding-top: 1rem; padding-bottom: 2rem; }
        h1, h2, h3 { letter-spacing: .2px; }
        section[data-testid="stSidebar"] button { margin-bottom: .3rem; border-radius: 8px; }
        .status-card { border: 1px solid rgba(49,51,63,.2); border-radius: 10px; padding: 12px 14px; background: #fff; box-shadow: 0 1px 2px rgba(0,0,0,.04); }
        .status-ok { border-left: 6px solid #16a34a; }
        .status-warn { border-left: 6px solid #ef4444; }
        .status-title { font-weight: 600; font-size: .9rem; margin-bottom: .25rem; }
        .status-desc { color: #5e5f6e; font-size: .85rem; margin: 0; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: .75rem; }
        .badge-ok { background:#dcfce7; color:#166534; }
        .badge-warn { background:#fee2e2; color:#991b1b; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_status_card(title: str, ok: bool, desc: str):
    css_class = "status-ok" if ok else "status-warn"
    badge = "<span class='badge badge-ok'>OK</span>" if ok else "<span class='badge badge-warn'>Issue</span>"
    st.markdown(
        f"""
        <div class="status-card {css_class}">
            <div class="status-title"><span class="status-desc">{title}</span> {badge}</div>
            <p class="status-desc">{desc}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def main():
    inject_styles()
    st.title("🔬 Multi-Agent Research Assistant")
    st.markdown("---")
    
    # Sidebar for navigation (buttons)
    st.sidebar.title("Navigation")
    if "nav_page" not in st.session_state:
        st.session_state.nav_page = "🏠 Home"

    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.nav_page = "🏠 Home"
        if st.button("📥 ArXiv", use_container_width=True):
            st.session_state.nav_page = "📥 Fetch ArXiv"
        if st.button("❓ Query", use_container_width=True):
            st.session_state.nav_page = "❓ Query Papers"
    with col_b:
        if st.button("🧪 Test", use_container_width=True):
            st.session_state.nav_page = "🧪 Test Phase 2"
        if st.button("📄 Upload", use_container_width=True):
            st.session_state.nav_page = "📄 Upload PDF"
        if st.button("🤖 Agents", use_container_width=True):
            st.session_state.nav_page = "🤖 Agent Workflow"

    page = st.session_state.nav_page
    
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
    vs_ok = True
    try:
        from core.embeddings import embedding_manager
        from core.vector_store import vector_store_manager
        
        st.sidebar.info("🔄 Embeddings Ready (lazy init)")
        st.sidebar.info("🔄 ChromaDB Ready (lazy init)")
            
    except Exception as e:
        st.sidebar.error("❌ Phase 2 Failed")
        logger.error(f"Phase 2 import error: {e}")
        vs_ok = False

    # Top status cards
    c1, c2, c3 = st.columns(3)
    with c1:
        render_status_card("Configuration", True, "Environment and API keys loaded")
    with c2:
        render_status_card("Database", True, "PostgreSQL connectivity and tables ready")
    with c3:
        render_status_card("Vector Store", vs_ok, "Chroma client available for retrieval")
    
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
        show_agent_workflow_page_impl()

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
    # Backward-compatible wrapper
    show_agent_workflow_page_impl()

if __name__ == "__main__":
    main()
