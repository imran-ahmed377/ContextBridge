from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ContentChunk(BaseModel):
    """Represents a piece of indexed content."""
    id: Optional[str] = None
    source: str  # e.g., 'github', 'notion', 'slack'
    source_id: str  # unique ID within the source (e.g., issue #123, page_id)
    title: str
    content: str  # The raw text content
    url: Optional[str] = None
    metadata: dict = {}  # Additional fields (author, created_at, type, etc.)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IndexedContent(BaseModel):
    """Represents a stored, indexed piece of content with embeddings."""
    id: str
    content_chunk_id: str
    source: str
    title: str
    content: str
    embedding: List[float]  # Vector embedding for semantic search
    metadata: dict
    indexed_at: datetime


class SearchQuery(BaseModel):
    """Request model for search."""
    query: str
    sources: Optional[List[str]] = None  # Filter by source(s)
    limit: int = 10
    threshold: Optional[float] = 0.5  # Similarity threshold


class SearchResult(BaseModel):
    """Single search result."""
    id: str
    title: str
    content: str
    source: str
    url: Optional[str] = None
    similarity_score: float
    metadata: dict


class SearchResponse(BaseModel):
    """Response model for search."""
    query: str
    results: List[SearchResult]
    total_results: int
    execution_time_ms: float
