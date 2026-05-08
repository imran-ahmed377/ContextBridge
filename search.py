from typing import List
from models import SearchResult, SearchResponse, SearchQuery
from embeddings import embedding_service
from storage import storage_service
import time


class SearchService:
    """Service for semantic search across indexed content."""

    def search(self, search_query: SearchQuery) -> SearchResponse:
        """
        Perform semantic search on indexed content.

        Args:
            search_query: SearchQuery object with query string and filters

        Returns:
            SearchResponse with ranked results
        """
        start_time = time.time()

        # Generate embedding for the query
        query_embedding = embedding_service.embed_text(search_query.query)

        # Retrieve all indexed content (or filter by source if specified)
        if search_query.sources and len(search_query.sources) > 0:
            all_content = []
            for source in search_query.sources:
                all_content.extend(
                    storage_service.get_all_indexed_content(source=source))
        else:
            all_content = storage_service.get_all_indexed_content()

        # Calculate similarity scores
        scored_results = []
        for content in all_content:
            similarity = embedding_service.similarity(
                query_embedding, content.embedding)

            # Filter by threshold if specified
            if search_query.threshold and similarity < search_query.threshold:
                continue

            result = SearchResult(
                id=content.id,
                title=content.title,
                content=content.content[:500],  # Truncate for display
                source=content.source,
                url=content.metadata.get('url'),
                similarity_score=similarity,
                metadata=content.metadata
            )
            scored_results.append((result, similarity))

        # Sort by similarity score (descending)
        scored_results.sort(key=lambda x: x[1], reverse=True)

        # Apply limit
        results = [result for result, _ in scored_results[:search_query.limit]]

        execution_time = (time.time() - start_time) * \
            1000  # Convert to milliseconds

        return SearchResponse(
            query=search_query.query,
            results=results,
            total_results=len(scored_results),
            execution_time_ms=execution_time
        )


# Global instance
search_service = SearchService()
