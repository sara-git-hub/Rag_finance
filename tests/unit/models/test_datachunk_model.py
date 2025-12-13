"""
Tests unitaires pour le modèle DataChunk
Tests des contraintes, relations et comportements de la table chunks
"""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
import uuid


@pytest.mark.unit
@pytest.mark.db
class TestDataChunkModel:
    """Tests pour le modèle DataChunk"""

    @pytest.mark.asyncio
    async def test_create_chunk_basic(self, test_db_session):
        """Création basique d'un chunk"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange - Create project and asset first
        project = Project(project_name="Test Project")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(
            asset_type="pdf",
            asset_name="doc.pdf",
            asset_size=1024,
            asset_project_id=project.project_id
        )
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="This is a test chunk of text.",
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )

        # Act
        test_db_session.add(chunk)
        await test_db_session.commit()
        await test_db_session.refresh(chunk)

        # Assert
        assert chunk.chunk_id is not None
        assert chunk.chunk_uuid is not None
        assert isinstance(chunk.chunk_uuid, uuid.UUID)
        assert chunk.chunk_text == "This is a test chunk of text."
        assert chunk.chunk_order == 1
        assert chunk.chunk_project_id == project.project_id
        assert chunk.chunk_asset_id == asset.asset_id
        assert chunk.created_at is not None

    @pytest.mark.asyncio
    async def test_chunk_uuid_unique_and_auto_generated(self, test_db_session):
        """Chaque chunk a un UUID unique auto-généré"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk1 = DataChunk(
            chunk_text="Chunk 1",
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )
        chunk2 = DataChunk(
            chunk_text="Chunk 2",
            chunk_order=2,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )

        # Act
        test_db_session.add_all([chunk1, chunk2])
        await test_db_session.commit()
        await test_db_session.refresh(chunk1)
        await test_db_session.refresh(chunk2)

        # Assert
        assert chunk1.chunk_uuid != chunk2.chunk_uuid
        assert isinstance(chunk1.chunk_uuid, uuid.UUID)
        assert isinstance(chunk2.chunk_uuid, uuid.UUID)

    @pytest.mark.asyncio
    async def test_chunk_text_not_null(self, test_db_session):
        """chunk_text est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(chunk)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_chunk_order_not_null(self, test_db_session):
        """chunk_order est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(chunk)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_chunk_project_id_not_null(self, test_db_session):
        """chunk_project_id (foreign key) est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_order=1,
            chunk_asset_id=asset.asset_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(chunk)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_chunk_asset_id_not_null(self, test_db_session):
        """chunk_asset_id (foreign key) est obligatoire"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_order=1,
            chunk_project_id=project.project_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(chunk)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_chunk_project_id_foreign_key_constraint(self, test_db_session):
        """chunk_project_id doit référencer un projet existant"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_order=1,
            chunk_project_id=99999,  # Non-existent project
            chunk_asset_id=asset.asset_id
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(chunk)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_chunk_asset_id_foreign_key_constraint(self, test_db_session):
        """chunk_asset_id doit référencer un asset existant"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=99999  # Non-existent asset
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            test_db_session.add(chunk)
            await test_db_session.commit()

    @pytest.mark.asyncio
    async def test_chunk_with_metadata_jsonb(self, test_db_session):
        """chunk_metadata peut contenir du JSON"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        metadata = {
            "page": 5,
            "filename": "document.pdf",
            "section": "Introduction"
        }

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_order=1,
            chunk_metadata=metadata,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )

        # Act
        test_db_session.add(chunk)
        await test_db_session.commit()
        await test_db_session.refresh(chunk)

        # Assert
        assert chunk.chunk_metadata == metadata
        assert chunk.chunk_metadata["page"] == 5
        assert chunk.chunk_metadata["filename"] == "document.pdf"

    @pytest.mark.asyncio
    async def test_chunk_metadata_can_be_null(self, test_db_session):
        """chunk_metadata peut être null"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="Test text",
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )

        # Act
        test_db_session.add(chunk)
        await test_db_session.commit()
        await test_db_session.refresh(chunk)

        # Assert
        assert chunk.chunk_metadata is None

    @pytest.mark.asyncio
    async def test_chunk_relationship_to_project(self, test_db_session):
        """Test de la relation DataChunk -> Project"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk
        from sqlalchemy.orm import selectinload

        # Arrange
        project = Project(project_name="Related Project")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="Test",
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )
        test_db_session.add(chunk)
        await test_db_session.commit()

        # Act - Load chunk with project relationship
        result = await test_db_session.execute(
            select(DataChunk).options(selectinload(DataChunk.project)).where(DataChunk.chunk_id == chunk.chunk_id)
        )
        loaded_chunk = result.scalar_one()

        # Assert
        assert loaded_chunk.project is not None
        assert loaded_chunk.project.project_name == "Related Project"

    @pytest.mark.asyncio
    async def test_chunk_relationship_to_asset(self, test_db_session):
        """Test de la relation DataChunk -> Asset"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk
        from sqlalchemy.orm import selectinload

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="related_doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk = DataChunk(
            chunk_text="Test",
            chunk_order=1,
            chunk_project_id=project.project_id,
            chunk_asset_id=asset.asset_id
        )
        test_db_session.add(chunk)
        await test_db_session.commit()

        # Act - Load chunk with asset relationship
        result = await test_db_session.execute(
            select(DataChunk).options(selectinload(DataChunk.asset)).where(DataChunk.chunk_id == chunk.chunk_id)
        )
        loaded_chunk = result.scalar_one()

        # Assert
        assert loaded_chunk.asset is not None
        assert loaded_chunk.asset.asset_name == "related_doc.pdf"

    @pytest.mark.asyncio
    async def test_asset_relationship_to_chunks(self, test_db_session):
        """Test de la relation Asset -> Chunks"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk
        from sqlalchemy.orm import selectinload

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunk1 = DataChunk(chunk_text="Chunk 1", chunk_order=1, chunk_project_id=project.project_id, chunk_asset_id=asset.asset_id)
        chunk2 = DataChunk(chunk_text="Chunk 2", chunk_order=2, chunk_project_id=project.project_id, chunk_asset_id=asset.asset_id)
        chunk3 = DataChunk(chunk_text="Chunk 3", chunk_order=3, chunk_project_id=project.project_id, chunk_asset_id=asset.asset_id)

        test_db_session.add_all([chunk1, chunk2, chunk3])
        await test_db_session.commit()

        # Act - Load asset with chunks relationship
        result = await test_db_session.execute(
            select(Asset).options(selectinload(Asset.chunks)).where(Asset.asset_id == asset.asset_id)
        )
        loaded_asset = result.scalar_one()

        # Assert
        assert len(loaded_asset.chunks) == 3
        chunk_texts = [c.chunk_text for c in loaded_asset.chunks]
        assert "Chunk 1" in chunk_texts
        assert "Chunk 2" in chunk_texts
        assert "Chunk 3" in chunk_texts

    @pytest.mark.asyncio
    async def test_query_chunks_by_order(self, test_db_session):
        """Recherche de chunks par ordre"""
        from models.db_schemes.minirag.schemes.project import Project
        from models.db_schemes.minirag.schemes.asset import Asset
        from models.db_schemes.minirag.schemes.datachunk import DataChunk

        # Arrange
        project = Project(project_name="Test")
        test_db_session.add(project)
        await test_db_session.commit()
        await test_db_session.refresh(project)

        asset = Asset(asset_type="pdf", asset_name="doc.pdf", asset_size=100, asset_project_id=project.project_id)
        test_db_session.add(asset)
        await test_db_session.commit()
        await test_db_session.refresh(asset)

        chunks = [
            DataChunk(chunk_text=f"Chunk {i}", chunk_order=i, chunk_project_id=project.project_id, chunk_asset_id=asset.asset_id)
            for i in range(1, 6)
        ]
        test_db_session.add_all(chunks)
        await test_db_session.commit()

        # Act
        result = await test_db_session.execute(
            select(DataChunk).where(DataChunk.chunk_asset_id == asset.asset_id).order_by(DataChunk.chunk_order)
        )
        ordered_chunks = result.scalars().all()

        # Assert
        assert len(ordered_chunks) == 5
        assert ordered_chunks[0].chunk_order == 1
        assert ordered_chunks[4].chunk_order == 5
        assert [c.chunk_order for c in ordered_chunks] == [1, 2, 3, 4, 5]
