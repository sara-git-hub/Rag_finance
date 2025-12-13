"""
Tests unitaires pour ProjectController
"""

import pytest
import os
import tempfile
import shutil


@pytest.mark.unit
class TestProjectController:
    """Tests pour ProjectController"""

    @pytest.fixture
    def temp_files_dir(self):
        """Créer un répertoire temporaire pour les tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def controller(self, temp_files_dir, monkeypatch):
        """Créer un ProjectController avec répertoire temporaire"""
        from controllers.ProjectController import ProjectController

        # Mock files_dir to use temp directory
        controller = ProjectController()
        monkeypatch.setattr(controller, 'files_dir', temp_files_dir)
        return controller

    def test_initialization(self):
        """Test initialisation du controller"""
        from controllers.ProjectController import ProjectController

        # Act
        controller = ProjectController()

        # Assert
        assert controller is not None
        assert hasattr(controller, 'files_dir')

    def test_get_project_path_creates_directory(self, controller, temp_files_dir):
        """Test que get_project_path crée le répertoire s'il n'existe pas"""
        # Arrange
        project_id = "test_project_123"
        expected_path = os.path.join(temp_files_dir, project_id)

        # Vérifier que le répertoire n'existe pas
        assert not os.path.exists(expected_path)

        # Act
        result_path = controller.get_project_path(project_id)

        # Assert
        assert result_path == expected_path
        assert os.path.exists(result_path)
        assert os.path.isdir(result_path)

    def test_get_project_path_returns_existing_directory(self, controller, temp_files_dir):
        """Test que get_project_path retourne le répertoire existant"""
        # Arrange
        project_id = "existing_project"
        project_path = os.path.join(temp_files_dir, project_id)

        # Créer le répertoire manuellement
        os.makedirs(project_path)
        assert os.path.exists(project_path)

        # Act
        result_path = controller.get_project_path(project_id)

        # Assert
        assert result_path == project_path
        assert os.path.exists(result_path)

    def test_get_project_path_with_numeric_id(self, controller, temp_files_dir):
        """Test avec un ID numérique"""
        # Arrange
        project_id = 12345
        expected_path = os.path.join(temp_files_dir, str(project_id))

        # Act
        result_path = controller.get_project_path(project_id)

        # Assert
        assert result_path == expected_path
        assert os.path.exists(result_path)

    def test_get_project_path_multiple_calls_same_id(self, controller, temp_files_dir):
        """Test appels multiples avec même ID"""
        # Arrange
        project_id = "same_project"

        # Act - Premier appel
        path1 = controller.get_project_path(project_id)

        # Act - Deuxième appel
        path2 = controller.get_project_path(project_id)

        # Assert
        assert path1 == path2
        assert os.path.exists(path1)
        assert os.path.isdir(path1)

    def test_get_project_path_different_projects(self, controller, temp_files_dir):
        """Test création de plusieurs projets différents"""
        # Arrange
        project_ids = ["project_a", "project_b", "project_c"]

        # Act
        paths = [controller.get_project_path(pid) for pid in project_ids]

        # Assert
        for path, project_id in zip(paths, project_ids):
            expected_path = os.path.join(temp_files_dir, project_id)
            assert path == expected_path
            assert os.path.exists(path)

        # Vérifier que tous les répertoires sont distincts
        assert len(set(paths)) == len(project_ids)
