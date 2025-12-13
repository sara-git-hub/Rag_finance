"""
Tests unitaires pour le modèle Project
Tests des contraintes, relations et comportements de la table projects
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import uuid


@pytest.mark.unit
@pytest.mark.db
class TestProjectModel:
    """Tests pour le modèle Project"""

    @pytest.mark.asyncio
    async def test_create_project_basic(self, test_db_session):
        """Création basique d'un projet"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(
            project_name="Test Project",
            project_language="fr"
        )

        # Act
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.project_id is not None
        assert project.project_uuid is not None
        assert isinstance(project.project_uuid, uuid.UUID)
        assert project.project_name == "Test Project"
        assert project.project_language == "fr"
        assert project.created_at is not None

    @pytest.mark.asyncio
    async def test_project_uuid_unique_and_auto_generated(self, test_db_session):
        """Chaque projet a un UUID unique auto-généré"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project1 = Project(project_name="Project 1")
        project2 = Project(project_name="Project 2")

        # Act
        test_db_session.add_all([project1, project2])
        await test_db_session.commit()
        await test_db_session.refresh(project1)
        await test_db_session.refresh(project2)

        # Assert
        assert project1.project_uuid != project2.project_uuid
        assert isinstance(project1.project_uuid, uuid.UUID)
        assert isinstance(project2.project_uuid, uuid.UUID)

    @pytest.mark.asyncio
    async def test_project_name_can_be_null(self, test_db_session):
        """Le nom du projet peut être null"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_language="en")

        # Act
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.project_name is None
        assert project.project_id is not None

    @pytest.mark.asyncio
    async def test_default_language_is_fr(self, test_db_session):
        """La langue par défaut est 'fr'"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="Test")

        # Act
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.project_language == "fr"

    @pytest.mark.asyncio
    async def test_project_with_english_language(self, test_db_session):
        """Création d'un projet en anglais"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="English Project", project_language="en")

        # Act
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.project_language == "en"

    @pytest.mark.asyncio
    async def test_created_at_auto_generated(self, test_db_session):
        """created_at est automatiquement généré"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="Test")

        # Act
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.created_at is not None

    @pytest.mark.asyncio
    async def test_updated_at_initially_null(self, test_db_session):
        """updated_at est null à la création"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="Test")

        # Act
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.updated_at is None

    @pytest.mark.asyncio
    async def test_updated_at_set_on_update(self, test_db_session):
        """updated_at est mis à jour lors d'une modification"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="Original Name")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Act - Update project
        project.project_name = "Updated Name"
        await test_db_session.commit()
        await test_db_session.refresh(project)

        # Assert
        assert project.updated_at is not None
        assert project.project_name == "Updated Name"

    @pytest.mark.asyncio
    async def test_query_project_by_name(self, test_db_session):
        """Recherche d'un projet par nom"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="Unique Project Name")
        test_db_session.add(project)
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(Project).where(Project.project_name == "Unique Project Name")
        )
        found_project = result.scalar_one_or_none()

        # Assert
        assert found_project is not None
        assert found_project.project_name == "Unique Project Name"

    @pytest.mark.asyncio
    async def test_query_project_by_uuid(self, test_db_session):
        """Recherche d'un projet par UUID"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)
        project_uuid = project.project_uuid

        # Act
        result = await test_db_session.execute(
            select(Project).where(Project.project_uuid == project_uuid)
        )
        found_project = result.scalar_one_or_none()

        # Assert
        assert found_project is not None
        assert found_project.project_uuid == project_uuid

    @pytest.mark.asyncio
    async def test_query_projects_by_language(self, test_db_session):
        """Recherche de projets par langue"""
        from models.db_schemes.minirag.schemes.project import Project

        # Arrange
        project_fr1 = Project(project_name="French 1", project_language="fr")
        project_fr2 = Project(project_name="French 2", project_language="fr")
        project_en = Project(project_name="English", project_language="en")

        test_db_session.add_all([project_fr1, project_fr2, project_en])
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(Project).where(Project.project_language == "fr")
        )
        french_projects = result.scalars().all()

        # Assert
        assert len(french_projects) == 2
        assert all(p.project_language == "fr" for p in french_projects)
