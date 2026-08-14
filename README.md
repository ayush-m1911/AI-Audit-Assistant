# AuditFlow AI — Enterprise Compliance & Audit Assistant

AuditFlow AI is an enterprise-grade AI Compliance & Audit Assistant powered by FastAPI, React.js, LangGraph, Neon PostgreSQL, and Qdrant. It ingests company policy documents, indexes them as semantic embeddings, and runs compliance audit questions through a structured multi-agent LangGraph workflow.

---

## 1. System Architecture

The end-to-end execution flow of the system runs as follows:

```
    Document Upload
          ↓
  [React Documents UI] 
          ↓ POST /upload
    [FastAPI Ingest]
          ↓
  - Parse policy text
  - Chunk & embed (BAAI/bge-small-en-v1.5)
  - Write metadata to Neon PostgreSQL
  - Write vectors to Qdrant Collection
          ↓
      Indexed
          ↓
   Run Compliance Audit
          ↓
    [React Audits UI]
          ↓ POST /audit
  [LangGraph Orchestrator]
          ↓
  - Planner Agent (Scoping checklist)
  - Retriever Agent (RAG context from Qdrant)
  - Compliance Agent (Control gap checks)
  - Risk Agent (Severity & Likelihood calculations)
  - Recommendation Agent (Actionable remediation list)
  - Confidence Gate (Confidence scoring reviews trigger)
          ↓
  Review Required?
    ├─► YES: [Human Review Gate] ──► Approve/Reject ──► [Report Gen]
    └─► NO: ───────────────────────────────────────────► [Report Gen]
                                                               │
                                                       Neon PostgreSQL
                                                       (Persistent Report)
                                                               │
                                                        [React Reports]
                                                       (Evidence & Download)
```

---

## 2. Environment Configurations

### Backend Configuration (`backend/.env`)
Create a `.env` file inside the `backend/` directory:
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=qwen/qwen3.6-27b
DATABASE_URL=postgresql://neondb_owner:...@ep-sparkling-mud...neon.tech/neondb?sslmode=require
QDRANT_HOST=localhost
QDRANT_PORT=6335
QDRANT_COLLECTION=audit_documents
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
UPLOAD_DIR=data/uploads
REPORT_DIR=reports
```
*Note: This project utilizes a custom host port `6335` to connect to Qdrant (mapping to port `6333` inside the Docker container).*

### Frontend Configuration (`frontend/.env`)
Create a `.env` file inside the `frontend/` directory:
```env
VITE_API_BASE_URL=http://localhost:8000
```
*Note: Public configurations prefix with `VITE_` to be loaded in client bundles. Private keys are never exposed.*

---

## 3. Getting Started

### Prerequisites
* Docker Desktop (Required for local Qdrant container)
* Node.js (v18+) & npm
* Python (3.10+)

### Setting up Qdrant Vector DB
Start the local Qdrant container mapping container port `6333` to host port `6335`:
```bash
docker run -d -p 6335:6333 -v qdrant_storage:/qdrant/storage qdrant/qdrant
```

### Backend Installation & Startup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server using Uvicorn:
   ```bash
   venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```

### Frontend Installation & Startup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 4. Verification & Testing

### Running Backend Tests
Ensure your backend environment is activated, then run the pytest suite:
```bash
cd backend
venv\Scripts\pytest tests/
```

### Production Build compilation
Verify that the React production assets build correctly:
```bash
cd frontend
npm run build
```

### Gated Sandbox Fixtures
For development-only presentation checks (when external APIs like Groq hit rate limits), the workspace contains mock fixtures (`mock_review_123` and `mock_report_123`). These sandbox features are gated using:
`import.meta.env.DEV`
This guarantees they compile out and are completely inaccessible in production builds.
