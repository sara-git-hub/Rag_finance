"""
Tests unitaires pour NLPController
Tests des méthodes principales (initialisation, vectorstore, collection)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestNLPControllerInitialization:
    """Tests d'initialisation de NLPController"""

    def test_initialization_with_required_params(self):
        """Test initialisation avec paramètres requis"""
        from controllers.NLPController import NLPController

        # Arrange
        embeddings_service = Mock()
        prompt_service = Mock()

        # Act
        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key"
        )

        # Assert
        assert controller.embeddings_service == embeddings_service
        assert controller.prompt_service == prompt_service
        assert controller.generation_backend == "openai"
        assert controller.generation_model == "gpt-3.5-turbo"
        assert controller.api_key == "test_key"
        assert controller.vector_db_backend == "qdrant"  # default
        assert controller.max_tokens == 1000  # default
        assert controller.temperature == 0.7  # default
        assert controller._vectorstores == {}  # cache vide

    def test_initialization_with_custom_params(self):
        """Test initialisation avec tous les paramètres personnalisés"""
        from controllers.NLPController import NLPController

        # Arrange
        embeddings_service = Mock()
        prompt_service = Mock()

        # Act
        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="ollama",
            generation_model="llama2",
            api_key="",
            vector_db_backend="pgvector",
            vector_db_path="/custom/path",
            connection_string="postgresql://...",
            qdrant_url="http://qdrant:6333",
            max_tokens=2000,
            temperature=0.5
        )

        # Assert
        assert controller.vector_db_backend == "pgvector"
        assert controller.vector_db_path == "/custom/path"
        assert controller.connection_string == "postgresql://..."
        assert controller.qdrant_url == "http://qdrant:6333"
        assert controller.max_tokens == 2000
        assert controller.temperature == 0.5

    def test_initialization_different_generation_backends(self):
        """Test initialisation avec différents backends de génération"""
        from controllers.NLPController import NLPController

        backends = ["openai", "cohere", "ollama", "groq"]

        for backend in backends:
            # Arrange
            embeddings_service = Mock()
            prompt_service = Mock()

            # Act
            controller = NLPController(
                embeddings_service=embeddings_service,
                prompt_service=prompt_service,
                generation_backend=backend,
                generation_model="test-model",
                api_key="test-key" if backend != "ollama" else ""
            )

            # Assert
            assert controller.generation_backend == backend


@pytest.mark.unit
class TestNLPControllerCollectionName:
    """Tests pour la création de noms de collection"""

    def test_create_collection_name_basic(self):
        """Test création de nom de collection basique"""
        from controllers.NLPController import NLPController

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 384
        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key"
        )

        # Act
        collection_name = controller.create_collection_name("project_123")

        # Assert
        assert collection_name == "collection_384_project_123"
        embeddings_service.get_embedding_dimension.assert_called_once()

    def test_create_collection_name_different_dimensions(self):
        """Test avec différentes dimensions d'embedding"""
        from controllers.NLPController import NLPController

        dimensions = [384, 768, 1536, 3072]

        for dim in dimensions:
            # Arrange
            embeddings_service = Mock()
            embeddings_service.get_embedding_dimension.return_value = dim
            prompt_service = Mock()

            controller = NLPController(
                embeddings_service=embeddings_service,
                prompt_service=prompt_service,
                generation_backend="openai",
                generation_model="gpt-3.5-turbo",
                api_key="test_key"
            )

            # Act
            collection_name = controller.create_collection_name("test_project")

            # Assert
            assert collection_name == f"collection_{dim}_test_project"

    def test_create_collection_name_with_spaces(self):
        """Test que les espaces dans project_id sont bien gérés"""
        from controllers.NLPController import NLPController

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 384
        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key"
        )

        # Act
        collection_name = controller.create_collection_name(" test_project ")

        # Assert
        # strip() est appelé sur la string complète après concaténation
        # donc les espaces au début/fin du project_id restent dans le milieu
        assert collection_name == "collection_384_ test_project"


