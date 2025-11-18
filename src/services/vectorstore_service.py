"""
VectorStore Service
Unified interface for vector stores using LangChain integrations
Supports: Qdrant, PGVector
"""

from typing import List, Literal, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from langchain_postgres import PGVector
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os


class VectorStoreService:
    """Service for managing vector stores with LangChain"""

    def __init__(
        self,
        embeddings: Embeddings,
        provider: Literal["qdrant", "pgvector"] = "qdrant",
        collection_name: str = "documents",
        **config
    ):
        """
        Initialize VectorStoreService

        Args:
            embeddings: LangChain embeddings instance
            provider: Vector store provider ("qdrant" or "pgvector")
            collection_name: Name of collection/table
            **config: Provider-specific configuration
        """
        self.embeddings = embeddings
        self.provider = provider
        self.collection_name = collection_name
        self.config = config
        self.vectorstore: Optional[VectorStore] = None

        # Initialize vector store
        if provider == "qdrant":
            self.vectorstore = self._init_qdrant()
        elif provider == "pgvector":
            self.vectorstore = self._init_pgvector()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _init_qdrant(self) -> QdrantVectorStore:
        """
        Initialize Qdrant vector store

        Config keys:
            - path: Path to Qdrant database file (default: "assets/database")
            - url: Qdrant server URL (optional, for remote Qdrant)
            - distance: Distance metric ("cosine" or "dot", default: "cosine")
        """
        path = self.config.get("path", "assets/database")
        url = self.config.get("url")
        distance_metric = self.config.get("distance", "cosine")

        # Create directory if it doesn't exist
        os.makedirs(path, exist_ok=True)

        # Map distance metric
        distance_map = {
            "cosine": Distance.COSINE,
            "dot": Distance.DOT,
            "euclid": Distance.EUCLID
        }
        distance = distance_map.get(distance_metric, Distance.COSINE)

        # Initialize Qdrant client
        if url:
            client = QdrantClient(url=url)
        else:
            # Local file-based storage
            client = QdrantClient(path=path)

        # Create vector store
        vectorstore = QdrantVectorStore(
            client=client,
            collection_name=self.collection_name,
            embedding=self.embeddings,
            distance=distance
        )

        return vectorstore

    def _init_pgvector(self) -> PGVector:
        """
        Initialize PGVector vector store

        Config keys:
            - connection_string: PostgreSQL connection string (required)
            - distance: Distance metric ("cosine" or "l2", default: "cosine")
        """
        connection_string = self.config.get("connection_string")
        if not connection_string:
            raise ValueError("PGVector requires 'connection_string' in config")

        distance_metric = self.config.get("distance", "cosine")

        # Map distance metric for pgvector
        distance_map = {
            "cosine": "cosine",
            "dot": "dot",
            "l2": "l2"
        }
        distance = distance_map.get(distance_metric, "cosine")

        # Create vector store
        vectorstore = PGVector(
            collection_name=self.collection_name,
            connection=connection_string,
            embeddings=self.embeddings,
            distance_strategy=distance,
            use_jsonb=True
        )

        return vectorstore

    def add_documents(
        self,
        documents: List[Document],
        batch_size: int = 50
    ) -> List[str]:
        """
        Add documents to vector store

        Args:
            documents: List of Document objects
            batch_size: Batch size for adding documents

        Returns:
            List of document IDs
        """
        if not documents:
            return []

        # LangChain handles batching internally
        ids = self.vectorstore.add_documents(documents)

        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[Document]:
        """
        Search for similar documents

        Args:
            query: Query text
            k: Number of results to return
            filter: Metadata filter (optional)

        Returns:
            List of similar documents
        """
        results = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter=filter
        )

        return results

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """
        Search for similar documents with relevance scores

        Args:
            query: Query text
            k: Number of results to return
            filter: Metadata filter (optional)

        Returns:
            List of tuples (document, score)
        """
        results = self.vectorstore.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter
        )

        return results

    def as_retriever(
        self,
        search_type: Literal["similarity", "mmr", "similarity_score_threshold"] = "similarity",
        search_kwargs: Optional[dict] = None
    ):
        """
        Get retriever interface for use in LangChain chains

        Args:
            search_type: Type of search
                - "similarity": Standard similarity search
                - "mmr": Maximal Marginal Relevance (diverse results)
                - "similarity_score_threshold": Filter by score threshold
            search_kwargs: Additional search arguments
                - k: Number of results (default: 5)
                - score_threshold: Minimum score (for similarity_score_threshold)
                - fetch_k: Number to fetch for MMR (for mmr)
                - lambda_mult: Diversity parameter (for mmr, 0=diverse, 1=similar)

        Returns:
            VectorStoreRetriever instance
        """
        search_kwargs = search_kwargs or {"k": 5}

        return self.vectorstore.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

    def delete_collection(self):
        """Delete the entire collection"""
        if self.provider == "qdrant":
            self.vectorstore.client.delete_collection(self.collection_name)
        elif self.provider == "pgvector":
            # PGVector collection deletion
            self.vectorstore.drop_tables()

    def get_stats(self) -> dict:
        """Get vector store statistics"""
        stats = {
            "provider": self.provider,
            "collection_name": self.collection_name,
            "embedding_dimension": getattr(self.embeddings, "embedding_dimension", "unknown")
        }

        # Provider-specific stats
        if self.provider == "qdrant":
            try:
                collection_info = self.vectorstore.client.get_collection(self.collection_name)
                stats["vectors_count"] = collection_info.vectors_count
                stats["points_count"] = collection_info.points_count
            except:
                stats["vectors_count"] = "unknown"

        return stats


def create_vectorstore(
    embeddings: Embeddings,
    provider: str,
    collection_name: str,
    **config
) -> VectorStoreService:
    """
    Factory function to create vector store service

    Args:
        embeddings: Embeddings instance
        provider: Vector store provider
        collection_name: Collection name
        **config: Provider configuration

    Returns:
        VectorStoreService instance
    """
    return VectorStoreService(
        embeddings=embeddings,
        provider=provider,
        collection_name=collection_name,
        **config
    )
