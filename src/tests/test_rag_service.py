"""
Tests for RAGService
"""

import pytest
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from services import (
    RAGService,
    VectorStoreService,
    EmbeddingsService,
    PromptService,
    create_rag_service
)


class TestRAGServiceStructure:
    """Test RAG service structure (without actual LLM calls)"""

    @pytest.fixture
    def mock_llm(self, mocker):
        """Mock LLM for testing structure"""
        mock = mocker.Mock(spec=ChatOpenAI)
        return mock

    @pytest.fixture
    def vectorstore_with_data(self, test_database_dir, sample_documents):
        """Create vector store with test data"""
        embeddings_service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        vectorstore = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name="test_rag",
            path=str(test_database_dir)
        )

        vectorstore.add_documents(sample_documents)

        yield vectorstore

        # Cleanup
        try:
            vectorstore.delete_collection()
        except:
            pass

    def test_init(self, vectorstore_with_data, mock_llm):
        """Test RAG service initialization"""
        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=mock_llm,
            language="fr"
        )

        assert rag.vectorstore_service is not None
        assert rag.llm is not None
        assert rag.language == "fr"
        assert rag.prompt_service is not None
        assert rag.chain is not None

    def test_set_language(self, vectorstore_with_data, mock_llm):
        """Test changing language"""
        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=mock_llm,
            language="en"
        )

        assert rag.language == "en"

        rag.set_language("fr")

        assert rag.language == "fr"

    def test_update_retriever_config(self, vectorstore_with_data, mock_llm):
        """Test updating retriever configuration"""
        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=mock_llm
        )

        # Should not raise error
        rag.update_retriever_config(
            search_type="similarity",
            k=3
        )

    def test_get_stats(self, vectorstore_with_data, mock_llm):
        """Test getting RAG statistics"""
        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=mock_llm,
            language="fr"
        )

        stats = rag.get_stats()

        assert "language" in stats
        assert "vectorstore" in stats
        assert stats["language"] == "fr"


class TestRAGServiceWithLLM:
    """Test RAG service with actual LLM (requires API key)"""

    @pytest.fixture
    def vectorstore_with_data(self, test_database_dir):
        """Create vector store with test data"""
        embeddings_service = EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

        vectorstore = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name="test_rag_llm",
            path=str(test_database_dir)
        )

        # Add relevant documents
        docs = [
            Document(page_content="LangChain est un framework pour développer des applications basées sur des LLMs."),
            Document(page_content="Python est le langage principal utilisé avec LangChain."),
            Document(page_content="RAG signifie Retrieval-Augmented Generation."),
        ]
        vectorstore.add_documents(docs)

        yield vectorstore

        # Cleanup
        try:
            vectorstore.delete_collection()
        except:
            pass

    def test_answer(self, vectorstore_with_data, openai_api_key):
        """Test basic answer generation"""
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
            temperature=0.7
        )

        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=llm,
            language="fr"
        )

        result = rag.answer("Qu'est-ce que LangChain?")

        assert "answer" in result
        assert isinstance(result["answer"], str)
        assert len(result["answer"]) > 0

    def test_answer_with_sources(self, vectorstore_with_data, openai_api_key):
        """Test answer with source documents"""
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
            temperature=0.7
        )

        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=llm,
            language="fr"
        )

        result = rag.answer_with_sources("Qu'est-ce que RAG?")

        assert "answer" in result
        assert "sources" in result
        assert isinstance(result["sources"], list)
        assert len(result["sources"]) > 0

    def test_stream_answer(self, vectorstore_with_data, openai_api_key):
        """Test streaming answer"""
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
            temperature=0.7
        )

        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=llm,
            language="fr"
        )

        chunks = list(rag.stream_answer("Qu'est-ce que Python?"))

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_batch_answer(self, vectorstore_with_data, openai_api_key):
        """Test batch answer generation"""
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            api_key=openai_api_key,
            temperature=0.7
        )

        rag = RAGService(
            vectorstore_service=vectorstore_with_data,
            llm=llm,
            language="fr"
        )

        questions = [
            "Qu'est-ce que LangChain?",
            "Qu'est-ce que RAG?"
        ]

        answers = rag.batch_answer(questions)

        assert len(answers) == 2
        assert all(isinstance(answer, str) for answer in answers)


class TestRAGServiceFactory:
    """Test RAG service factory function"""

    def test_create_rag_service_openai(self, test_database_dir, openai_api_key):
        """Test creating RAG service with factory"""
        # Create vector store
        embeddings_service = EmbeddingsService(provider="local", model_name="multilingual-mini")
        vectorstore = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name="test_factory",
            path=str(test_database_dir)
        )

        # Add test data
        docs = [Document(page_content="Test content")]
        vectorstore.add_documents(docs)

        # Create RAG service
        rag = create_rag_service(
            vectorstore_service=vectorstore,
            llm_provider="openai",
            model_name="gpt-3.5-turbo",
            api_key=openai_api_key,
            language="fr"
        )

        assert rag is not None
        assert rag.language == "fr"

        # Cleanup
        try:
            vectorstore.delete_collection()
        except:
            pass

    def test_create_rag_service_invalid_provider(self, test_database_dir):
        """Test factory with invalid LLM provider"""
        embeddings_service = EmbeddingsService(provider="local", model_name="multilingual-mini")
        vectorstore = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name="test_invalid",
            path=str(test_database_dir)
        )

        with pytest.raises(ValueError, match="Unsupported LLM provider"):
            create_rag_service(
                vectorstore_service=vectorstore,
                llm_provider="invalid_provider"
            )
