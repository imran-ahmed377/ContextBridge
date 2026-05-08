# ContextBridge Example Documentation

## Introduction

Welcome to ContextBridge. This document serves as example content to demonstrate the semantic search capability.

## Architecture Overview

ContextBridge uses a three-layer architecture:

### Embedding Layer
The embedding layer converts text into vector representations using transformer models. These vectors capture semantic meaning, allowing us to find similar content even when the exact wording differs.

### Storage Layer
Indexed embeddings are stored in a vector database with metadata. Each entry includes the original text, source information, and similarity metrics.

### Search Layer
When a user queries, their search text is embedded and compared against all stored vectors using cosine similarity. Results are ranked by relevance score.

## Key Concepts

### Semantic Search
Unlike keyword search, semantic search understands meaning. Searching for "how to optimize performance" will find content about database indexing, caching strategies, and algorithm efficiency—even if those exact words aren't in the query.

### Embeddings
Embeddings are numerical representations of text. A sentence is converted into a vector of 384 numbers (for our lightweight model), where similar meanings produce similar vectors. The model learns this through training on billions of text examples.

### Vector Similarity
We use cosine similarity to measure how close two vectors are. A score of 1.0 means identical, 0.0 means completely unrelated. We filter results by a similarity threshold (default 0.5).

## Getting Started

1. Start the ContextBridge server
2. Index your documentation files (Markdown, text)
3. Search across your indexed content with natural language queries
4. Results appear ranked by relevance

## Use Cases

### Knowledge Base Search
Index all your documentation and wikis. Find answers faster with natural language search.

### Code Understanding
Index source code comments and documentation. Ask questions like "where is error handling implemented?"

### Meeting Notes Analysis
Index meeting transcripts and notes. Discover decisions and action items across meetings.

### Troubleshooting Guides
Build a searchable knowledge base of common issues and solutions.

## Performance Characteristics

- **Embedding Time**: ~10-50ms per document (depends on size)
- **Search Time**: <100ms for 1000s of documents
- **Storage**: ~4KB per embedding vector
- **Throughput**: Process 100+ documents per second

## Future Enhancements

- Cross-document relationship detection
- Automatic summarization of search results
- Real-time sync from external sources (GitHub, Slack, Notion)
- Advanced filtering and faceted search
- Persistent user sessions and personalization

## Technical Stack

- **Embeddings**: sentence-transformers (384-dim vectors)
- **Search**: Cosine similarity with vector indexing
- **Storage**: SQLite with JSON metadata
- **API**: FastAPI with async support

## FAQ

**Q: Can I search across multiple file types?**
A: Yes. ContextBridge supports Markdown, plain text, and JSON. The connector framework makes adding new types simple.

**Q: How accurate is semantic search?**
A: Accuracy depends on your use case. For finding relevant documents, it's excellent (>80% precision). For exact fact extraction, use it as a first filter before reading full results.

**Q: Does it require internet connectivity?**
A: No. Everything runs locally on your machine. Embeddings are generated offline.

**Q: How much disk space do I need?**
A: Very little. Each indexed document takes about 4KB for its embedding plus the text size. 10,000 documents is typically <500MB.

---

*This documentation demonstrates ContextBridge's semantic search capabilities. Try indexing this file and searching for concepts mentioned throughout.*
