# ContextBridge

ContextBridge is a compact semantic search engine and context layer for LLM-powered applications. It ingests text content from files and external sources, converts content into vector embeddings,+ stores them in a local index, and exposes search and indexing APIs to retrieve relevant context for downstream language model usage.

## Features

- Ingest content from local files and connectors
- Generate embeddings (pluggable embedding backend)
- Store embeddings and metadata in a lightweight local database
- Perform semantic search with cosine similarity
- HTTP API (FastAPI) for indexing and retrieval

## Quickstart

Prerequisites: Python 3.8+ and pip.

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. (Optional) Copy and edit environment variables:

```bash
cp .env.example .env
```

3. Start the API server:

```bash
python main.py
```

The server listens on `http://localhost:8000` and Swagger UI is available at `/docs`.

## Common API Endpoints

- `GET /` — Health check and basic configuration
- `POST /api/v1/index/file` — Index a single file (form data: `file_path`)
- `POST /api/v1/index/directory` — Recursively index a local directory
- `POST /api/v1/index/github` — Index markdown/text files from a GitHub repo
- `POST /api/v1/search` — Semantic search (JSON: `query`, optional filters)
- `GET /api/v1/content/all` — List indexed content
- `GET /api/v1/content/{content_id}` — Retrieve a specific indexed item
- `DELETE /api/v1/content/{content_id}` — Remove an item from the index

Refer to the live Swagger UI at `/docs` for request/response details.

## Project Layout

```
contextbridge/
├── main.py        # FastAPI application and HTTP routes
├── config.py      # Configuration and environment handling
├── models.py      # Pydantic request/response models
├── embeddings.py  # Embedding backend wrapper
├── storage.py     # Database and persistence logic
├── search.py      # Semantic search utilities
├── connectors.py  # Content connectors (file, markdown, GitHub, ...)
├── requirements.txt
├── example_content.md
└── data/          # runtime data (SQLite DB created here)
```

## Configuration

Settings are read from environment variables (see `.env.example`). Key configs include embedding backend selection, database path, and optional GitHub token for repository connectors.

## Development Notes

- Embedding generation is pluggable; `sentence-transformers` is used by default in the MVP.
- Storage currently uses SQLite suitable for local/small datasets. Swap in a production vector DB for scale.
- Chunking and retrieval are intentionally simple; advanced strategies (overlap, hierarchical indexing) are planned.

## Contributing

Contributions are welcome. For bug fixes or features:

1. Fork the repo
2. Create a topic branch
3. Open a PR describing changes

Please include tests for new features where applicable.

## License

This project is provided under the MIT License — see the `LICENSE` file if present.

## Contact

For questions or help, open an issue or contact the maintainer via the repository.

---