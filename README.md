
# 🔬 Multi-Agent Research Assistant

A modern, multi-agent research assistant built with Streamlit, LangChain, Google Gemini, ChromaDB, and Railway PostgreSQL. This tool enables you to fetch, store, analyze, and synthesize research papers using advanced LLM-powered agents and RAG (Retrieval-Augmented Generation) techniques.

---

## 🚀 Features

- **📥 ArXiv Integration**: Search and fetch research papers from ArXiv using natural language queries.
- **📚 Smart Storage**: Store papers and metadata in PostgreSQL; chunk and embed text in ChromaDB for semantic search.
- **🔍 Vector Search**: Fast, full-text similarity search over your research corpus.
- **📄 PDF Processing**: Upload and parse local PDF files, chunking and embedding their content.
- **💬 RAG Q&A**: Ask questions about your stored papers and get LLM-generated answers with citations.
- **🤖 Multi-Agent Workflow**: Run a pipeline of agents to cluster, summarize, hypothesize, and design experiments from your corpus.
- **🗑️ Data Management**: Remove all data from both the vector store and SQL database with a single click.

---

## 🏗️ Architecture

```
Frontend: Streamlit
├── LLM: Google Gemini (via LangChain)
├── Vector DB: ChromaDB (local, persisted)
├── Database: Railway PostgreSQL
├── PDF Parsing: PyMuPDF
└── Orchestration: LangChain Agents (Cluster, Summarizer, Hypothesis, Experiment)
```

---

## 📋 Prerequisites

- Python 3.8+
- Railway PostgreSQL database (or compatible Postgres)
- Google Generative AI API key
- ArXiv API access (free)

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Research_agent_project
   ```

2. **Install dependencies**
   ```bash
   pip install virtualenv
   virtualenv venv
   ./venv/Scripts/activate  # On Windows
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

---

## 🚀 Usage

1. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

2. **Navigate through the UI:**
   - **🏠 Home**: Overview and system status
   - **📥 Fetch ArXiv**: Search and download papers from ArXiv
   - **📄 Upload PDF**: Upload and parse local PDF files
   - **❓ Query Papers**: RAG-powered Q&A over your corpus
   - **🔥 Agent Workflow**: Multi-agent research analysis pipeline
   - **🧪 Test**: Embeddings and vector store diagnostics
   - **🗑️ Remove ALL Data**: Clear all data from both SQL and vector store

---

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

---

## 🔄 Multi-Agent Pipeline

The system implements a sequential orchestrator with specialized agents:

1. **Cluster Agent**: Groups papers by topic using embeddings and LLMs.
2. **Summarizer Agent**: Creates structured summaries for each cluster.
3. **Hypothesis Agent**: Proposes testable hypotheses with supporting citations.
4. **Experiment Agent**: Designs experimental plans for each hypothesis.

---

## 🧪 Development Phases

- **Phase 1**: Config, DB, basic UI
- **Phase 2**: ChromaDB + Embeddings
- **Phase 3**: ArXiv ingestion
- **Phase 4**: PDF parsing
- **Phase 5**: RAG Q&A
- **Phase 6**: Multi-agent workflow

---

## 🔧 Configuration

### Environment Variables

| Variable                | Description                        | Default           |
|-------------------------|------------------------------------|-------------------|
| `DATABASE_URL`          | PostgreSQL connection string       | Required          |
| `GOOGLE_API_KEY`        | Google Generative AI API key       | Required          |
| `CHROMA_PERSIST_DIRECTORY` | ChromaDB storage path           | `./chroma_db`     |
| `ARXIV_MAX_RESULTS`     | Max ArXiv results                  | `50`              |
| `CHUNK_SIZE`            | Text chunk size                    | `1200`            |
| `CHUNK_OVERLAP`         | Chunk overlap                      | `200`             |
| `RETRIEVER_K`           | RAG retrieval count                | `5`               |
| `DEFAULT_PAPER_LIMIT`   | Default number of papers for agents| `20`              |

---

## �️ Administrative Scripts

### User Isolation Migration
```bash
# Run once to add user isolation to existing database
python migrate_user_isolation.py
```

### Data Management Scripts

**Safe Administrative Reset** (with confirmation):
```bash
# Interactive script with safety prompts
python admin_clear_all_data.py

# Skip confirmation (use with caution)
python admin_clear_all_data.py --confirm
```

**Quick Development Reset** (no confirmation):
```bash
# Fast reset for development - NO CONFIRMATION!
python dev_reset.py
```

⚠️ **WARNING**: These scripts will delete ALL user data from both SQL database and ChromaDB vector store. Use with extreme caution in production!

### What Gets Deleted:
- All papers from all users
- All text chunks and embeddings
- All cluster results 
- All hypotheses
- All experiment plans
- All ChromaDB collections

### When to Use:
- **admin_clear_all_data.py**: Production resets, major testing, system maintenance
- **dev_reset.py**: Quick development cycles, testing new features
- **migrate_user_isolation.py**: One-time migration to add user isolation

---

## �🐛 Troubleshooting

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

---

## 📝 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs in the Streamlit sidebar
- Open an issue on GitHub
