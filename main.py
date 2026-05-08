from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid
from datetime import datetime
from typing import List

from config import settings
from models import ContentChunk, SearchQuery, SearchResponse
from embeddings import embedding_service
from storage import storage_service
from search import search_service
from connectors import FileConnector, MarkdownConnector


app = FastAPI(title=settings.app_name, version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "embedding_model": settings.embedding_model
    }


@app.post("/api/v1/index/file")
def index_file(file_path: str) -> dict:
    """
    Index a single file and store embeddings.

    Args:
        file_path: Path to the file to index

    Returns:
        Dictionary with indexing results
    """
    try:
        # Determine connector type based on file extension
        if file_path.endswith('.md'):
            connector = MarkdownConnector(file_path)
        else:
            connector = FileConnector(file_path)

        # Fetch content from connector
        content_chunks = connector.fetch_content()
        if not content_chunks:
            raise HTTPException(
                status_code=400, detail="No content extracted from file")

        # Process each chunk: embed and store
        indexed_count = 0
        for chunk in content_chunks:
            # Generate embedding
            embedding = embedding_service.embed_text(chunk.content)

            # Create indexed content object
            indexed_item = {
                'id': str(uuid.uuid4()),
                'content_chunk_id': str(uuid.uuid4()),
                'source': chunk.source,
                'title': chunk.title,
                'content': chunk.content,
                'embedding': embedding,
                'metadata': {
                    **chunk.metadata,
                    'url': chunk.url
                },
                'indexed_at': datetime.now()
            }

            # Convert to IndexedContent model and store
            from models import IndexedContent
            indexed_content = IndexedContent(**indexed_item)

            if storage_service.store_indexed_content(indexed_content):
                indexed_count += 1

        return {
            "status": "success",
            "file_path": file_path,
            "chunks_processed": len(content_chunks),
            "chunks_indexed": indexed_count,
            "source": connector.source_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/search")
def search(query: SearchQuery) -> SearchResponse:
    """
    Perform semantic search on indexed content.

    Args:
        query: SearchQuery object with query string and filters

    Returns:
        SearchResponse with ranked results
    """
    try:
        if not query.query.strip():
            raise HTTPException(
                status_code=400, detail="Query cannot be empty")

        response = search_service.search(query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/content/all")
def get_all_content(source: str = None):
    """
    Retrieve all indexed content, optionally filtered by source.

    Args:
        source: Optional source filter

    Returns:
        List of indexed content
    """
    try:
        content = storage_service.get_all_indexed_content(source=source)
        return {
            "total": len(content),
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "source": item.source,
                    "content": item.content[:200],
                    "metadata": item.metadata,
                    "indexed_at": item.indexed_at.isoformat()
                }
                for item in content
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/content/{content_id}")
def get_content(content_id: str):
    """
    Retrieve a specific indexed content item by ID.

    Args:
        content_id: ID of content to retrieve

    Returns:
        Full indexed content item
    """
    try:
        content = storage_service.get_indexed_content(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")

        return {
            "id": content.id,
            "title": content.title,
            "source": content.source,
            "content": content.content,
            "metadata": content.metadata,
            "indexed_at": content.indexed_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/content/{content_id}")
def delete_content(content_id: str):
    """
    Delete an indexed content item.

    Args:
        content_id: ID of content to delete

    Returns:
        Confirmation message
    """
    try:
        if storage_service.delete_indexed_content(content_id):
            return {"status": "success", "message": "Content deleted"}
        else:
            raise HTTPException(
                status_code=500, detail="Failed to delete content")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
