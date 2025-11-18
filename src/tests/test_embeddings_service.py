"""
Tests for EmbeddingsService
"""

import pytest
from services import EmbeddingsService


class TestEmbeddingsServiceLocal:
    """Test suite for EmbeddingsService with local provider"""

    def test_init_local_default(self):
        """Test initialization with local provider and default model"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",  # Use mini for faster tests
            device="cpu"
        )

        assert service.provider == "local"
        assert service.device == "cpu"
        assert service.embeddings is not None
        assert service.embedding_dimension > 0

    def test_init_local_custom_model(self):
        """Test initialization with custom HuggingFace model"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        assert service.embedding_dimension > 0

    def test_embed_query_local(self):
        """Test embedding a single query with local provider"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        vector = service.embed_query("Test en français")

        assert isinstance(vector, list)
        assert len(vector) == service.embedding_dimension
        assert all(isinstance(x, float) for x in vector)

    def test_embed_documents_local(self):
        """Test embedding multiple documents with local provider"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        texts = [
            "Premier document",
            "Deuxième document",
            "Troisième document"
        ]

        vectors = service.embed_documents(texts)

        assert isinstance(vectors, list)
        assert len(vectors) == 3
        assert all(len(vec) == service.embedding_dimension for vec in vectors)

    def test_embed_multilingual(self):
        """Test embedding texts in different languages"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        texts = [
            "Hello world",  # English
            "Bonjour le monde",  # French
            "مرحبا بالعالم"  # Arabic
        ]

        vectors = service.embed_documents(texts)

        assert len(vectors) == 3
        assert all(len(vec) == service.embedding_dimension for vec in vectors)

    def test_get_embedding_dimension(self):
        """Test getting embedding dimension"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        dimension = service.get_embedding_dimension()

        assert isinstance(dimension, int)
        assert dimension > 0

    def test_get_provider_info(self):
        """Test getting provider information"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        info = service.get_provider_info()

        assert "provider" in info
        assert "dimension" in info
        assert "device" in info
        assert info["provider"] == "local"
        assert info["device"] == "cpu"

    def test_embedding_consistency(self):
        """Test that same text produces same embedding"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        text = "Test de cohérence"

        vec1 = service.embed_query(text)
        vec2 = service.embed_query(text)

        # Should produce identical embeddings
        assert vec1 == vec2


class TestEmbeddingsServiceOpenAI:
    """Test suite for EmbeddingsService with OpenAI provider"""

    def test_init_openai(self, openai_api_key):
        """Test initialization with OpenAI provider"""
        service = EmbeddingsService(
            provider="openai",
            model_name="text-embedding-3-small",
            api_key=openai_api_key
        )

        assert service.provider == "openai"
        assert service.embedding_dimension == 1536

    def test_embed_query_openai(self, openai_api_key):
        """Test embedding with OpenAI"""
        service = EmbeddingsService(
            provider="openai",
            model_name="text-embedding-3-small",
            api_key=openai_api_key
        )

        vector = service.embed_query("Test query")

        assert len(vector) == 1536


class TestEmbeddingsServiceCohere:
    """Test suite for EmbeddingsService with Cohere provider"""

    def test_init_cohere(self, cohere_api_key):
        """Test initialization with Cohere provider"""
        service = EmbeddingsService(
            provider="cohere",
            model_name="embed-multilingual-v3.0",
            api_key=cohere_api_key
        )

        assert service.provider == "cohere"
        assert service.embedding_dimension == 1024

    def test_embed_query_cohere(self, cohere_api_key):
        """Test embedding with Cohere"""
        service = EmbeddingsService(
            provider="cohere",
            model_name="embed-multilingual-v3.0",
            api_key=cohere_api_key
        )

        vector = service.embed_query("Test query")

        assert len(vector) == 1024


class TestEmbeddingsServiceErrors:
    """Test error handling"""

    def test_invalid_provider(self):
        """Test initialization with invalid provider"""
        with pytest.raises(ValueError, match="Unsupported provider"):
            EmbeddingsService(
                provider="invalid_provider",
                device="cpu"
            )
