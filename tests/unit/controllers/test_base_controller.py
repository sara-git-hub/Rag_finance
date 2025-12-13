"""
Tests unitaires pour BaseController
Tests des méthodes de base (initialisation, génération de strings, gestion de paths)
"""

import pytest
import os
import tempfile
import shutil
import string


@pytest.mark.unit
class TestBaseControllerInitialization:
    """Tests d'initialisation de BaseController"""

    def test_initialization(self):
        """Test que BaseController s'initialise correctement"""
        from controllers.BaseController import BaseController

        # Act
        controller = BaseController()

        # Assert
        assert controller is not None
        assert hasattr(controller, 'app_settings')
        assert hasattr(controller, 'base_dir')
        assert hasattr(controller, 'files_dir')
        assert hasattr(controller, 'database_dir')

    def test_initialization_sets_base_dir(self):
        """Test que base_dir est correctement défini"""
        from controllers.BaseController import BaseController

        # Act
        controller = BaseController()

        # Assert
        assert controller.base_dir is not None
        assert isinstance(controller.base_dir, str)
        # base_dir devrait pointer vers le répertoire src
        assert 'src' in controller.base_dir or os.path.isabs(controller.base_dir)

    def test_initialization_sets_files_dir(self):
        """Test que files_dir est correctement défini"""
        from controllers.BaseController import BaseController

        # Act
        controller = BaseController()

        # Assert
        assert controller.files_dir is not None
        assert 'assets/files' in controller.files_dir.replace('\\', '/')

    def test_initialization_sets_database_dir(self):
        """Test que database_dir est correctement défini"""
        from controllers.BaseController import BaseController

        # Act
        controller = BaseController()

        # Assert
        assert controller.database_dir is not None
        assert 'assets/database' in controller.database_dir.replace('\\', '/')

    def test_initialization_loads_settings(self):
        """Test que app_settings est chargé depuis config"""
        from controllers.BaseController import BaseController

        # Act
        controller = BaseController()

        # Assert
        assert controller.app_settings is not None
        # Vérifier qu'il a au moins quelques attributs de Settings
        assert hasattr(controller.app_settings, 'APP_NAME')
        assert hasattr(controller.app_settings, 'SECRET_KEY')


@pytest.mark.unit
class TestGenerateRandomString:
    """Tests pour la génération de strings aléatoires"""

    def test_generate_random_string_default_length(self):
        """Test génération avec longueur par défaut (12)"""
        from controllers.BaseController import BaseController

        # Arrange
        controller = BaseController()

        # Act
        result = controller.generate_random_string()

        # Assert
        assert result is not None
        assert isinstance(result, str)
        assert len(result) == 12

    def test_generate_random_string_custom_length(self):
        """Test génération avec longueur personnalisée"""
        from controllers.BaseController import BaseController

        # Arrange
        controller = BaseController()
        lengths = [5, 10, 20, 32, 50]

        for length in lengths:
            # Act
            result = controller.generate_random_string(length=length)

            # Assert
            assert len(result) == length

    def test_generate_random_string_contains_valid_characters(self):
        """Test que la string contient seulement des caractères valides"""
        from controllers.BaseController import BaseController

        # Arrange
        controller = BaseController()
        valid_chars = set(string.ascii_lowercase + string.digits)

        # Act
        result = controller.generate_random_string(length=100)

        # Assert
        for char in result:
            assert char in valid_chars

    def test_generate_random_string_is_random(self):
        """Test que les strings générées sont différentes"""
        from controllers.BaseController import BaseController

        # Arrange
        controller = BaseController()

        # Act
        result1 = controller.generate_random_string(length=20)
        result2 = controller.generate_random_string(length=20)
        result3 = controller.generate_random_string(length=20)

        # Assert
        # Il est extrêmement peu probable que 3 strings aléatoires soient identiques
        assert result1 != result2 or result1 != result3 or result2 != result3

    def test_generate_random_string_length_zero(self):
        """Test génération avec longueur 0"""
        from controllers.BaseController import BaseController

        # Arrange
        controller = BaseController()

        # Act
        result = controller.generate_random_string(length=0)

        # Assert
        assert result == ""
        assert len(result) == 0

    def test_generate_random_string_length_one(self):
        """Test génération avec longueur 1"""
        from controllers.BaseController import BaseController

        # Arrange
        controller = BaseController()

        # Act
        result = controller.generate_random_string(length=1)

        # Assert
        assert len(result) == 1
        assert result in string.ascii_lowercase + string.digits


