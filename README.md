# 🔬 Multi-Agent Research Assistant

A Streamlit-based research paper assistant that can fetch papers from ArXiv, store them in PostgreSQL, create embeddings in ChromaDB, and run a multi-agent pipeline for research analysis.

## 🚀 Features

- **📥 ArXiv Integration**: Fetch research papers using natural language queries
- **📚 Smart Storage**: Store papers and metadata in Railway PostgreSQL
- **🔍 Vector Search**: Full-text embeddings stored in ChromaDB
- **🤖 Multi-Agent Analysis**: Intelligent pipeline for research synthesis
- **💬 RAG-powered Q&A**: Ask questions about your research corpus
- **📄 PDF Processing**: Upload and parse local PDF files

## 🏗️ Architecture

```
Frontend: Streamlit
├── LLM: Google Gemini (via LangChain)
├── Vector DB: ChromaDB (local persisted)
├── Database: Railway PostgreSQL
├── PDF Parsing: PyMuPDF
└── Orchestration: LangChain Agents
```

## 📋 Prerequisites

- Python 3.8+
- Railway PostgreSQL database
- Google Generative AI API key
- ArXiv API access (free)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd research_assistant_project
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   # Database
   DATABASE_URL=postgresql://username:password@host:port/database
   
   # Google Generative AI
   GOOGLE_API_KEY=your_google_api_key_here
   
   # Optional: Customize settings
   CHROMA_PERSIST_DIRECTORY=./chroma_db
   ARXIV_MAX_RESULTS=50
   CHUNK_SIZE=1200
   CHUNK_OVERLAP=200
   RETRIEVER_K=5
   DEFAULT_PAPER_LIMIT=20
   ```

4. **Initialize the database**
   ```bash
   python -c "from core.db import init_db; init_db()"
   ```

## 🚀 Usage

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Navigate through the pages**:
   - **🏠 Home**: Overview and system status
   - **📥 Fetch ArXiv**: Search and download papers
   - **📄 Upload PDF**: Upload local PDF files
   - **❓ Query Papers**: RAG-powered Q&A
   - **🤖 Agent Workflow**: Multi-agent research analysis

## 📊 Database Schema

### Papers Table
- `id`: Primary key
- `arxiv_id`: ArXiv identifier (unique)
- `title`: Paper title
- `authors`: Author list
- `summary`: Abstract
- `published_at`: Publication date
- `link`: ArXiv URL
- `pdf_url`: PDF download URL
- `source`: Source (arxiv/upload)
- `ingested`: Text parsed flag
- `embedded`: Vectors created flag

### Chunks Table
- `id`: Primary key
- `paper_id`: Foreign key to papers
- `order`: Chunk sequence
- `text`: Chunk content
- `chroma_doc_id`: ChromaDB document ID

### Agent Results Tables
- `cluster_results`: Paper clustering results
- `hypotheses`: Generated hypotheses
- `experiment_plans`: Experimental designs

## 🔄 Multi-Agent Pipeline

The system implements a sequential orchestrator with specialized agents:

1. **Cluster Agent**: Groups papers by topic using embeddings
2. **Summarizer Agent**: Creates structured summaries per cluster
3. **Hypothesis Agent**: Proposes testable hypotheses with citations
4. **Experiment Agent**: Designs experimental plans for hypotheses

## 🧪 Development Phases

- **Phase 1**: ✅ Config, DB, basic UI
- **Phase 2**: ChromaDB + Embeddings
- **Phase 3**: ArXiv ingestion
- **Phase 4**: PDF parsing
- **Phase 5**: RAG Q&A
- **Phase 6**: Multi-agent workflow

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `GOOGLE_API_KEY` | Google Generative AI API key | Required |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path | `./chroma_db` |
| `ARXIV_MAX_RESULTS` | Max ArXiv results | `50` |
| `CHUNK_SIZE` | Text chunk size | `1200` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `RETRIEVER_K` | RAG retrieval count | `5` |

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check your `DATABASE_URL` format
   - Ensure Railway PostgreSQL is running
   - Verify network connectivity

2. **Google API Key Error**
   - Ensure `GOOGLE_API_KEY` is set in `.env`
   - Verify the API key is valid and has proper permissions

3. **ChromaDB Issues**
   - Check disk space for `CHROMA_PERSIST_DIRECTORY`
   - Ensure write permissions to the directory

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in the Streamlit sidebar
- Open an issue on GitHub
