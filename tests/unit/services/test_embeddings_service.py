"""
Tests for EmbeddingsService
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
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


class TestEmbeddingsServiceOpenAIMocked:
    """Test OpenAI provider with mocks (pour éviter vraie API)"""

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_init_openai_mocked(self, mock_openai_class):
        """Test init OpenAI avec mock"""
        # Mock OpenAIEmbeddings
        mock_embeddings = Mock()
        mock_openai_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="openai",
            model_name="text-embedding-3-small",
            api_key="fake_key"
        )

        # Assert
        assert service.provider == "openai"
        assert service.embedding_dimension == 1536
        mock_openai_class.assert_called_once_with(
            model="text-embedding-3-small",
            openai_api_key="fake_key"
        )

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_init_openai_large_model(self, mock_openai_class):
        """Test init OpenAI avec text-embedding-3-large"""
        mock_embeddings = Mock()
        mock_openai_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="openai",
            model_name="text-embedding-3-large",
            api_key="fake_key"
        )

        # Assert
        assert service.embedding_dimension == 3072

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_init_openai_ada_model(self, mock_openai_class):
        """Test init OpenAI avec text-embedding-ada-002"""
        mock_embeddings = Mock()
        mock_openai_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="openai",
            model_name="text-embedding-ada-002",
            api_key="fake_key"
        )

        # Assert
        assert service.embedding_dimension == 1536

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_init_openai_default_model(self, mock_openai_class):
        """Test init OpenAI sans model_name (utilise default)"""
        mock_embeddings = Mock()
        mock_openai_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="openai",
            api_key="fake_key"
        )

        # Assert
        mock_openai_class.assert_called_once_with(
            model="text-embedding-3-small",
            openai_api_key="fake_key"
        )
        assert service.embedding_dimension == 1536

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_embed_documents_openai_mocked(self, mock_openai_class):
        """Test embed_documents avec OpenAI mocké"""
        # Mock embeddings
        mock_embeddings = Mock()
        mock_vectors = [[0.1] * 1536, [0.2] * 1536]
        mock_embeddings.embed_documents.return_value = mock_vectors
        mock_openai_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(provider="openai", api_key="fake_key")
        result = service.embed_documents(["text1", "text2"])

        # Assert
        assert result == mock_vectors
        mock_embeddings.embed_documents.assert_called_once_with(["text1", "text2"])

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_embed_query_openai_mocked(self, mock_openai_class):
        """Test embed_query avec OpenAI mocké"""
        # Mock embeddings
        mock_embeddings = Mock()
        mock_vector = [0.1] * 1536
        mock_embeddings.embed_query.return_value = mock_vector
        mock_openai_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(provider="openai", api_key="fake_key")
        result = service.embed_query("test query")

        # Assert
        assert result == mock_vector
        mock_embeddings.embed_query.assert_called_once_with("test query")


class TestEmbeddingsServiceCohereMocked:
    """Test Cohere provider with mocks"""

    @patch('services.embeddings_service.CohereEmbeddings')
    def test_init_cohere_mocked(self, mock_cohere_class):
        """Test init Cohere avec mock"""
        mock_embeddings = Mock()
        mock_cohere_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="cohere",
            model_name="embed-multilingual-v3.0",
            api_key="fake_key"
        )

        # Assert
        assert service.provider == "cohere"
        assert service.embedding_dimension == 1024
        mock_cohere_class.assert_called_once_with(
            model="embed-multilingual-v3.0",
            cohere_api_key="fake_key"
        )

    @patch('services.embeddings_service.CohereEmbeddings')
    def test_init_cohere_english_model(self, mock_cohere_class):
        """Test init Cohere avec embed-english-v3.0"""
        mock_embeddings = Mock()
        mock_cohere_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="cohere",
            model_name="embed-english-v3.0",
            api_key="fake_key"
        )

        # Assert
        assert service.embedding_dimension == 1024

    @patch('services.embeddings_service.CohereEmbeddings')
    def test_init_cohere_light_model(self, mock_cohere_class):
        """Test init Cohere avec embed-multilingual-light-v3.0"""
        mock_embeddings = Mock()
        mock_cohere_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="cohere",
            model_name="embed-multilingual-light-v3.0",
            api_key="fake_key"
        )

        # Assert
        assert service.embedding_dimension == 384

    @patch('services.embeddings_service.CohereEmbeddings')
    def test_init_cohere_default_model(self, mock_cohere_class):
        """Test init Cohere sans model_name (utilise default)"""
        mock_embeddings = Mock()
        mock_cohere_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(
            provider="cohere",
            api_key="fake_key"
        )

        # Assert
        mock_cohere_class.assert_called_once_with(
            model="embed-multilingual-v3.0",
            cohere_api_key="fake_key"
        )
        assert service.embedding_dimension == 1024

    @patch('services.embeddings_service.CohereEmbeddings')
    def test_embed_documents_cohere_mocked(self, mock_cohere_class):
        """Test embed_documents avec Cohere mocké"""
        mock_embeddings = Mock()
        mock_vectors = [[0.1] * 1024, [0.2] * 1024]
        mock_embeddings.embed_documents.return_value = mock_vectors
        mock_cohere_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(provider="cohere", api_key="fake_key")
        result = service.embed_documents(["text1", "text2"])

        # Assert
        assert result == mock_vectors
        mock_embeddings.embed_documents.assert_called_once_with(["text1", "text2"])

    @patch('services.embeddings_service.CohereEmbeddings')
    def test_embed_query_cohere_mocked(self, mock_cohere_class):
        """Test embed_query avec Cohere mocké"""
        mock_embeddings = Mock()
        mock_vector = [0.1] * 1024
        mock_embeddings.embed_query.return_value = mock_vector
        mock_cohere_class.return_value = mock_embeddings

        # Act
        service = EmbeddingsService(provider="cohere", api_key="fake_key")
        result = service.embed_query("test query")

        # Assert
        assert result == mock_vector
        mock_embeddings.embed_query.assert_called_once_with("test query")


class TestEmbeddingsServiceLocalExtended:
    """Tests supplémentaires pour local provider"""

    def test_init_local_default_model_name(self):
        """Test init local avec model_name=None (utilise multilingual par défaut)"""
        # Act
        service = EmbeddingsService(
            provider="local",
            model_name=None,  # Devrait utiliser "multilingual" par défaut
            device="cpu"
        )

        # Assert
        assert service.provider == "local"
        assert service.embeddings is not None
        assert service.embedding_dimension > 0

    def test_init_local_preset_model(self):
        """Test init local avec preset model key"""
        # Act
        service = EmbeddingsService(
            provider="local",
            model_name="english-mini",  # Preset key
            device="cpu"
        )

        # Assert
        assert service.embedding_dimension > 0

    def test_get_provider_info_local(self):
        """Test get_provider_info pour local provider"""
        service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        # Act
        info = service.get_provider_info()

        # Assert
        assert info["provider"] == "local"
        assert info["device"] == "cpu"
        assert info["dimension"] > 0

    @patch('services.embeddings_service.OpenAIEmbeddings')
    def test_get_provider_info_cloud(self, mock_openai_class):
        """Test get_provider_info pour cloud provider"""
        mock_embeddings = Mock()
        mock_openai_class.return_value = mock_embeddings

        service = EmbeddingsService(
            provider="openai",
            api_key="fake_key"
        )

        # Act
        info = service.get_provider_info()

        # Assert
        assert info["provider"] == "openai"
        assert info["device"] == "cloud"


class TestEmbeddingsGetInstance:
    """Tests pour la fonction factory get_embeddings_instance"""

    @patch('services.embeddings_service.EmbeddingsService')
    def test_get_embeddings_instance_called(self, mock_service_class):
        """Test que get_embeddings_instance crée une instance"""
        from services.embeddings_service import get_embeddings_instance

        # Clear cache first
        get_embeddings_instance.cache_clear()

        mock_instance = Mock()
        mock_service_class.return_value = mock_instance

        # Act
        result = get_embeddings_instance(
            provider="local",
            model_name="test",
            device="cpu"
        )

        # Assert
        mock_service_class.assert_called_once_with(
            provider="local",
            model_name="test",
            api_key=None,
            device="cpu"
        )

    def test_get_embeddings_instance_caching(self):
        """Test que get_embeddings_instance utilise le cache"""
        from services.embeddings_service import get_embeddings_instance

        # Clear cache first
        get_embeddings_instance.cache_clear()

        # Act
        instance1 = get_embeddings_instance(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        instance2 = get_embeddings_instance(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        # Assert - should be same instance (cached)
        assert instance1 is instance2