@pytest.mark.unit
class TestGetDatabasePath:
    """Tests pour la gestion des paths de database"""

    @pytest.fixture
    def temp_base_controller(self, monkeypatch):
        """Créer un BaseController avec répertoire temporaire"""
        from controllers.BaseController import BaseController

        temp_dir = tempfile.mkdtemp()
        controller = BaseController()

        # Remplacer database_dir par un répertoire temporaire
        monkeypatch.setattr(controller, 'database_dir', temp_dir)

        yield controller

        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_get_database_path_creates_directory(self, temp_base_controller):
        """Test que get_database_path crée le répertoire s'il n'existe pas"""
        # Arrange
        db_name = "test_database"
        expected_path = os.path.join(temp_base_controller.database_dir, db_name)

        # Vérifier que le répertoire n'existe pas
        assert not os.path.exists(expected_path)

        # Act
        result_path = temp_base_controller.get_database_path(db_name)

        # Assert
        assert result_path == expected_path
        assert os.path.exists(result_path)
        assert os.path.isdir(result_path)

    def test_get_database_path_returns_existing_directory(self, temp_base_controller):
        """Test que get_database_path retourne le répertoire existant"""
        # Arrange
        db_name = "existing_database"
        db_path = os.path.join(temp_base_controller.database_dir, db_name)

        # Créer le répertoire manuellement
        os.makedirs(db_path)
        assert os.path.exists(db_path)

        # Act
        result_path = temp_base_controller.get_database_path(db_name)

        # Assert
        assert result_path == db_path
        assert os.path.exists(result_path)

    def test_get_database_path_multiple_calls_same_name(self, temp_base_controller):
        """Test appels multiples avec même nom de database"""
        # Arrange
        db_name = "same_database"

        # Act - Premier appel
        path1 = temp_base_controller.get_database_path(db_name)

        # Act - Deuxième appel
        path2 = temp_base_controller.get_database_path(db_name)

        # Assert
        assert path1 == path2
        assert os.path.exists(path1)

    def test_get_database_path_different_names(self, temp_base_controller):
        """Test création de plusieurs databases différentes"""
        # Arrange
        db_names = ["db1", "db2", "db3"]

        # Act
        paths = [temp_base_controller.get_database_path(name) for name in db_names]

        # Assert
        for path, db_name in zip(paths, db_names):
            assert os.path.exists(path)
            assert os.path.isdir(path)
            assert db_name in path

        # Vérifier que tous les paths sont distincts
        assert len(set(paths)) == len(db_names)

    def test_get_database_path_with_special_characters(self, temp_base_controller):
        """Test avec nom de database contenant des caractères spéciaux"""
        # Arrange
        db_name = "test_db_2024"

        # Act
        result_path = temp_base_controller.get_database_path(db_name)

        # Assert
        assert os.path.exists(result_path)
        assert "test_db_2024" in result_path

    def test_get_database_path_nested_structure(self, temp_base_controller):
        """Test que le path est correctement construit"""
        # Arrange
        db_name = "my_database"

        # Act
        result_path = temp_base_controller.get_database_path(db_name)

        # Assert
        # Le path devrait être database_dir/my_database
        expected_path = os.path.join(temp_base_controller.database_dir, db_name)
        assert result_path == expected_path
