"""
Tests unitaires pour le modèle Asset
Tests des contraintes, relations et comportements de la table assets
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import uuid


@pytest.mark.unit
@pytest.mark.db
class TestAssetModel:
    """Tests pour le modèle Asset"""

    @pytest.mark.asyncio
    async def test_create_asset_basic(self, test_db_session):
        """Création basique d'un asset"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange - Create project first
        project = Project(project_name="Test Project")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_type="pdf",
            asset_name="document.pdf",
            asset_size=1024,
            asset_project_id=project.project_id
        )

        # Act
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        # Assert
        assert asset.asset_id is not None
        assert asset.asset_uuid is not None
        assert isinstance(asset.asset_uuid, uuid.UUID)
        assert asset.asset_type == "pdf"
        assert asset.asset_name == "document.pdf"
        assert asset.asset_size == 1024
        assert asset.asset_project_id == project.project_id
        assert asset.created_at is not None

    @pytest.mark.asyncio
    async def test_asset_uuid_unique_and_auto_generated(self, test_db_session):
        """Chaque asset a un UUID unique auto-généré"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test Project")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset1 = Asset(
            asset_type="pdf",
            asset_name="doc1.pdf",
            asset_size=100,
            asset_project_id=project.project_id
        )
        asset2 = Asset(
            asset_type="pdf",
            asset_name="doc2.pdf",
            asset_size=200,
            asset_project_id=project.project_id
        )

        # Act
        test_db_session.add_all([asset1, asset2])
        await test_db_session.commit()
        await test_db_session.refresh(asset1)
        await test_db_session.refresh(asset2)

        # Assert
        assert asset1.asset_uuid != asset2.asset_uuid
        assert isinstance(asset1.asset_uuid, uuid.UUID)
        assert isinstance(asset2.asset_uuid, uuid.UUID)

    @pytest.mark.asyncio
    async def test_asset_type_not_null(self, test_db_session):
        """asset_type est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_name="doc.pdf",
            asset_size=100,
            asset_project_id=project.project_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(asset)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_asset_name_not_null(self, test_db_session):
        """asset_name est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_type="pdf",
            asset_size=100,
            asset_project_id=project.project_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(asset)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_asset_size_not_null(self, test_db_session):
        """asset_size est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_project_id=project.project_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(asset)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_asset_project_id_not_null(self, test_db_session):
        """asset_project_id (foreign key) est obligatoire"""
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_size=100
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(asset)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_asset_project_id_foreign_key_constraint(self, test_db_session):
        """asset_project_id doit référencer un projet existant"""
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_size=100,
            asset_project_id=99999  # Non-existent project
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(asset)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_asset_with_config_jsonb(self, test_db_session):
        """asset_config peut contenir du JSON"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        config = {
            "processing": "done",
            "chunks": 10,
            "metadata": {"author": "test"}
        }

        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_size=100,
            asset_project_id=project.project_id,
            asset_config=config
        )

        # Act
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        # Assert
        assert asset.asset_config == config
        assert asset.asset_config["chunks"] == 10
        assert asset.asset_config["metadata"]["author"] == "test"

    @pytest.mark.asyncio
    async def test_asset_config_can_be_null(self, test_db_session):
        """asset_config peut être null"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_size=100,
            asset_project_id=project.project_id
        )

        # Act
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        # Assert
        assert asset.asset_config is None

    @pytest.mark.asyncio
    async def test_asset_relationship_to_project(self, test_db_session):
        """Test de la relation Asset -> Project"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from sqlalchemy.orm import selectinload

        # Arrange
        project = Project(project_name="Related Project")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_size=100,
            asset_project_id=project.project_id
        )
        test_db_session.add(asset)
        await test_db_session.commit()

        # Act - Load asset with project relationship
        result = await test_db_session.execute(
            select(Asset).options(selectinload(Asset.project)).where(Asset.asset_id == asset.asset_id)
        )
        loaded_asset = result.scalar_one()

        # Assert
        assert loaded_asset.project is not None
        assert loaded_asset.project.project_name == "Related Project"
        assert loaded_asset.project.project_id == project.project_id

    @pytest.mark.asyncio
    async def test_project_relationship_to_assets(self, test_db_session):
        """Test de la relation Project -> Assets"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from sqlalchemy.orm import selectinload

        # Arrange
        project = Project(project_name="Project with assets")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset1 = Asset(asset_type="pdf", asset_name="doc1.pdf", asset_size=100, asset_project_id=project.project_id)
        asset2 = Asset(asset_type="txt", asset_name="doc2.txt", asset_size=50, asset_project_id=project.project_id)

        test_db_session.add_all([asset1, asset2])
        await test_db_session.commit()

        # Act - Load project with assets relationship
        result = await test_db_session.execute(
            select(Project).options(selectinload(Project.assets)).where(Project.project_id == project.project_id)
        )
        loaded_project = result.scalar_one()

        # Assert
        assert len(loaded_project.assets) == 2
        asset_names = [a.asset_name for a in loaded_project.assets]
        assert "doc1.pdf" in asset_names
        assert "doc2.txt" in asset_names

    @pytest.mark.asyncio
    async def test_query_assets_by_type(self, test_db_session):
        """Recherche d'assets par type"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        pdf1 = Asset(asset_type="pdf", asset_name="doc1.pdf", asset_size=100, asset_project_id=project.project_id)
        pdf2 = Asset(asset_type="pdf", asset_name="doc2.pdf", asset_size=200, asset_project_id=project.project_id)
        txt = Asset(asset_type="txt", asset_name="doc.txt", asset_size=50, asset_project_id=project.project_id)

        test_db_session.add_all([pdf1, pdf2, txt])
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(Asset).where(Asset.asset_type == "pdf")
        )
        pdf_assets = result.scalars().all()

        # Assert
        assert len(pdf_assets) == 2
        assert all(a.asset_type == "pdf" for a in pdf_assets)

    @pytest.mark.asyncio
    async def test_query_assets_by_project(self, test_db_session):
        """Recherche d'assets par projet"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset

        # Arrange
        project1 = Project(project_name="Project 1")
        project2 = Project(project_name="Project 2")
        test_db_session.add_all([project1, project2])
        await test_db_session.commit()
        await test_db_session.refresh(project1)
        await test_db_session.refresh(project2)

        asset1 = Asset(asset_type="pdf", asset_name="p1_doc1.pdf", asset_size=100, asset_project_id=project1.project_id)
        asset2 = Asset(asset_type="pdf", asset_name="p1_doc2.pdf", asset_size=200, asset_project_id=project1.project_id)
        asset3 = Asset(asset_type="pdf", asset_name="p2_doc1.pdf", asset_size=150, asset_project_id=project2.project_id)

        test_db_session.add_all([asset1, asset2, asset3])
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(Asset).where(Asset.asset_project_id == project1.project_id)
        )
        project1_assets = result.scalars().all()

        # Assert
        assert len(project1_assets) == 2
        assert all(a.asset_project_id == project1.project_id for a in project1_assets)
