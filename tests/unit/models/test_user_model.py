"""
Tests unitaires pour le modèle User
Tests des contraintes, validations et comportements de la table users
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import uuid


@pytest.mark.unit
@pytest.mark.db
class TestUserModel:
    """Tests pour le modèle User"""

    @pytest.mark.asyncio
    async def test_create_user_basic(self, test_db_session):
        """Création basique d'un utilisateur avec tous les champs requis"""
        from models.db_schemes.minirag.schemes.user import User, UserRole

        # Arrange
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.USER
        )

        # Act
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.user_id is not None
        assert user.user_uuid is not None
        assert isinstance(user.user_uuid, uuid.UUID)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True  # Default value
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_create_admin_user(self, test_db_session):
        """Création d'un utilisateur avec rôle admin"""
        from models.db_schemes.minirag.schemes.user import User, UserRole

        # Arrange
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password="admin_hash",
            role=UserRole.ADMIN
        )

        # Act
        test_db_session.add(admin)
        await test_db_session.commit()
        await test_db_session.refresh(admin)

        # Assert
        assert admin.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_user_uuid_unique_and_auto_generated(self, test_db_session):
        """Chaque utilisateur a un UUID unique auto-généré"""
        from models.db_schemes.minirag.schemes.user import User, UserRole

        # Arrange
        user1 = User(username="user1", email="user1@test.com", hashed_password="hash1")
        user2 = User(username="user2", email="user2@test.com", hashed_password="hash2")

        # Act
        test_db_session.add_all([user1, user2])
        await test_db_session.commit()
        await test_db_session.refresh(user1)
        await test_db_session.refresh(user2)

        # Assert
        assert user1.user_uuid != user2.user_uuid
        assert isinstance(user1.user_uuid, uuid.UUID)
        assert isinstance(user2.user_uuid, uuid.UUID)

    @pytest.mark.asyncio
    async def test_username_unique_constraint(self, test_db_session):
        """Le username doit être unique"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user1 = User(username="duplicate", email="email1@test.com", hashed_password="hash1")
        user2 = User(username="duplicate", email="email2@test.com", hashed_password="hash2")

        test_db_session.add(user1)
        await test_db_session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(user2)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_email_unique_constraint(self, test_db_session):
        """L'email doit être unique"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user1 = User(username="user1", email="duplicate@test.com", hashed_password="hash1")
        user2 = User(username="user2", email="duplicate@test.com", hashed_password="hash2")

        test_db_session.add(user1)
        await test_db_session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(user2)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_username_not_null(self, test_db_session):
        """Le username est obligatoire"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(email="test@test.com", hashed_password="hash")

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(user)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_email_not_null(self, test_db_session):
        """L'email est obligatoire"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", hashed_password="hash")

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(user)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_hashed_password_not_null(self, test_db_session):
        """Le mot de passe hashé est obligatoire"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", email="test@test.com")

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(user)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_default_role_is_user(self, test_db_session):
        """Le rôle par défaut est USER"""
        from models.db_schemes.minirag.schemes.user import User, UserRole

        # Arrange
        user = User(
            username="testuser",
            email="test@test.com",
            hashed_password="hash"
            # role not specified
        )

        # Act
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_default_is_active_true(self, test_db_session):
        """is_active est True par défaut"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(
            username="testuser",
            email="test@test.com",
            hashed_password="hash"
            # is_active not specified
        )

        # Act
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_can_deactivate_user(self, test_db_session):
        """Un utilisateur peut être désactivé"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(
            username="testuser",
            email="test@test.com",
            hashed_password="hash",
            is_active=False
        )

        # Act
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.is_active is False

    @pytest.mark.asyncio
    async def test_created_at_auto_generated(self, test_db_session):
        """created_at est automatiquement généré"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", email="test@test.com", hashed_password="hash")

        # Act
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_updated_at_initially_null(self, test_db_session):
        """updated_at est null à la création"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", email="test@test.com", hashed_password="hash")

        # Act
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.updated_at is None

    @pytest.mark.asyncio
    async def test_updated_at_set_on_update(self, test_db_session):
        """updated_at est mis à jour lors d'une modification"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", email="test@test.com", hashed_password="hash")
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Act - Update user
        user.email = "newemail@test.com"
        await test_db_session.commit()
        await test_db_session.refresh(user)

        # Assert
        assert user.updated_at is not None
        assert user.email == "newemail@test.com"

    @pytest.mark.asyncio
    async def test_user_role_enum_values(self, test_db_session):
        """Test des valeurs possibles de UserRole"""
        from models.db_schemes.minirag.schemes.user import UserRole

        # Assert
        assert UserRole.ADMIN.value == "admin"
        assert UserRole.USER.value == "user"
        assert len(list(UserRole)) == 2

    @pytest.mark.asyncio
    async def test_query_user_by_username(self, test_db_session):
        """Recherche d'un utilisateur par username"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="findme", email="find@test.com", hashed_password="hash")
        test_db_session.add(user)
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(User).where(User.username == "findme")
        )
        found_user = result.scalar_one_or_none()

        # Assert
        assert found_user is not None
        assert found_user.username == "findme"
        assert found_user.email == "find@test.com"

    @pytest.mark.asyncio
    async def test_query_user_by_email(self, test_db_session):
        """Recherche d'un utilisateur par email"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", email="findme@test.com", hashed_password="hash")
        test_db_session.add(user)
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(User).where(User.email == "findme@test.com")
        )
        found_user = result.scalar_one_or_none()

        # Assert
        assert found_user is not None
        assert found_user.email == "findme@test.com"

    @pytest.mark.asyncio
    async def test_query_user_by_uuid(self, test_db_session):
        """Recherche d'un utilisateur par UUID"""
        from models.db_schemes.minirag.schemes.user import User

        # Arrange
        user = User(username="testuser", email="test@test.com", hashed_password="hash")
        test_db_session.add(user)
        await test_db_session.commit()
        await test_db_session.refresh(user)
        user_uuid = user.user_uuid

        # Act
        result = await test_db_session.execute(
            select(User).where(User.user_uuid == user_uuid)
        )
        found_user = result.scalar_one_or_none()

        # Assert
        assert found_user is not None
        assert found_user.user_uuid == user_uuid
