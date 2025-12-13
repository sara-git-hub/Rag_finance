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

        assert "## Passage:" in formatted
        assert "**Source:**" in formatted
        assert len(formatted) > 0
        # Vérifier que le contenu du document est présent
        assert "finance" in formatted.lower()

    def test_format_documents_french(self, sample_documents):
        """Test formatting documents in French"""
        service = PromptService(language="fr")

        formatted = service.format_documents(sample_documents)

        assert "## Passage :" in formatted
        assert "**Source :**" in formatted
        assert "finance" in formatted.lower()

    def test_format_documents_arabic(self):
        """Test formatting documents in Arabic"""
        service = PromptService(language="ar")

        docs = [Document(page_content="محتوى الاختبار", metadata={"filename": "test.pdf"})]
        formatted = service.format_documents(docs)

        assert "## مقتطف:" in formatted
        assert "**المصدر:**" in formatted
        assert "محتوى" in formatted

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

    def test_format_documents_with_filename_metadata(self):
        """Test formatting avec filename dans metadata"""
        service = PromptService(language="en")

        docs = [
            Document(
                page_content="Document content",
                metadata={"filename": "Report_2024.pdf"}
            )
        ]

        formatted = service.format_documents(docs)

        assert "**Source:** Report_2024.pdf" in formatted
        assert "Document content" in formatted

    def test_format_documents_fallback_to_source(self):
        """Test que source est utilisé si filename absent"""
        service = PromptService(language="en")

        docs = [
            Document(
                page_content="Content here",
                metadata={"source": "fallback_doc.txt"}
            )
        ]

        formatted = service.format_documents(docs)

        assert "fallback_doc.txt" in formatted

    def test_format_documents_default_filename(self):
        """Test fallback vers 'Document' si pas de metadata"""
        service = PromptService(language="en")

        docs = [Document(page_content="Content without metadata", metadata={})]

        formatted = service.format_documents(docs)

        assert "**Source:** Document" in formatted
        assert "Content without metadata" in formatted

    def test_format_documents_language_override(self):
        """Test format_documents avec language override"""
        service = PromptService(language="en")

        docs = [Document(page_content="Test", metadata={"filename": "doc.pdf"})]

        # Override avec français
        formatted_fr = service.format_documents(docs, language="fr")

        assert "## Passage :" in formatted_fr
        assert "**Source :**" in formatted_fr

    def test_format_documents_multiple_docs(self):
        """Test formatting de multiples documents"""
        service = PromptService(language="en")

        docs = [
            Document(page_content="First doc", metadata={"filename": "doc1.pdf"}),
            Document(page_content="Second doc", metadata={"filename": "doc2.pdf"}),
            Document(page_content="Third doc", metadata={"filename": "doc3.pdf"})
        ]

        formatted = service.format_documents(docs)

        # Vérifier que tous les documents sont présents
        assert "First doc" in formatted
        assert "Second doc" in formatted
        assert "Third doc" in formatted
        assert "doc1.pdf" in formatted
        assert "doc2.pdf" in formatted
        assert "doc3.pdf" in formatted
        # Vérifier le nombre de passages
        assert formatted.count("## Passage:") == 3

    def test_create_rag_prompt_all_languages(self):
        """Test create_rag_prompt pour toutes les langues"""
        for lang in ["en", "fr", "ar"]:
            service = PromptService(language=lang)
            prompt = service.create_rag_prompt()

            assert isinstance(prompt, ChatPromptTemplate)
            assert prompt is not None

    def test_create_rag_prompt_contains_variables(self):
        """Test que le prompt RAG contient les variables nécessaires"""
        service = PromptService(language="en")
        prompt = service.create_rag_prompt()

        # Le prompt devrait contenir {context} et {question}
        template_str = str(prompt)
        assert "context" in template_str.lower() or "{" in template_str

    def test_get_simple_prompt_complete(self):
        """Test get_simple_prompt avec question et context complets"""
        service = PromptService(language="fr")

        context = "**Source:** Doc1.pdf\n\nContenu du document financier."
        question = "Quelle est l'inflation?"

        prompt = service.get_simple_prompt(question=question, context=context)

        assert "Quelle est l'inflation?" in prompt
        assert "Doc1.pdf" in prompt
        assert "Contenu du document financier" in prompt
        # Vérifier que le system prompt est inclus
        assert "utilisateur" in prompt.lower() or "document" in prompt.lower()

    def test_init_with_unsupported_language_fallback(self):
        """Test que init avec langue invalide utilise fallback en"""
        # Le code actuel utilise .get() avec fallback
        service = PromptService(language="invalid_lang")

        # Devrait fallback vers "en"
        assert service.language == "invalid_lang"  # Stocke la langue demandée
        assert service.system_prompt == PromptService.SYSTEM_PROMPTS["en"]  # Mais utilise EN

    def test_set_language_updates_all_prompts(self):
        """Test que set_language met à jour tous les prompts"""
        service = PromptService(language="en")

        original_system = service.system_prompt
        original_footer = service.footer_template

        service.set_language("fr")

        # Vérifier que TOUS les prompts ont changé
        assert service.system_prompt != original_system
        assert service.footer_template != original_footer
        assert "utilisateur" in service.system_prompt.lower()

    def test_get_language_info_complete(self):
        """Test get_language_info retourne toutes les infos"""
        service = PromptService(language="ar")

        info = service.get_language_info()

        assert info["current_language"] == "ar"
        assert len(info["supported_languages"]) == 3
        assert set(info["supported_languages"]) == {"en", "fr", "ar"}


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
