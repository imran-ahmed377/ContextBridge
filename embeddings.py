from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config import settings


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""

    def __init__(self):
        """Initialize the embedding model."""
        self.model = SentenceTransformer(settings.embedding_model)

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch (more efficient).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return [emb.tolist() for emb in embeddings]

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Similarity score between 0 and 1
        """
        arr1 = np.array(embedding1)
        arr2 = np.array(embedding2)

        # Cosine similarity
        similarity = np.dot(arr1, arr2) / \
            (np.linalg.norm(arr1) * np.linalg.norm(arr2))
        return float(similarity)


# Global instance
embedding_service = EmbeddingService()
