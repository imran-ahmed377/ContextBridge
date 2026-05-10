# ContextBridge - Day 1

**Status: MVP Foundation - Minimal Viable Semantic Search**

## What's Built

Day 1 of ContextBridge provides the core indexing and semantic search infrastructure:

### Core Components
- **Embedding Service**: Uses `sentence-transformers` to generate vector embeddings for text
- **Storage Layer**: SQLite database for storing indexed content with embeddings
- **Search Service**: Semantic search using cosine similarity on embeddings
- **Connectors**: Base connector interface with File and Markdown implementations
- **FastAPI Server**: REST API for indexing and searching

### APIs Available

#### 1. Health Check
```
GET /
```
Returns server status and configuration.

#### 2. Index a File
```
POST /api/v1/index/file
Content-Type: application/x-www-form-urlencoded

file_path=/path/to/file.md
```
Reads a file, generates embeddings, and stores indexed content.

#### 3. Search
```
POST /api/v1/search
Content-Type: application/json

{
  "query": "how to optimize database queries",
  "sources": ["markdown", "file"],  // optional
  "limit": 10,
  "threshold": 0.5  // optional similarity threshold
}
```
Performs semantic search and returns ranked results with similarity scores.

#### 4. Get All Content
```
GET /api/v1/content/all?source=markdown
```
Lists all indexed content, optionally filtered by source.

#### 5. Get Specific Content
```
GET /api/v1/content/{content_id}
```
Retrieves full details of a single indexed item.

#### 6. Delete Content
```
DELETE /api/v1/content/{content_id}
```
Removes content from the index.

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
```bash
cp .env.example .env
# Edit .env if needed (defaults are sensible for MVP)
```

### 3. Start the Server
```bash
python main.py
```
Server runs on `http://localhost:8000`

### 4. API Documentation
Navigate to `http://localhost:8000/docs` (Swagger UI) to explore and test APIs interactively.

## Day 1 Quick Demo

### Index a Markdown File
```bash
curl -X POST "http://localhost:8000/api/v1/index/file" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "file_path=/path/to/your/file.md"
```

### Search
```bash
curl -X POST "http://localhost:8000/api/v1/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "your search query here",
    "limit": 5
  }'
```

## Architecture

```
FastAPI Server (main.py)
    ↓
├── Embedding Service (embeddings.py)
│   └── Uses sentence-transformers for vector generation
├── Storage Service (storage.py)
│   └── SQLite database with embedding vectors
├── Search Service (search.py)
│   └── Semantic search via cosine similarity
└── Connectors (connectors.py)
    ├── FileConnector
    └── MarkdownConnector
```

## Data Models

- **ContentChunk**: Raw content extracted from a source
- **IndexedContent**: Stored content with embedding vector
- **SearchQuery**: Search request with filters
- **SearchResponse**: Ranked search results with similarity scores

## Limitations (Day 1)

- Single-source indexing (no cross-source linking yet)
- No authentication/authorization
- SQLite only (not suitable for large scale)
- Basic chunking strategy (no overlap, no smart section splitting)
- No incremental sync (full re-index required)
- No concurrent request handling optimization

## Next Steps (Day 2+)

1. Add connector for external sources (GitHub, Notion)
2. Implement cross-source context linking
3. Add batch indexing and incremental sync
4. Build simple web UI for search
5. Implement user authentication
6. Add advanced chunking strategies
7. Performance optimization for large datasets

## Day 2 (What I implemented)

- **GitHubConnector**: Added `GitHubConnector` to `connectors.py` to fetch markdown/text files recursively from a GitHub repository (supports optional `GITHUB_TOKEN` via `.env`).
- **Batch indexing endpoints**: Added two endpoints in `main.py`:
  - `POST /api/v1/index/directory` — recursively index Markdown/text files from a local directory.
  - `POST /api/v1/index/github` — index markdown/text files from a GitHub repo (`owner` + `repo`, optional `path`).

These Day 2 changes let you index many files at once and pull documentation from GitHub to populate the local semantic index.

## File Structure

```
contextbridge/
├── main.py              # FastAPI application
├── config.py            # Configuration management
├── models.py            # Pydantic data models
├── embeddings.py        # Embedding service
├── storage.py           # Database operations
├── search.py            # Search logic
├── connectors.py        # Data source connectors
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── data/               # Created on first run
    └── contextbridge.db  # SQLite database
```

## Technology Stack

- **FastAPI**: Web framework
- **sentence-transformers**: Embeddings generation
- **SQLite**: Vector storage
- **Pydantic**: Data validation
- **NumPy**: Vector operations

---

**Built on Day 1 with MVP principles: Simple, functional, extensible.**
