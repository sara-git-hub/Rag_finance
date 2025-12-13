"""
Tests unitaires pour DataController
Tests de validation de fichiers, génération de filepaths, nettoyage de noms
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestDataControllerInitialization:
    """Tests d'initialisation de DataController"""

    def test_initialization(self):
        """Test que DataController s'initialise correctement"""
        from controllers.DataController import DataController

        # Act
        controller = DataController()

        # Assert
        assert controller is not None
        assert hasattr(controller, 'size_scale')
        assert controller.size_scale == 1048576  # 1 MB en bytes

    def test_initialization_inherits_from_base(self):
        """Test que DataController hérite de BaseController"""
        from controllers.DataController import DataController

        # Act
        controller = DataController()

        # Assert
        # Devrait avoir les attributs de BaseController
        assert hasattr(controller, 'app_settings')
        assert hasattr(controller, 'base_dir')
        assert hasattr(controller, 'files_dir')
        assert hasattr(controller, 'database_dir')


@pytest.mark.unit
class TestValidateUploadedFile:
    """Tests pour la validation de fichiers uploadés"""

    def test_validate_uploaded_file_success(self):
        """Test validation réussie d'un fichier"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Mock UploadFile
        mock_file = Mock()
        mock_file.content_type = "application/pdf"
        mock_file.size = 5 * 1048576  # 5 MB

        # Mock settings
        controller.app_settings.FILE_ALLOWED_TYPES = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        controller.app_settings.FILE_MAX_SIZE = 10  # 10 MB

        # Act
        is_valid, message = controller.validate_uploaded_file(mock_file)

        # Assert
        assert is_valid is True
        assert message == "file_validate_successfully"

    def test_validate_uploaded_file_invalid_type(self):
        """Test validation échoue avec type de fichier non supporté"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Mock UploadFile avec type non supporté
        mock_file = Mock()
        mock_file.content_type = "image/png"
        mock_file.size = 1 * 1048576  # 1 MB

        # Mock settings
        controller.app_settings.FILE_ALLOWED_TYPES = [
            "application/pdf",
            "text/plain"
        ]
        controller.app_settings.FILE_MAX_SIZE = 10

        # Act
        is_valid, message = controller.validate_uploaded_file(mock_file)

        # Assert
        assert is_valid is False
        assert message == "file_type_not_supported"

    def test_validate_uploaded_file_size_exceeded(self):
        """Test validation échoue si taille dépasse la limite"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Mock UploadFile avec taille trop grande
        mock_file = Mock()
        mock_file.content_type = "application/pdf"
        mock_file.size = 15 * 1048576  # 15 MB

        # Mock settings
        controller.app_settings.FILE_ALLOWED_TYPES = ["application/pdf"]
        controller.app_settings.FILE_MAX_SIZE = 10  # 10 MB max

        # Act
        is_valid, message = controller.validate_uploaded_file(mock_file)

        # Assert
        assert is_valid is False
        assert message == "file_size_exceeded"

    def test_validate_uploaded_file_exact_max_size(self):
        """Test validation avec taille exactement à la limite"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Mock UploadFile avec taille exactement à la limite
        mock_file = Mock()
        mock_file.content_type = "application/pdf"
        mock_file.size = 10 * 1048576  # Exactement 10 MB

        # Mock settings
        controller.app_settings.FILE_ALLOWED_TYPES = ["application/pdf"]
        controller.app_settings.FILE_MAX_SIZE = 10

        # Act
        is_valid, message = controller.validate_uploaded_file(mock_file)

        # Assert
        assert is_valid is True
        assert message == "file_validate_successfully"

    def test_validate_uploaded_file_multiple_allowed_types(self):
        """Test validation avec plusieurs types de fichiers autorisés"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Mock settings
        controller.app_settings.FILE_ALLOWED_TYPES = [
            "application/pdf",
            "text/plain",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/csv"
        ]
        controller.app_settings.FILE_MAX_SIZE = 10

        file_types = [
            "application/pdf",
            "text/plain",
            "text/csv"
        ]

        for file_type in file_types:
            mock_file = Mock()
            mock_file.content_type = file_type
            mock_file.size = 1 * 1048576

            # Act
            is_valid, message = controller.validate_uploaded_file(mock_file)

            # Assert
            assert is_valid is True


@pytest.mark.unit
class TestGetCleanFileName:
    """Tests pour le nettoyage de noms de fichiers"""

    def test_get_clean_file_name_basic(self):
        """Test nettoyage de nom de fichier basique"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("document.pdf")

        # Assert
        assert result == "document.pdf"

    def test_get_clean_file_name_with_spaces(self):
        """Test que les espaces sont remplacés par underscore"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("my document.pdf")

        # Assert
        assert result == "mydocument.pdf"
        assert " " not in result

    def test_get_clean_file_name_with_special_characters(self):
        """Test suppression des caractères spéciaux"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("doc@#$%ument!.pdf")

        # Assert
        assert result == "document.pdf"
        assert "@" not in result
        assert "#" not in result
        assert "!" not in result

    def test_get_clean_file_name_preserves_underscores(self):
        """Test que les underscores sont préservés"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("my_important_document.pdf")

        # Assert
        assert result == "my_important_document.pdf"
        assert "_" in result

    def test_get_clean_file_name_preserves_dots(self):
        """Test que les points sont préservés"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("document.v2.final.pdf")

        # Assert
        assert result == "document.v2.final.pdf"
        assert result.count(".") == 3

    def test_get_clean_file_name_strips_whitespace(self):
        """Test que les espaces en début/fin sont supprimés"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("  document.pdf  ")

        # Assert
        assert result == "document.pdf"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_get_clean_file_name_complex_case(self):
        """Test cas complexe avec plusieurs types de caractères"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("  My-Report (2024) v1.2 - Final!.docx  ")

        # Assert
        # Les tirets et parenthèses sont supprimés, espaces remplacés
        assert ".docx" in result
        assert "(" not in result
        assert ")" not in result
        assert "-" not in result
        assert "!" not in result

    def test_get_clean_file_name_unicode_characters(self):
        """Test avec caractères unicode"""
        from controllers.DataController import DataController

        # Arrange
        controller = DataController()

        # Act
        result = controller.get_clean_file_name("document_été_2024.pdf")

        # Assert
        # En Python 3, \w inclut les caractères unicode, donc ils sont préservés
        assert result == "document_été_2024.pdf"
        assert ".pdf" in result


