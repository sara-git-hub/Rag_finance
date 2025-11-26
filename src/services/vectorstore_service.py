"""
VectorStore Service
Unified interface for vector stores using LangChain integrations
Supports: Qdrant
"""

from typing import List, Literal, Optional
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_core.embeddings import Embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os


class VectorStoreService:
    """Service for managing vector stores with LangChain"""

    def __init__(
        self,
        embeddings: Embeddings,
        provider: Literal["qdrant"] = "qdrant",
        collection_name: str = "documents",
        **config
    ):
        """
        Initialize VectorStoreService

        Args:
            embeddings: LangChain embeddings instance
            provider: Vector store provider (only "qdrant" supported)
            collection_name: Name of collection
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
        else:
            raise ValueError(f"Unsupported provider: {provider}. Only 'qdrant' is supported.")

    def _init_qdrant(self) -> QdrantVectorStore:
        """
        Initialize Qdrant vector store

        Config keys:
            - path: Path to Qdrant database file (default: "assets/database")
            - url: Qdrant server URL (optional, for remote Qdrant)
            - distance: Distance metric ("cosine", "dot", or "euclid", default: "cosine")
        """
        path = self.config.get("path", "assets/database")
        url = self.config.get("url")
        distance_metric = self.config.get("distance", "cosine")

        # Map distance metric
        distance_map = {
            "cosine": Distance.COSINE,
            "dot": Distance.DOT,
            "euclid": Distance.EUCLID
        }
        distance = distance_map.get(distance_metric, Distance.COSINE)
        self._distance = distance

        # QdrantVectorStore does NOT support async_client parameter!
        # It uses run_in_executor internally for async operations
        # Best practice: Use from_existing_collection() with URL

        # Check if collection exists first
        try:
            if url:
                temp_client = QdrantClient(url=url)
            else:
                os.makedirs(path, exist_ok=True)
                temp_client = QdrantClient(path=path)

            collections = temp_client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)

            if not collection_exists:
                # Create collection if it doesn't exist
                sample_embedding = self.embeddings.embed_query("test")
                vector_size = len(sample_embedding)
                temp_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=distance)
                )
                print(f"✓ Collection '{self.collection_name}' created (dim={vector_size}, distance={distance.name})")
            else:
                print(f"✓ Collection '{self.collection_name}' already exists")

            temp_client.close()
        except Exception as e:
            print(f"Warning during collection setup: {e}")
            import traceback
            traceback.print_exc()

        # Use from_existing_collection for better async support
        if url:
            print(f"✓ Using QdrantVectorStore.from_existing_collection with URL: {url}")
            vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                collection_name=self.collection_name,
                url=url
            )
        else:
            print(f"✓ Using QdrantVectorStore.from_existing_collection with path: {path}")
            vectorstore = QdrantVectorStore.from_existing_collection(
                embedding=self.embeddings,
                collection_name=self.collection_name,
                path=path
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
            batch_size: Batch size for adding documents (Qdrant handles batching internally)

        Returns:
            List of document IDs
        """
        if not documents:
            return []

        # LangChain handles batching and indexing internally
        # Collection is already created during __init__
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

    async def asimilarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        filter: Optional[dict] = None
    ) -> List[tuple[Document, float]]:
        """
        Async search for similar documents with relevance scores

        Args:
            query: Query text
            k: Number of results to return
            filter: Metadata filter (optional)

        Returns:
            List of tuples (document, score)
        """
        # Use LangChain's native async method
        results = await self.vectorstore.asimilarity_search_with_score(
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
        self.vectorstore.client.delete_collection(self.collection_name)

    def delete_by_metadata(self, filter_dict: dict) -> bool:
        """
        Delete vectors by metadata filter

        Args:
            filter_dict: Filter dictionary (e.g., {"chunk_id": 123} or {"chunk_id": {"$in": [1,2,3]}})

        Returns:
            True if successful
        """
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchAny, MatchValue

            # Build Qdrant filter
            conditions = []
            for key, value in filter_dict.items():
                if isinstance(value, dict) and "$in" in value:
                    # Handle $in operator for multiple values
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchAny(any=value["$in"])
                        )
                    )
                else:
                    # Handle single value
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )

            filter_obj = Filter(must=conditions)

            # Delete points matching the filter
            self.vectorstore.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_obj
            )

            return True
        except Exception as e:
            print(f"Error deleting vectors by metadata: {e}")
            return False

    def get_stats(self) -> dict:
        """Get vector store statistics"""
        stats = {
            "provider": self.provider,
            "collection_name": self.collection_name,
            "embedding_dimension": getattr(self.embeddings, "embedding_dimension", "unknown")
        }

        # Qdrant-specific stats
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