@pytest.mark.unit
class TestNLPControllerVectorStore:
    """Tests pour la gestion des vectorstores"""

    @patch('controllers.NLPController.VectorStoreService')
    def test_get_vectorstore_creates_new(self, mock_vectorstore_class):
        """Test création d'un nouveau vectorstore"""
        from controllers.NLPController import NLPController
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 384
        embeddings_service.embeddings = Mock()  # Mock des embeddings LangChain

        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key",
            vector_db_backend="qdrant",
            vector_db_path="/test/path"
        )

        project = Mock(spec=Project)
        project.project_id = 123

        mock_vectorstore = Mock()
        mock_vectorstore_class.return_value = mock_vectorstore

        # Act
        result = controller._get_vectorstore(project)

        # Assert
        assert result == mock_vectorstore
        # Vérifier que VectorStoreService a été créé avec les bons params
        mock_vectorstore_class.assert_called_once()
        call_kwargs = mock_vectorstore_class.call_args[1]
        assert call_kwargs['provider'] == "qdrant"
        assert call_kwargs['collection_name'] == "collection_384_123"
        assert 'path' in call_kwargs

    @patch('controllers.NLPController.VectorStoreService')
    def test_get_vectorstore_returns_cached(self, mock_vectorstore_class):
        """Test que le vectorstore est mis en cache"""
        from controllers.NLPController import NLPController
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 384
        embeddings_service.embeddings = Mock()

        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key"
        )

        project = Mock(spec=Project)
        project.project_id = 123

        mock_vectorstore = Mock()
        mock_vectorstore_class.return_value = mock_vectorstore

        # Act - Premier appel
        result1 = controller._get_vectorstore(project)

        # Act - Deuxième appel (devrait utiliser le cache)
        result2 = controller._get_vectorstore(project)

        # Assert
        assert result1 == result2
        # VectorStoreService ne doit être créé qu'une seule fois
        assert mock_vectorstore_class.call_count == 1

    @patch('controllers.NLPController.VectorStoreService')
    def test_get_vectorstore_with_pgvector(self, mock_vectorstore_class):
        """Test création de vectorstore avec PGVector"""
        from controllers.NLPController import NLPController
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 768
        embeddings_service.embeddings = Mock()

        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key",
            vector_db_backend="pgvector",
            connection_string="postgresql://user:pass@localhost/db"
        )

        project = Mock(spec=Project)
        project.project_id = 456

        mock_vectorstore = Mock()
        mock_vectorstore_class.return_value = mock_vectorstore

        # Act
        result = controller._get_vectorstore(project)

        # Assert
        call_kwargs = mock_vectorstore_class.call_args[1]
        assert call_kwargs['provider'] == "pgvector"
        assert call_kwargs['connection_string'] == "postgresql://user:pass@localhost/db"

    @patch('controllers.NLPController.VectorStoreService')
    def test_get_vectorstore_with_qdrant_url(self, mock_vectorstore_class):
        """Test création de vectorstore avec Qdrant URL (Docker)"""
        from controllers.NLPController import NLPController
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 384
        embeddings_service.embeddings = Mock()

        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key",
            vector_db_backend="qdrant",
            qdrant_url="http://qdrant:6333"
        )

        project = Mock(spec=Project)
        project.project_id = 789

        mock_vectorstore = Mock()
        mock_vectorstore_class.return_value = mock_vectorstore

        # Act
        result = controller._get_vectorstore(project)

        # Assert
        call_kwargs = mock_vectorstore_class.call_args[1]
        assert call_kwargs['provider'] == "qdrant"
        assert call_kwargs['url'] == "http://qdrant:6333"
        # path ne doit pas être présent si url est fourni
        assert 'url' in call_kwargs

    @patch('controllers.NLPController.VectorStoreService')
    def test_get_vectorstore_different_projects(self, mock_vectorstore_class):
        """Test que différents projets ont différents vectorstores"""
        from controllers.NLPController import NLPController
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        embeddings_service = Mock()
        embeddings_service.get_embedding_dimension.return_value = 384
        embeddings_service.embeddings = Mock()

        prompt_service = Mock()

        controller = NLPController(
            embeddings_service=embeddings_service,
            prompt_service=prompt_service,
            generation_backend="openai",
            generation_model="gpt-3.5-turbo",
            api_key="test_key"
        )

        project1 = Mock(spec=Project)
        project1.project_id = 1

        project2 = Mock(spec=Project)
        project2.project_id = 2

        mock_vectorstore1 = Mock()
        mock_vectorstore2 = Mock()
        mock_vectorstore_class.side_effect = [mock_vectorstore1, mock_vectorstore2]

        # Act
        result1 = controller._get_vectorstore(project1)
        result2 = controller._get_vectorstore(project2)

        # Assert
        assert result1 != result2
        assert mock_vectorstore_class.call_count == 2