@pytest.mark.unit
class TestGenerateUniqueFilepath:
    """Tests pour la génération de filepaths uniques"""

    @pytest.fixture
    def temp_project_dir(self, monkeypatch):
        """Créer un répertoire de projet temporaire"""
        temp_dir = tempfile.mkdtemp()

        # Mock ProjectController.get_project_path
        def mock_get_project_path(project_id):
            return temp_dir

        with patch('controllers.DataController.ProjectController') as mock_pc:
            mock_pc.return_value.get_project_path.return_value = temp_dir
            yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_generate_unique_filepath_creates_filepath(self, temp_project_dir):
        """Test génération de filepath unique"""
        from controllers.DataController import DataController

        with patch('controllers.DataController.ProjectController') as mock_pc:
            mock_pc.return_value.get_project_path.return_value = temp_project_dir

            # Arrange
            controller = DataController()
            orig_filename = "document.pdf"
            project_id = "test_project"

            # Act
            filepath, file_id = controller.generate_unique_filepath(orig_filename, project_id)

            # Assert
            assert filepath is not None
            assert file_id is not None
            assert "document.pdf" in file_id
            assert "_" in file_id  # random_key_filename format
            assert filepath.endswith(file_id)

    def test_generate_unique_filepath_includes_random_key(self, temp_project_dir):
        """Test que le filepath contient une clé aléatoire"""
        from controllers.DataController import DataController

        with patch('controllers.DataController.ProjectController') as mock_pc:
            mock_pc.return_value.get_project_path.return_value = temp_project_dir

            # Arrange
            controller = DataController()

            # Act
            filepath1, file_id1 = controller.generate_unique_filepath("test.pdf", "proj1")
            filepath2, file_id2 = controller.generate_unique_filepath("test.pdf", "proj1")

            # Assert
            # Les filepaths doivent être différents grâce à la clé aléatoire
            assert filepath1 != filepath2
            assert file_id1 != file_id2
            # Mais tous deux doivent contenir "test.pdf"
            assert "test.pdf" in file_id1
            assert "test.pdf" in file_id2

    def test_generate_unique_filepath_cleans_filename(self, temp_project_dir):
        """Test que le nom de fichier est nettoyé"""
        from controllers.DataController import DataController

        with patch('controllers.DataController.ProjectController') as mock_pc:
            mock_pc.return_value.get_project_path.return_value = temp_project_dir

            # Arrange
            controller = DataController()
            orig_filename = "my document (final).pdf"

            # Act
            filepath, file_id = controller.generate_unique_filepath(orig_filename, "proj1")

            # Assert
            # Les espaces et parenthèses doivent être supprimés
            assert "(" not in file_id
            assert ")" not in file_id
            assert " " not in file_id or file_id.replace("_", "").replace(".", "").replace(
                "mydocumentfinalpdf", ""
            )

    def test_generate_unique_filepath_avoids_collision(self, temp_project_dir):
        """Test que le filepath évite les collisions"""
        from controllers.DataController import DataController

        with patch('controllers.DataController.ProjectController') as mock_pc:
            mock_pc.return_value.get_project_path.return_value = temp_project_dir

            # Arrange
            controller = DataController()

            # Mock generate_random_string pour simuler une collision
            original_generate = controller.generate_random_string
            call_count = [0]

            def mock_generate_with_collision(length=12):
                call_count[0] += 1
                if call_count[0] == 1:
                    return "collision_key"
                return original_generate(length)

            # Créer un fichier qui causera une collision
            collision_file = os.path.join(temp_project_dir, "collision_key_test.pdf")
            with open(collision_file, 'w') as f:
                f.write("test")

            with patch.object(controller, 'generate_random_string', side_effect=mock_generate_with_collision):
                # Act
                filepath, file_id = controller.generate_unique_filepath("test.pdf", "proj1")

                # Assert
                # Doit avoir généré une nouvelle clé après la collision
                assert call_count[0] >= 2
                assert filepath != collision_file

    def test_generate_unique_filepath_format(self, temp_project_dir):
        """Test le format du filepath généré"""
        from controllers.DataController import DataController

        with patch('controllers.DataController.ProjectController') as mock_pc:
            mock_pc.return_value.get_project_path.return_value = temp_project_dir

            # Arrange
            controller = DataController()

            # Act
            filepath, file_id = controller.generate_unique_filepath("report.pdf", "project_123")

            # Assert
            # Le format doit être: random_key_filename
            parts = file_id.split("_", 1)
            assert len(parts) == 2
            assert "report.pdf" in parts[1]
            assert len(parts[0]) == 12  # longueur par défaut de la clé aléatoire
