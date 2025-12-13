"""
Tests unitaires pour ProcessController
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document


@pytest.mark.unit
class TestProcessController:
    """Tests pour ProcessController"""

    @pytest.fixture
    def mock_document_service(self):
        """Mock DocumentService"""
        mock = Mock()
        mock.chunk_size = 1000
        mock.chunk_overlap = 200
        return mock

    @pytest.fixture
    def controller(self, mock_document_service):
        """Créer ProcessController avec DocumentService mocké"""
        with patch('controllers.ProcessController.DocumentService', return_value=mock_document_service):
            with patch('controllers.ProcessController.ProjectController') as mock_project_ctrl:
                mock_project_ctrl.return_value.get_project_path.return_value = "/fake/path"

                from controllers.ProcessController import ProcessController

                controller = ProcessController(project_id="test_project")
                controller.doc_service = mock_document_service

                return controller

    def test_initialization_default_params(self):
        """Test initialisation avec paramètres par défaut"""
        with patch('controllers.ProcessController.DocumentService') as mock_ds:
            with patch('controllers.ProcessController.ProjectController') as mock_pc:
                mock_pc.return_value.get_project_path.return_value = "/fake/path"

                from controllers.ProcessController import ProcessController

                # Act
                controller = ProcessController(project_id="test_project")

                # Assert
                assert controller.project_id == "test_project"
                assert controller.project_path == "/fake/path"
                # Vérifier que DocumentService a été appelé avec les bons params
                mock_ds.assert_called_once()
                call_kwargs = mock_ds.call_args[1]
                assert call_kwargs['chunk_size'] == 1000
                assert call_kwargs['chunk_overlap'] == 200

    def test_initialization_custom_params(self):
        """Test initialisation avec paramètres personnalisés"""
        with patch('controllers.ProcessController.DocumentService') as mock_ds:
            with patch('controllers.ProcessController.ProjectController') as mock_pc:
                mock_pc.return_value.get_project_path.return_value = "/fake/path"

                from controllers.ProcessController import ProcessController

                # Act
                controller = ProcessController(
                    project_id="custom_project",
                    chunk_size=500,
                    chunk_overlap=100
                )

                # Assert
                call_kwargs = mock_ds.call_args[1]
                assert call_kwargs['chunk_size'] == 500
                assert call_kwargs['chunk_overlap'] == 100

    def test_get_file_content_success(self, controller, mock_document_service):
        """Test chargement de fichier réussi"""
        # Arrange
        file_id = "test_file.pdf"
        expected_docs = [
            Document(page_content="Content 1"),
            Document(page_content="Content 2")
        ]
        mock_document_service.load_document.return_value = expected_docs

        # Act
        result = controller.get_file_content(file_id)

        # Assert
        assert result == expected_docs
        mock_document_service.load_document.assert_called_once_with(file_id)

    def test_get_file_content_returns_none(self, controller, mock_document_service):
        """Test chargement de fichier qui retourne None"""
        # Arrange
        file_id = "nonexistent.pdf"
        mock_document_service.load_document.return_value = None

        # Act
        result = controller.get_file_content(file_id)

        # Assert
        assert result is None

    def test_process_file_content_default_params(self, controller, mock_document_service):
        """Test traitement de contenu avec paramètres par défaut"""
        # Arrange
        file_content = [Document(page_content="Test content")]
        file_id = "abc123_document.pdf"

        chunked_docs = [
            Document(page_content="Chunk 1", metadata={}),
            Document(page_content="Chunk 2", metadata={})
        ]
        mock_document_service.chunk_documents.return_value = chunked_docs

        # Act
        result = controller.process_file_content(file_content, file_id)

        # Assert
        assert len(result) == 2
        # Vérifier que file_id et filename ont été ajoutés aux metadata
        for chunk in result:
            assert chunk.metadata["file_id"] == file_id
            assert chunk.metadata["filename"] == "document.pdf"

    def test_process_file_content_custom_params(self, controller):
        """Test traitement avec paramètres personnalisés"""
        with patch('controllers.ProcessController.DocumentService') as mock_ds_class:
            # Arrange
            temp_service = Mock()
            chunked_docs = [Document(page_content="Chunk", metadata={})]
            temp_service.chunk_documents.return_value = chunked_docs
            mock_ds_class.return_value = temp_service

            file_content = [Document(page_content="Content")]
            file_id = "test_file.pdf"

            # Act
            result = controller.process_file_content(
                file_content,
                file_id,
                chunk_size=2000,
                overlap_size=400
            )

            # Assert
            # Vérifier qu'un nouveau service temporaire a été créé
            mock_ds_class.assert_called_once()
            call_kwargs = mock_ds_class.call_args[1]
            assert call_kwargs['chunk_size'] == 2000
            assert call_kwargs['chunk_overlap'] == 400

    def test_process_file_content_adds_filename_metadata(self, controller, mock_document_service):
        """Test que le filename est correctement extrait du file_id"""
        # Arrange
        file_id = "xyz789_Report_2024.pdf"
        file_content = [Document(page_content="Content")]
        chunked_docs = [Document(page_content="Chunk", metadata={})]
        mock_document_service.chunk_documents.return_value = chunked_docs

        # Act
        result = controller.process_file_content(file_content, file_id)

        # Assert
        assert result[0].metadata["filename"] == "Report_2024.pdf"

    def test_process_file_content_file_id_without_prefix(self, controller, mock_document_service):
        """Test avec file_id sans préfixe (pas d'underscore)"""
        # Arrange
        file_id = "simple.pdf"
        file_content = [Document(page_content="Content")]
        chunked_docs = [Document(page_content="Chunk", metadata={})]
        mock_document_service.chunk_documents.return_value = chunked_docs

        # Act
        result = controller.process_file_content(file_content, file_id)

        # Assert
        # Si pas d'underscore, filename = file_id
        assert result[0].metadata["filename"] == file_id

    def test_process_file_success(self, controller, mock_document_service):
        """Test pipeline complet réussi"""
        # Arrange
        file_id = "test_document.pdf"

        loaded_docs = [Document(page_content="Original content")]
        chunked_docs = [
            Document(page_content="Chunk 1", metadata={}),
            Document(page_content="Chunk 2", metadata={})
        ]

        mock_document_service.load_document.return_value = loaded_docs
        mock_document_service.chunk_documents.return_value = chunked_docs

        # Act
        result = controller.process_file(file_id)

        # Assert
        assert result is not None
        assert len(result) == 2
        mock_document_service.load_document.assert_called_once_with(file_id)

    def test_process_file_returns_none_when_load_fails(self, controller, mock_document_service):
        """Test pipeline retourne None si chargement échoue"""
        # Arrange
        file_id = "nonexistent.pdf"
        mock_document_service.load_document.return_value = None

        # Act
        result = controller.process_file(file_id)

        # Assert
        assert result is None
        # chunk_documents ne doit pas être appelé
        mock_document_service.chunk_documents.assert_not_called()

    def test_process_file_with_custom_chunk_params(self, controller, mock_document_service):
        """Test pipeline avec paramètres de chunking personnalisés"""
        with patch('controllers.ProcessController.DocumentService') as mock_ds_class:
            # Arrange
            loaded_docs = [Document(page_content="Content")]
            mock_document_service.load_document.return_value = loaded_docs

            temp_service = Mock()
            chunked_docs = [Document(page_content="Chunk", metadata={})]
            temp_service.chunk_documents.return_value = chunked_docs
            mock_ds_class.return_value = temp_service

            # Act
            result = controller.process_file(
                "test.pdf",
                chunk_size=1500,
                overlap_size=300
            )

            # Assert
            assert result is not None
            mock_ds_class.assert_called_once()

    def test_get_chunks_stats(self, controller, mock_document_service):
        """Test récupération des statistiques de chunks"""
        # Arrange
        chunks = [
            Document(page_content="Chunk 1"),
            Document(page_content="Chunk 2"),
            Document(page_content="Chunk 3")
        ]
        expected_stats = {
            'total_chunks': 3,
            'avg_chunk_size': 100,
            'min_chunk_size': 80,
            'max_chunk_size': 120
        }
        mock_document_service.get_chunks_stats.return_value = expected_stats

        # Act
        result = controller.get_chunks_stats(chunks)

        # Assert
        assert result == expected_stats
        mock_document_service.get_chunks_stats.assert_called_once_with(chunks)

    def test_get_file_extension(self, controller, mock_document_service):
        """Test récupération de l'extension de fichier"""
        # Arrange
        file_id = "document.pdf"
        mock_document_service.get_file_extension.return_value = ".pdf"

        # Act
        result = controller.get_file_extension(file_id)

        # Assert
        assert result == ".pdf"
        mock_document_service.get_file_extension.assert_called_once_with(file_id)

    def test_get_file_extension_various_types(self, controller, mock_document_service):
        """Test avec différents types de fichiers"""
        test_cases = [
            ("file.txt", ".txt"),
            ("document.docx", ".docx"),
            ("data.csv", ".csv"),
            ("image.png", ".png")
        ]

        for file_id, expected_ext in test_cases:
            mock_document_service.get_file_extension.return_value = expected_ext

            # Act
            result = controller.get_file_extension(file_id)

            # Assert
            assert result == expected_ext
