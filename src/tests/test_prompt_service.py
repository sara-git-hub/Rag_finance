"""
Tests for PromptService
"""

import pytest
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from services import PromptService


class TestPromptService:
    """Test suite for PromptService"""

    def test_init_default_language(self):
        """Test initialization with default language"""
        service = PromptService()

        assert service.language == "en"
        assert service.system_prompt is not None

    def test_init_french(self):
        """Test initialization with French"""
        service = PromptService(language="fr")

        assert service.language == "fr"
        assert "français" in service.system_prompt.lower() or "utilisateur" in service.system_prompt

    def test_init_arabic(self):
        """Test initialization with Arabic"""
        service = PromptService(language="ar")

        assert service.language == "ar"
        assert "مستخدم" in service.system_prompt or "وثائق" in service.system_prompt

    def test_format_documents_english(self, sample_documents):
        """Test formatting documents in English"""
        service = PromptService(language="en")

        formatted = service.format_documents(sample_documents)

        assert "Document No:" in formatted
        assert "Content:" in formatted
        assert len(formatted) > 0

    def test_format_documents_french(self, sample_documents):
        """Test formatting documents in French"""
        service = PromptService(language="fr")

        formatted = service.format_documents(sample_documents)

        assert "Document n°" in formatted
        assert "Contenu" in formatted

    def test_format_documents_numbered(self, sample_documents):
        """Test that documents are properly numbered"""
        service = PromptService(language="en")

        formatted = service.format_documents(sample_documents)

        # Check that all documents are numbered
        for i in range(1, len(sample_documents) + 1):
            assert f"Document No: {i}" in formatted

    def test_create_rag_prompt(self):
        """Test creating RAG prompt template"""
        service = PromptService(language="en")

        prompt = service.create_rag_prompt()

        assert isinstance(prompt, ChatPromptTemplate)
        assert prompt is not None

    def test_create_conversational_rag_prompt(self):
        """Test creating conversational RAG prompt"""
        service = PromptService(language="en")

        prompt = service.create_conversational_rag_prompt()

        assert isinstance(prompt, ChatPromptTemplate)
        assert prompt is not None

    def test_get_simple_prompt(self, sample_documents):
        """Test getting simple formatted prompt"""
        service = PromptService(language="en")

        context = service.format_documents(sample_documents)
        prompt = service.get_simple_prompt(
            question="What is finance?",
            context=context
        )

        assert "What is finance?" in prompt
        assert "finance" in prompt.lower()
        assert len(prompt) > 0

    def test_set_language(self):
        """Test changing language"""
        service = PromptService(language="en")

        assert service.language == "en"

        service.set_language("fr")

        assert service.language == "fr"
        assert "utilisateur" in service.system_prompt

    def test_set_invalid_language(self):
        """Test setting invalid language"""
        service = PromptService(language="en")

        with pytest.raises(ValueError, match="Unsupported language"):
            service.set_language("invalid")

    def test_get_language_info(self):
        """Test getting language information"""
        service = PromptService(language="en")

        info = service.get_language_info()

        assert "current_language" in info
        assert "supported_languages" in info
        assert info["current_language"] == "en"
        assert "en" in info["supported_languages"]
        assert "fr" in info["supported_languages"]
        assert "ar" in info["supported_languages"]

    def test_format_empty_documents(self):
        """Test formatting empty document list"""
        service = PromptService(language="en")

        formatted = service.format_documents([])

        assert formatted == ""

    def test_format_documents_with_metadata(self):
        """Test that document metadata is preserved"""
        service = PromptService(language="en")

        docs = [
            Document(
                page_content="Test content",
                metadata={"source": "test.pdf", "page": 1}
            )
        ]

        formatted = service.format_documents(docs)

        assert "Test content" in formatted


class TestPromptServiceConvenience:
    """Test convenience functions"""

    def test_get_rag_prompt(self):
        """Test convenience function for RAG prompt"""
        from services import get_rag_prompt

        prompt = get_rag_prompt(language="fr")

        assert isinstance(prompt, ChatPromptTemplate)

    def test_get_conversational_rag_prompt(self):
        """Test convenience function for conversational RAG prompt"""
        from services import get_conversational_rag_prompt

        prompt = get_conversational_rag_prompt(language="en")

        assert isinstance(prompt, ChatPromptTemplate)
