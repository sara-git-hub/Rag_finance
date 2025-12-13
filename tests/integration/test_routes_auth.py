"""
Tests d'intégration pour les endpoints d'authentification
Tests des routes /api/v1/auth/*
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRegistration:
    """Tests pour l'endpoint de registration"""

    @pytest.mark.asyncio
    async def test_first_user_becomes_admin(self, test_client: AsyncClient):
        """Le premier utilisateur enregistré devient automatiquement admin"""
        # Arrange
        user_data = {
            "username": "firstuser",
            "email": "first@test.com",
            "password": "SecurePass123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "admin"  # Premier utilisateur = admin
        assert data["username"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_register_valid_user(self, test_client: AsyncClient, admin_user):
        """Enregistrement d'un utilisateur valide"""
        # Arrange
        user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "password": "ValidPass123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"  # Deuxième utilisateur = user
        assert data["username"] == user_data["username"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, test_client: AsyncClient, admin_user):
        """Ne peut pas enregistrer un username déjà existant"""
        # Arrange
        user_data = {
            "username": admin_user["username"],  # Username déjà utilisé
            "email": "different@test.com",
            "password": "SecurePass123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, test_client: AsyncClient, admin_user):
        """Ne peut pas enregistrer un email déjà existant"""
        # Arrange
        user_data = {
            "username": "differentuser",
            "email": admin_user["email"],  # Email déjà utilisé
            "password": "SecurePass123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, test_client: AsyncClient):
        """Validation de l'email échoue avec un email invalide"""
        # Arrange
        user_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "SecurePass123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/register", json=user_data)

        # Assert
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, test_client: AsyncClient):
        """Échec si des champs obligatoires sont manquants"""
        # Arrange
        incomplete_data = {
            "username": "testuser"
            # email et password manquants
        }

        # Act
        response = await test_client.post("/api/v1/auth/register", json=incomplete_data)

        # Assert
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.auth
class TestAuthLogin:
    """Tests pour l'endpoint de login"""

    @pytest.mark.asyncio
    async def test_login_valid_credentials(self, test_client: AsyncClient, admin_user):
        """Login réussi avec des credentials valides"""
        # Arrange
        login_data = {
            "username": admin_user["username"],
            "password": admin_user["password"]
        }

        # Act
        response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == admin_user["role"]
        assert data["username"] == admin_user["username"]

    @pytest.mark.asyncio
    async def test_login_invalid_username(self, test_client: AsyncClient):
        """Login échoue avec un username inexistant"""
        # Arrange
        login_data = {
            "username": "nonexistent",
            "password": "SomePassword123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, test_client: AsyncClient, admin_user):
        """Login échoue avec un mauvais mot de passe"""
        # Arrange
        login_data = {
            "username": admin_user["username"],
            "password": "WrongPassword123!"
        }

        # Act
        response = await test_client.post("/api/v1/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_login_missing_fields(self, test_client: AsyncClient):
        """Login échoue si des champs sont manquants"""
        # Arrange
        incomplete_data = {
            "username": "testuser"
            # password manquant
        }

        # Act
        response = await test_client.post("/api/v1/auth/login", json=incomplete_data)

        # Assert
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.auth
class TestAuthProtectedRoutes:
    """Tests pour les routes protégées par authentification"""

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_token(self, test_client: AsyncClient, admin_user):
        """Accès à /me réussi avec un token valide"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}

        # Act
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == admin_user["username"]
        assert data["email"] == admin_user["email"]
        assert data["role"] == admin_user["role"]
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_get_current_user_without_token(self, test_client: AsyncClient):
        """Accès à /me échoue sans token"""
        # Act
        response = await test_client.get("/api/v1/auth/me")

        # Assert
        assert response.status_code == 403  # FastAPI returns 403 when no credentials provided

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token(self, test_client: AsyncClient):
        """Accès à /me échoue avec un token invalide"""
        # Arrange
        headers = {"Authorization": "Bearer invalid_token_xyz"}

        # Act
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.admin
class TestAuthAdminEndpoints:
    """Tests pour les endpoints admin"""

    @pytest.mark.asyncio
    async def test_get_all_users_as_admin(self, test_client: AsyncClient, admin_user, registered_user):
        """Admin peut lister tous les utilisateurs"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}

        # Act
        response = await test_client.get("/api/v1/auth/users", headers=headers)

        # Assert
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)
        assert len(users) >= 2  # Au moins admin + registered_user
        usernames = [u["username"] for u in users]
        assert admin_user["username"] in usernames
        assert registered_user["username"] in usernames

    @pytest.mark.asyncio
    async def test_get_all_users_as_regular_user(self, test_client: AsyncClient, registered_user):
        """Utilisateur normal ne peut pas lister les utilisateurs"""
        # Arrange
        headers = {"Authorization": f"Bearer {registered_user['token']}"}

        # Act
        response = await test_client.get("/api/v1/auth/users", headers=headers)

        # Assert
        assert response.status_code == 403  # Forbidden

    @pytest.mark.asyncio
    async def test_admin_create_user(self, test_client: AsyncClient, admin_user):
        """Admin peut créer un nouvel utilisateur"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}
        new_user_data = {
            "username": "created_by_admin",
            "email": "created@test.com",
            "password": "CreatedPass123!",
            "role": "user"
        }

        # Act
        response = await test_client.post(
            "/api/v1/auth/admin/users",
            json=new_user_data,
            headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == new_user_data["username"]
        assert data["email"] == new_user_data["email"]
        assert data["role"] == new_user_data["role"]
        assert data["is_active"] is True

    @pytest.mark.asyncio
    async def test_admin_create_admin_user(self, test_client: AsyncClient, admin_user):
        """Admin peut créer un autre admin"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}
        new_admin_data = {
            "username": "second_admin",
            "email": "admin2@test.com",
            "password": "AdminPass123!",
            "role": "admin"
        }

        # Act
        response = await test_client.post(
            "/api/v1/auth/admin/users",
            json=new_admin_data,
            headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    @pytest.mark.asyncio
    async def test_regular_user_cannot_create_user(self, test_client: AsyncClient, registered_user):
        """Utilisateur normal ne peut pas créer d'utilisateur"""
        # Arrange
        headers = {"Authorization": f"Bearer {registered_user['token']}"}
        new_user_data = {
            "username": "should_fail",
            "email": "fail@test.com",
            "password": "FailPass123!",
            "role": "user"
        }

        # Act
        response = await test_client.post(
            "/api/v1/auth/admin/users",
            json=new_user_data,
            headers=headers
        )

        # Assert
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_update_user_password(self, test_client: AsyncClient, admin_user, registered_user):
        """Admin peut changer le mot de passe d'un utilisateur"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}
        new_password_data = {"new_password": "NewSecurePass123!"}

        # Act
        response = await test_client.patch(
            f"/api/v1/auth/users/{registered_user['username']}/password",
            json=new_password_data,
            headers=headers
        )

        # Assert
        assert response.status_code == 200
        assert "updated successfully" in response.json()["message"]

        # Verify new password works
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "username": registered_user["username"],
                "password": new_password_data["new_password"]
            }
        )
        assert login_response.status_code == 200

    @pytest.mark.asyncio
    async def test_admin_delete_user(self, test_client: AsyncClient, admin_user, registered_user):
        """Admin peut supprimer un utilisateur"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}

        # Act
        response = await test_client.delete(
            f"/api/v1/auth/users/{registered_user['username']}",
            headers=headers
        )

        # Assert
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify user cannot login anymore
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "username": registered_user["username"],
                "password": registered_user["password"]
            }
        )
        assert login_response.status_code == 401

    @pytest.mark.asyncio
    async def test_admin_cannot_delete_self(self, test_client: AsyncClient, admin_user):
        """Admin ne peut pas se supprimer lui-même"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}

        # Act
        response = await test_client.delete(
            f"/api/v1/auth/users/{admin_user['username']}",
            headers=headers
        )

        # Assert
        assert response.status_code == 403
        assert "cannot delete your own account" in response.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_delete_nonexistent_user(self, test_client: AsyncClient, admin_user):
        """Supprimer un utilisateur inexistant retourne 404"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}

        # Act
        response = await test_client.delete(
            "/api/v1/auth/users/nonexistent_user",
            headers=headers
        )

        # Assert
        assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.auth
class TestJWTTokenValidation:
    """Tests pour la validation des tokens JWT"""

    @pytest.mark.asyncio
    async def test_token_contains_user_info(self, test_client: AsyncClient, admin_user):
        """Le token JWT contient les informations de l'utilisateur"""
        # Arrange
        headers = {"Authorization": f"Bearer {admin_user['token']}"}

        # Act - Utiliser le token pour accéder à une route protégée
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        # Assert - Les infos du token correspondent aux infos du user
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == admin_user["username"]
        assert data["role"] == admin_user["role"]

    @pytest.mark.asyncio
    async def test_expired_token_rejected(self, test_client: AsyncClient):
        """Un token expiré est rejeté"""
        # Arrange - Token manifestement invalide/expiré
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjowfQ.invalid"}

        # Act
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_token_rejected(self, test_client: AsyncClient):
        """Un token mal formé est rejeté"""
        # Arrange
        headers = {"Authorization": "Bearer not.a.jwt"}

        # Act
        response = await test_client.get("/api/v1/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401
