import sqlite3
import json
from typing import List, Optional
from datetime import datetime
import os
from config import settings
from models import IndexedContent, ContentChunk


class StorageService:
    """Service for storing and retrieving indexed content from SQLite."""

    def __init__(self):
        """Initialize database connection and create tables if needed."""
        os.makedirs(os.path.dirname(settings.db_path), exist_ok=True)
        self.db_path = settings.db_path
        self._init_db()

    def _get_connection(self):
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def _init_db(self):
        """Initialize database schema."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Table for indexed content with embeddings
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS indexed_content (
                id TEXT PRIMARY KEY,
                content_chunk_id TEXT NOT NULL,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                embedding BLOB NOT NULL,
                metadata TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create index on source for faster filtering
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_source ON indexed_content(source)
        """)

        conn.commit()
        conn.close()

    def store_indexed_content(self, item: IndexedContent) -> bool:
        """
        Store an indexed content item in the database.

        Args:
            item: IndexedContent object to store

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Convert embedding list to binary format (pickle-like)
            embedding_blob = json.dumps(item.embedding).encode('utf-8')
            metadata_json = json.dumps(item.metadata)

            cursor.execute("""
                INSERT OR REPLACE INTO indexed_content
                (id, content_chunk_id, source, title, content, embedding, metadata, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.id,
                item.content_chunk_id,
                item.source,
                item.title,
                item.content,
                embedding_blob,
                metadata_json,
                item.indexed_at
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error storing indexed content: {e}")
            return False

    def get_indexed_content(self, content_id: str) -> Optional[IndexedContent]:
        """
        Retrieve an indexed content item by ID.

        Args:
            content_id: ID of the content to retrieve

        Returns:
            IndexedContent object or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM indexed_content WHERE id = ?", (content_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            embedding = json.loads(row['embedding'].decode('utf-8'))
            metadata = json.loads(row['metadata']) if row['metadata'] else {}

            return IndexedContent(
                id=row['id'],
                content_chunk_id=row['content_chunk_id'],
                source=row['source'],
                title=row['title'],
                content=row['content'],
                embedding=embedding,
                metadata=metadata,
                indexed_at=datetime.fromisoformat(row['indexed_at'])
            )
        except Exception as e:
            print(f"Error retrieving indexed content: {e}")
            return None

    def get_all_indexed_content(self, source: Optional[str] = None) -> List[IndexedContent]:
        """
        Retrieve all indexed content, optionally filtered by source.

        Args:
            source: Optional source filter

        Returns:
            List of IndexedContent objects
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            if source:
                cursor.execute(
                    "SELECT * FROM indexed_content WHERE source = ?", (source,))
            else:
                cursor.execute("SELECT * FROM indexed_content")

            rows = cursor.fetchall()
            conn.close()

            results = []
            for row in rows:
                embedding = json.loads(row['embedding'].decode('utf-8'))
                metadata = json.loads(
                    row['metadata']) if row['metadata'] else {}

                results.append(IndexedContent(
                    id=row['id'],
                    content_chunk_id=row['content_chunk_id'],
                    source=row['source'],
                    title=row['title'],
                    content=row['content'],
                    embedding=embedding,
                    metadata=metadata,
                    indexed_at=datetime.fromisoformat(row['indexed_at'])
                ))

            return results
        except Exception as e:
            print(f"Error retrieving all indexed content: {e}")
            return []

    def delete_indexed_content(self, content_id: str) -> bool:
        """
        Delete an indexed content item.

        Args:
            content_id: ID of content to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM indexed_content WHERE id = ?", (content_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting indexed content: {e}")
            return False


# Global instance
storage_service = StorageService()
