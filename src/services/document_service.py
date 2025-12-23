"""
Document Service
Handles document loading, chunking, and processing using LangChain
"""

import os
from typing import List, Optional
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from models import ProcessingEnum


class DocumentService:
    """Service for document processing with LangChain"""

    def __init__(
        self,
        project_path: str,
        chunk_size: int = 800,
        chunk_overlap: int = 160,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize DocumentService

        Args:
            project_path: Path to project directory
            chunk_size: Size of text chunks (default: 800 chars)
            chunk_overlap: Overlap between chunks (default: 160 chars)
            separators: List of separators for splitting (default: ["\n\n", "\n", " ", ""])
        """
        self.project_path = project_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # Default separators: prioritize paragraph > line > word > character
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

        # Initialize text splitter with LangChain
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
            length_function=len,
            is_separator_regex=False,
        )

    def get_file_extension(self, file_id: str) -> str:
        """Get file extension from file_id"""
        return os.path.splitext(file_id)[-1]

    def get_file_path(self, file_id: str) -> str:
        """Get full file path"""
        return os.path.join(self.project_path, file_id)

    def get_file_loader(self, file_id: str):
        """
        Get appropriate document loader based on file extension

        Args:
            file_id: File identifier

        Returns:
            LangChain document loader or None
        """
        file_ext = self.get_file_extension(file_id)
        file_path = self.get_file_path(file_id)

        if not os.path.exists(file_path):
            return None

        # Text files
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        # PDF files
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)

        return None

    def load_document(self, file_id: str) -> Optional[List[Document]]:
        """
        Load document from file

        Args:
            file_id: File identifier

        Returns:
            List of LangChain Document objects or None
        """
        loader = self.get_file_loader(file_id)
        if loader:
            return loader.load()
        return None

    def chunk_documents(
        self,
        documents: List[Document],
        preserve_metadata: bool = True
    ) -> List[Document]:
        """
        Chunk documents using RecursiveCharacterTextSplitter

        Args:
            documents: List of LangChain Document objects
            preserve_metadata: Whether to preserve original metadata

        Returns:
            List of chunked Document objects with metadata
        """
        if not documents:
            return []

        # Use LangChain's split_documents method
        # This automatically preserves metadata and adds chunk information
        chunks = self.text_splitter.split_documents(documents)

        # Enrich metadata with additional information
        for i, chunk in enumerate(chunks):
            if preserve_metadata:
                # Add chunk index
                chunk.metadata["chunk_index"] = i
                chunk.metadata["chunk_size"] = len(chunk.page_content)

                # Add source information if not present
                if "source" not in chunk.metadata:
                    chunk.metadata["source"] = "unknown"

        return chunks

    def process_file(
        self,
        file_id: str,
        preserve_metadata: bool = True
    ) -> Optional[List[Document]]:
        """
        Complete pipeline: load and chunk a file

        Args:
            file_id: File identifier
            preserve_metadata: Whether to preserve metadata

        Returns:
            List of chunked Document objects or None
        """
        # Load document
        documents = self.load_document(file_id)

        if not documents:
            return None

        # Chunk documents
        chunks = self.chunk_documents(documents, preserve_metadata)

        return chunks

    def get_chunks_stats(self, chunks: List[Document]) -> dict:
        """
        Get statistics about chunks

        Args:
            chunks: List of Document chunks

        Returns:
            Dictionary with statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "total_characters": 0
            }

        chunk_sizes = [len(chunk.page_content) for chunk in chunks]

        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(chunk_sizes) / len(chunk_sizes),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": sum(chunk_sizes)
        }
