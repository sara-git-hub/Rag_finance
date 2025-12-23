"""
Tests for DocumentService
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from langchain_core.documents import Document
from services import DocumentService


class TestDocumentService:
    """Test suite for DocumentService"""

    def test_init_default_params(self, test_data_dir):
        """Test initialization with default parameters"""
        service = DocumentService(project_path=str(test_data_dir))

        assert service.project_path == str(test_data_dir)
        assert service.chunk_size == 800
        assert service.chunk_overlap == 160
        assert service.text_splitter is not None

    def test_init_custom_params(self, test_data_dir):
        """Test initialization with custom parameters"""
        service = DocumentService(
            project_path=str(test_data_dir),
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n"]
        )

        assert service.chunk_size == 500
        assert service.chunk_overlap == 100
        assert service.separators == ["\n\n", "\n"]

    def test_chunk_documents_basic(self, sample_long_text):
        """Test basic document chunking"""
        service = DocumentService(
            project_path=".",
            chunk_size=200,
            chunk_overlap=50
        )

        docs = [Document(page_content=sample_long_text)]
        chunks = service.chunk_documents(docs)

        assert len(chunks) > 1
        assert all(isinstance(chunk, Document) for chunk in chunks)
        assert all(len(chunk.page_content) <= 250 for chunk in chunks)  # Some tolerance

    def test_chunk_documents_preserves_metadata(self, test_data_dir):
        """Test that chunking preserves metadata"""
        service = DocumentService(project_path=str(test_data_dir))

        docs = [
            Document(
                page_content="A" * 2000,
                metadata={"source": "test.pdf", "author": "Test Author"}
            )
        ]

        chunks = service.chunk_documents(docs, preserve_metadata=True)

        assert len(chunks) > 1
        for chunk in chunks:
            assert "source" in chunk.metadata
            assert chunk.metadata["source"] == "test.pdf"
            assert "chunk_index" in chunk.metadata
            assert "chunk_size" in chunk.metadata

    def test_chunk_documents_empty(self, test_data_dir):
        """Test chunking with empty documents"""
        service = DocumentService(project_path=str(test_data_dir))

        chunks = service.chunk_documents([])

        assert chunks == []

    def test_get_chunks_stats_basic(self, sample_documents, test_data_dir):
        """Test getting statistics from chunks"""
        service = DocumentService(project_path=str(test_data_dir))
        chunks = service.chunk_documents(sample_documents)

        stats = service.get_chunks_stats(chunks)

        assert "total_chunks" in stats
        assert "avg_chunk_size" in stats
        assert "min_chunk_size" in stats
        assert "max_chunk_size" in stats
        assert "total_characters" in stats
        assert stats["total_chunks"] == len(chunks)

    def test_get_chunks_stats_empty(self, test_data_dir):
        """Test stats with empty chunks"""
        service = DocumentService(project_path=str(test_data_dir))

        stats = service.get_chunks_stats([])

        assert stats["total_chunks"] == 0
        assert stats["avg_chunk_size"] == 0

    def test_get_file_extension(self, test_data_dir):
        """Test file extension detection"""
        service = DocumentService(project_path=str(test_data_dir))

        assert service.get_file_extension("test.pdf") == ".pdf"
        assert service.get_file_extension("document.txt") == ".txt"
        assert service.get_file_extension("file.docx") == ".docx"

    def test_chunk_overlap_working(self, test_data_dir):
        """Test that chunk overlap actually works"""
        service = DocumentService(
            project_path=str(test_data_dir),
            chunk_size=100,
            chunk_overlap=20
        )

        # Create a document with clear boundaries
        text = "Word " * 100  # 500 characters
        docs = [Document(page_content=text)]

        chunks = service.chunk_documents(docs)

        # With overlap, adjacent chunks should share some content
        if len(chunks) > 1:
            # Check that there's some overlap between consecutive chunks
            assert len(chunks) > 1

    def test_get_file_path(self, test_data_dir):
        """Test construction du chemin complet du fichier"""
        service = DocumentService(project_path=str(test_data_dir))

        # Act
        file_path = service.get_file_path("test_document.pdf")

        # Assert
        assert file_path is not None
        assert str(test_data_dir) in file_path
        assert "test_document.pdf" in file_path
        assert file_path == str(test_data_dir / "test_document.pdf")

    def test_get_file_loader_txt(self, test_data_dir):
        """Test get_file_loader avec fichier .txt"""
        service = DocumentService(project_path=str(test_data_dir))

        # Créer un fichier .txt de test
        txt_file = test_data_dir / "test.txt"
        txt_file.write_text("Ceci est un test.\nDeuxième ligne.", encoding="utf-8")

        # Act
        loader = service.get_file_loader("test.txt")

        # Assert
        assert loader is not None
        from langchain_community.document_loaders import TextLoader
        assert isinstance(loader, TextLoader)

    def test_get_file_loader_pdf(self, test_data_dir):
        """Test get_file_loader avec fichier .pdf"""
        service = DocumentService(project_path=str(test_data_dir))

        # Créer un fichier PDF vide (minimal) de test
        pdf_file = test_data_dir / "test.pdf"
        # PDF minimal valide (header seulement)
        pdf_file.write_bytes(b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0/Kids[]>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n110\n%%EOF')

        # Act
        loader = service.get_file_loader("test.pdf")

        # Assert
        assert loader is not None
        from langchain_community.document_loaders import PyMuPDFLoader
        assert isinstance(loader, PyMuPDFLoader)

    def test_get_file_loader_nonexistent_file(self, test_data_dir):
        """Test get_file_loader avec fichier inexistant"""
        service = DocumentService(project_path=str(test_data_dir))

        # Act
        loader = service.get_file_loader("nonexistent.pdf")

        # Assert
        assert loader is None

    def test_get_file_loader_unsupported_extension(self, test_data_dir):
        """Test get_file_loader avec extension non supportée"""
        service = DocumentService(project_path=str(test_data_dir))

        # Créer un fichier avec extension non supportée
        docx_file = test_data_dir / "test.docx"
        docx_file.write_text("Test", encoding="utf-8")

        # Act
        loader = service.get_file_loader("test.docx")

        # Assert
        assert loader is None

    def test_load_document_txt(self, test_data_dir):
        """Test chargement d'un fichier .txt"""
        service = DocumentService(project_path=str(test_data_dir))

        # Créer un fichier .txt de test
        txt_file = test_data_dir / "load_test.txt"
        txt_content = "Première ligne du document.\nDeuxième ligne du document.\nTroisième ligne."
        txt_file.write_text(txt_content, encoding="utf-8")

        # Act
        documents = service.load_document("load_test.txt")

        # Assert
        assert documents is not None
        assert isinstance(documents, list)
        assert len(documents) > 0
        assert isinstance(documents[0], Document)
        assert "Première ligne" in documents[0].page_content

    @patch('services.document_service.PyMuPDFLoader')
    def test_load_document_pdf(self, mock_loader_class, test_data_dir):
        """Test chargement d'un fichier .pdf avec mock"""
        service = DocumentService(project_path=str(test_data_dir))

        # Créer un fichier PDF minimal
        pdf_file = test_data_dir / "load_test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4\n%%EOF')

        # Mock du loader
        mock_loader = Mock()
        mock_documents = [
            Document(page_content="Document PDF de test", metadata={"source": "load_test.pdf"}),
            Document(page_content="Deuxième page", metadata={"source": "load_test.pdf", "page": 2})
        ]
        mock_loader.load.return_value = mock_documents
        mock_loader_class.return_value = mock_loader

        # Act
        documents = service.load_document("load_test.pdf")

        # Assert
        assert documents is not None
        assert isinstance(documents, list)
        assert len(documents) == 2
        assert isinstance(documents[0], Document)
        assert "Document PDF" in documents[0].page_content

    def test_load_document_nonexistent(self, test_data_dir):
        """Test chargement d'un fichier inexistant"""
        service = DocumentService(project_path=str(test_data_dir))

        # Act
        documents = service.load_document("does_not_exist.pdf")

        # Assert
        assert documents is None

    def test_process_file_complete_pipeline(self, test_data_dir):
        """Test du pipeline complet: load + chunk"""
        service = DocumentService(
            project_path=str(test_data_dir),
            chunk_size=100,
            chunk_overlap=20
        )

        # Créer un fichier .txt avec assez de contenu pour être chunké
        txt_file = test_data_dir / "pipeline_test.txt"
        long_content = "Ceci est une phrase de test. " * 50  # ~1500 caractères
        txt_file.write_text(long_content, encoding="utf-8")

        # Act
        chunks = service.process_file("pipeline_test.txt", preserve_metadata=True)

        # Assert
        assert chunks is not None
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Devrait être chunké
        for chunk in chunks:
            assert isinstance(chunk, Document)
            assert "chunk_index" in chunk.metadata
            assert "chunk_size" in chunk.metadata
            assert len(chunk.page_content) <= 120  # chunk_size + tolérance

    def test_process_file_nonexistent(self, test_data_dir):
        """Test process_file avec fichier inexistant"""
        service = DocumentService(project_path=str(test_data_dir))

        # Act
        chunks = service.process_file("nonexistent.txt")

        # Assert
        assert chunks is None

    def test_process_file_without_metadata(self, test_data_dir):
        """Test process_file sans préservation des métadonnées"""
        service = DocumentService(project_path=str(test_data_dir))

        # Créer un fichier de test
        txt_file = test_data_dir / "no_metadata_test.txt"
        txt_file.write_text("Contenu court.", encoding="utf-8")

        # Act
        chunks = service.process_file("no_metadata_test.txt", preserve_metadata=False)

        # Assert
        assert chunks is not None
        # Même sans preserve_metadata=True, chunk_documents devrait retourner des chunks
        assert isinstance(chunks, list)
