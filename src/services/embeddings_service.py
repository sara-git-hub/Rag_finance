"""
Embeddings Service
Unified interface for embeddings: local (HuggingFace) and API-based (OpenAI, Cohere)
"""

from functools import lru_cache
from typing import List, Literal
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_core.embeddings import Embeddings


class EmbeddingsService:
    """Unified embeddings service supporting multiple providers"""

    # Supported embedding models
    HUGGINGFACE_MODELS = {
        "multilingual": "sentence-transformers/paraphrase-multilingual-mpnet-base-v2",  # 768 dims
        "multilingual-mini": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",  # 384 dims
        "english": "sentence-transformers/all-mpnet-base-v2",  # 768 dims
        "english-mini": "sentence-transformers/all-MiniLM-L6-v2",  # 384 dims
    }

    def __init__(
        self,
        provider: Literal["local", "openai", "cohere"] = "local",
        model_name: str = None,
        api_key: str = None,
        device: str = "cpu",
        **kwargs
    ):
        """
        Initialize EmbeddingsService

        Args:
            provider: Embedding provider ("local", "openai", "cohere")
            model_name: Model name/ID
            api_key: API key for OpenAI/Cohere
            device: Device for local embeddings ("cpu" or "cuda")
            **kwargs: Additional provider-specific arguments
        """
        self.provider = provider
        self.device = device
        self.embeddings: Embeddings = None
        self.embedding_dimension: int = 0

        # Initialize embeddings based on provider
        if provider == "local":
            self.embeddings = self._init_local_embeddings(model_name, device)
        elif provider == "openai":
            self.embeddings = self._init_openai_embeddings(model_name, api_key)
        elif provider == "cohere":
            self.embeddings = self._init_cohere_embeddings(model_name, api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _init_local_embeddings(
        self,
        model_name: str = None,
        device: str = "cpu"
    ) -> HuggingFaceEmbeddings:
        """
        Initialize local HuggingFace embeddings

        Args:
            model_name: HuggingFace model name or key from HUGGINGFACE_MODELS
            device: Device to use ("cpu" or "cuda")

        Returns:
            HuggingFaceEmbeddings instance
        """
        # Default to multilingual model
        if model_name is None:
            model_name = "multilingual"

        # Resolve model name from presets
        if model_name in self.HUGGINGFACE_MODELS:
            model_name = self.HUGGINGFACE_MODELS[model_name]

        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': device},
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 32
            }
        )

        # Get embedding dimension
        # Generate a test embedding to determine dimensions
        test_embedding = embeddings.embed_query("test")
        self.embedding_dimension = len(test_embedding)

        return embeddings

    def _init_openai_embeddings(
        self,
        model_name: str = None,
        api_key: str = None
    ) -> OpenAIEmbeddings:
        """
        Initialize OpenAI embeddings

        Args:
            model_name: OpenAI model name (default: "text-embedding-3-small")
            api_key: OpenAI API key

        Returns:
            OpenAIEmbeddings instance
        """
        model_name = model_name or "text-embedding-3-small"

        embeddings = OpenAIEmbeddings(
            model=model_name,
            openai_api_key=api_key
        )

        # Set dimension based on model
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        self.embedding_dimension = dimension_map.get(model_name, 1536)

        return embeddings

    def _init_cohere_embeddings(
        self,
        model_name: str = None,
        api_key: str = None
    ) -> CohereEmbeddings:
        """
        Initialize Cohere embeddings

        Args:
            model_name: Cohere model name (default: "embed-multilingual-v3.0")
            api_key: Cohere API key

        Returns:
            CohereEmbeddings instance
        """
        model_name = model_name or "embed-multilingual-v3.0"

        embeddings = CohereEmbeddings(
            model=model_name,
            cohere_api_key=api_key
        )

        # Set dimension based on model
        dimension_map = {
            "embed-multilingual-v3.0": 1024,
            "embed-english-v3.0": 1024,
            "embed-multilingual-light-v3.0": 384,
            "embed-english-light-v3.0": 384
        }
        self.embedding_dimension = dimension_map.get(model_name, 1024)

        return embeddings

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of documents

        Args:
            texts: List of text documents

        Returns:
            List of embedding vectors
        """
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single query

        Args:
            text: Query text

        Returns:
            Embedding vector
        """
        return self.embeddings.embed_query(text)

    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings"""
        return self.embedding_dimension

    def get_provider_info(self) -> dict:
        """Get information about the embeddings provider"""
        return {
            "provider": self.provider,
            "dimension": self.embedding_dimension,
            "device": self.device if self.provider == "local" else "cloud"
        }


@lru_cache(maxsize=1)
def get_embeddings_instance(
    provider: str = "local",
    model_name: str = None,
    api_key: str = None,
    device: str = "cpu"
) -> EmbeddingsService:
    """
    Get cached embeddings instance (singleton pattern)
    This ensures the model is loaded only once in memory

    Args:
        provider: Embedding provider
        model_name: Model name
        api_key: API key
        device: Device for local embeddings

    Returns:
        Cached EmbeddingsService instance
    """
    return EmbeddingsService(
        provider=provider,
        model_name=model_name,
        api_key=api_key,
        device=device
    )
