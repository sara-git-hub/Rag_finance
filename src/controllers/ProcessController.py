"""
ProcessController - Version LangChain
Gère le traitement des documents avec DocumentService
"""

from .BaseController import BaseController
from .ProjectController import ProjectController
from services import DocumentService
from typing import List, Optional
from langchain_core.documents import Document


class ProcessController(BaseController):
    """Controller pour le traitement de documents avec LangChain"""

    def __init__(self, project_id: str, chunk_size: int = 800, chunk_overlap: int = 160):
        """
        Initialize ProcessController

        Args:
            project_id: ID du projet
            chunk_size: Taille des chunks (défaut: 800)
            chunk_overlap: Chevauchement entre chunks (défaut: 160)
        """
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

        # Initialize DocumentService with LangChain
        self.doc_service = DocumentService(
            project_path=self.project_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]  # Intelligent separators
        )

    def get_file_content(self, file_id: str) -> Optional[List[Document]]:
        """
        Load document content

        Args:
            file_id: File identifier

        Returns:
            List of LangChain Document objects or None
        """
        return self.doc_service.load_document(file_id)

    def process_file_content(
        self,
        file_content: List[Document],
        file_id: str,
        chunk_size: Optional[int] = None,
        overlap_size: Optional[int] = None
    ) -> List[Document]:
        """
        Process and chunk file content using LangChain

        Args:
            file_content: List of Document objects from loader
            file_id: File identifier
            chunk_size: Optional custom chunk size
            overlap_size: Optional custom overlap size

        Returns:
            List of chunked Document objects
        """
        # Use custom parameters if provided
        if chunk_size is not None or overlap_size is not None:
            # Create temporary service with custom params
            temp_service = DocumentService(
                project_path=self.project_path,
                chunk_size=chunk_size or self.doc_service.chunk_size,
                chunk_overlap=overlap_size or self.doc_service.chunk_overlap
            )
            chunks = temp_service.chunk_documents(file_content, preserve_metadata=True)
        else:
            # Use default service
            chunks = self.doc_service.chunk_documents(file_content, preserve_metadata=True)

        # Add file_id and filename to metadata
        for chunk in chunks:
            chunk.metadata["file_id"] = file_id
            # Extract filename by removing ID prefix (format: {id}_{filename})
            if "_" in file_id:
                chunk.metadata["filename"] = "_".join(file_id.split("_")[1:])
            else:
                chunk.metadata["filename"] = file_id

        return chunks

    def process_file(
        self,
        file_id: str,
        chunk_size: Optional[int] = None,
        overlap_size: Optional[int] = None
    ) -> Optional[List[Document]]:
        """
        Complete pipeline: load and chunk a file

        Args:
            file_id: File identifier
            chunk_size: Optional custom chunk size
            overlap_size: Optional custom overlap size

        Returns:
            List of chunked Document objects or None
        """
        # Load document
        file_content = self.get_file_content(file_id)

        if not file_content:
            return None

        # Process and chunk
        chunks = self.process_file_content(
            file_content=file_content,
            file_id=file_id,
            chunk_size=chunk_size,
            overlap_size=overlap_size
        )

        return chunks

    def get_chunks_stats(self, chunks: List[Document]) -> dict:
        """
        Get statistics about chunks

        Args:
            chunks: List of Document chunks

        Returns:
            Dictionary with statistics
        """
        return self.doc_service.get_chunks_stats(chunks)

    def get_file_extension(self, file_id: str) -> str:
        """Get file extension from file_id"""
        return self.doc_service.get_file_extension(file_id)
