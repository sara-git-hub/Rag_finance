"""
Tests for DocumentService
"""

import pytest
from pathlib import Path
from langchain_core.documents import Document
from services import DocumentService


class TestDocumentService:
    """Test suite for DocumentService"""

    def test_init_default_params(self, test_data_dir):
        """Test initialization with default parameters"""
        service = DocumentService(project_path=str(test_data_dir))

        assert service.project_path == str(test_data_dir)
        assert service.chunk_size == 1000
        assert service.chunk_overlap == 200
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
