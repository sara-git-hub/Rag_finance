"""
Tests unitaires pour auth.py
Tests des fonctions de hachage de mot de passe, JWT, et authentification
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt, JWTError


@pytest.mark.unit
class TestPasswordHashing:
    """Tests pour le hachage et la vérification de mot de passe"""

    def test_get_password_hash_creates_hash(self):
        """Test que get_password_hash crée un hash"""
        from helpers.auth import get_password_hash

        # Arrange
        password = "SecurePassword123!"

        # Act
        hashed = get_password_hash(password)

        # Assert
        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        # Le hash ne doit pas être le mot de passe en clair
        assert hashed != password

    def test_get_password_hash_different_for_same_password(self):
        """Test que bcrypt génère des hash différents pour le même mot de passe (salt)"""
        from helpers.auth import get_password_hash

        # Arrange
        password = "SamePassword123"

        # Act
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Assert
        # Bcrypt utilise un salt aléatoire, donc les hash sont différents
        assert hash1 != hash2

    def test_get_password_hash_different_passwords(self):
        """Test que différents mots de passe génèrent différents hash"""
        from helpers.auth import get_password_hash

        # Arrange
        password1 = "Password1"
        password2 = "Password2"

        # Act
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)

        # Assert
        assert hash1 != hash2

    def test_verify_password_correct_password(self):
        """Test vérification avec mot de passe correct"""
        from helpers.auth import get_password_hash, verify_password

        # Arrange
        password = "CorrectPassword123"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect_password(self):
        """Test vérification avec mot de passe incorrect"""
        from helpers.auth import get_password_hash, verify_password

        # Arrange
        password = "CorrectPassword"
        wrong_password = "WrongPassword"
        hashed = get_password_hash(password)

        # Act
        result = verify_password(wrong_password, hashed)

        # Assert
        assert result is False

    def test_verify_password_empty_password(self):
        """Test vérification avec mot de passe vide"""
        from helpers.auth import get_password_hash, verify_password

        # Arrange
        password = "SomePassword"
        hashed = get_password_hash(password)

        # Act
        result = verify_password("", hashed)

        # Assert
        assert result is False


@pytest.mark.unit
class TestJWTToken:
    """Tests pour la création et validation de tokens JWT"""

    @patch('helpers.auth.get_settings')
    def test_create_access_token_default_expiration(self, mock_get_settings):
        """Test création de token avec expiration par défaut (24h)"""
        from helpers.auth import create_access_token

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key_12345"
        mock_get_settings.return_value = mock_settings

        user_data = {"sub": "testuser", "role": "user"}

        # Act
        token = create_access_token(user_data)

        # Assert
        assert token is not None
        assert isinstance(token, str)

        # Décoder le token pour vérifier le contenu
        decoded = jwt.decode(token, mock_settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "user"
        assert "exp" in decoded

    @patch('helpers.auth.get_settings')
    def test_create_access_token_custom_expiration(self, mock_get_settings):
        """Test création de token avec expiration personnalisée"""
        from helpers.auth import create_access_token

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key_12345"
        mock_get_settings.return_value = mock_settings

        user_data = {"sub": "testuser"}
        custom_expiration = timedelta(hours=2)

        # Act
        before_creation = datetime.utcnow()
        token = create_access_token(user_data, expires_delta=custom_expiration)
        after_creation = datetime.utcnow()

        # Assert
        decoded = jwt.decode(token, mock_settings.SECRET_KEY, algorithms=["HS256"])
        exp_time = datetime.utcfromtimestamp(decoded["exp"])

        # L'expiration doit être environ 2h après la création
        expected_exp = before_creation + custom_expiration
        # Tolérance de quelques secondes
        assert abs((exp_time - expected_exp).total_seconds()) < 10

    @patch('helpers.auth.get_settings')
    def test_create_access_token_contains_all_data(self, mock_get_settings):
        """Test que le token contient toutes les données fournies"""
        from helpers.auth import create_access_token

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_get_settings.return_value = mock_settings

        user_data = {
            "sub": "john_doe",
            "role": "admin",
            "email": "john@example.com",
            "user_id": 123
        }

        # Act
        token = create_access_token(user_data)

        # Assert
        decoded = jwt.decode(token, mock_settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == "john_doe"
        assert decoded["role"] == "admin"
        assert decoded["email"] == "john@example.com"
        assert decoded["user_id"] == 123


@pytest.mark.unit
class TestGetCurrentUser:
    """Tests pour la validation du token et extraction de l'utilisateur"""

    @pytest.mark.asyncio
    @patch('helpers.auth.get_settings')
    async def test_get_current_user_valid_token(self, mock_get_settings):
        """Test extraction utilisateur avec token valide"""
        from helpers.auth import get_current_user, create_access_token

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_get_settings.return_value = mock_settings

        user_data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(user_data)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        # Act
        result = await get_current_user(credentials)

        # Assert
        assert result["username"] == "testuser"
        assert result["role"] == "admin"

    @pytest.mark.asyncio
    @patch('helpers.auth.get_settings')
    async def test_get_current_user_invalid_token(self, mock_get_settings):
        """Test avec token invalide"""
        from helpers.auth import get_current_user

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_get_settings.return_value = mock_settings

        invalid_token = "invalid.token.here"
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=invalid_token
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('helpers.auth.get_settings')
    async def test_get_current_user_expired_token(self, mock_get_settings):
        """Test avec token expiré"""
        from helpers.auth import create_access_token, get_current_user

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_get_settings.return_value = mock_settings

        user_data = {"sub": "testuser", "role": "user"}
        # Créer un token avec expiration dans le passé
        expired_delta = timedelta(hours=-1)
        token = create_access_token(user_data, expires_delta=expired_delta)

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    @patch('helpers.auth.get_settings')
    async def test_get_current_user_missing_username(self, mock_get_settings):
        """Test avec token sans username (sub)"""
        from helpers.auth import get_current_user

        # Arrange
        mock_settings = Mock()
        mock_settings.SECRET_KEY = "test_secret_key"
        mock_get_settings.return_value = mock_settings

        # Créer un token sans 'sub'
        payload = {"role": "user", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, mock_settings.SECRET_KEY, algorithm="HS256")

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials)

        assert exc_info.value.status_code == 401


@pytest.mark.unit
class TestRequireAdmin:
    """Tests pour la vérification du rôle admin"""

    def test_require_admin_with_admin_user(self):
        """Test qu'un utilisateur admin passe la vérification"""
        from helpers.auth import require_admin
        from models.db_schemes.minirag.schemes.user import UserRole

        # Arrange
        admin_user = {
            "username": "admin_user",
            "role": UserRole.ADMIN.value
        }

        # Act
        result = require_admin(admin_user)

        # Assert
        assert result == admin_user

    def test_require_admin_with_regular_user(self):
        """Test qu'un utilisateur non-admin est rejeté"""
        from helpers.auth import require_admin
        from models.db_schemes.minirag.schemes.user import UserRole

        # Arrange
        regular_user = {
            "username": "regular_user",
            "role": UserRole.USER.value
        }

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            require_admin(regular_user)

        assert exc_info.value.status_code == 403
        assert "Admin privileges required" in exc_info.value.detail

    def test_require_admin_with_invalid_role(self):
        """Test avec rôle invalide"""
        from helpers.auth import require_admin

        # Arrange
        invalid_user = {
            "username": "test_user",
            "role": "invalid_role"
        }

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            require_admin(invalid_user)

        assert exc_info.value.status_code == 403
