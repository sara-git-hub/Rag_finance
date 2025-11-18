"""
Tests for VectorStoreService
"""

import pytest
from langchain_core.documents import Document
from services import VectorStoreService, EmbeddingsService


class TestVectorStoreServiceQdrant:
    """Test suite for VectorStoreService with Qdrant"""

    @pytest.fixture
    def embeddings_service(self):
        """Create embeddings service for tests"""
        return EmbeddingsService(
            provider="local",
            model_name="multilingual-mini",
            device="cpu"
        )

    @pytest.fixture
    def vectorstore(self, embeddings_service, test_database_dir, test_collection_name):
        """Create vector store for tests"""
        store = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name=test_collection_name,
            path=str(test_database_dir),
            distance="cosine"
        )
        yield store
        # Cleanup
        try:
            store.delete_collection()
        except:
            pass

    def test_init_qdrant(self, embeddings_service, test_database_dir):
        """Test initialization of Qdrant vector store"""
        store = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name="test_init",
            path=str(test_database_dir)
        )

        assert store.provider == "qdrant"
        assert store.collection_name == "test_init"
        assert store.vectorstore is not None

    def test_add_documents(self, vectorstore, sample_documents):
        """Test adding documents to vector store"""
        ids = vectorstore.add_documents(sample_documents)

        assert len(ids) == len(sample_documents)

    def test_add_empty_documents(self, vectorstore):
        """Test adding empty document list"""
        ids = vectorstore.add_documents([])

        assert ids == []

    def test_similarity_search(self, vectorstore, sample_documents):
        """Test similarity search"""
        # Add documents first
        vectorstore.add_documents(sample_documents)

        # Search
        results = vectorstore.similarity_search("finance", k=2)

        assert len(results) <= 2
        assert all(isinstance(doc, Document) for doc in results)

    def test_similarity_search_with_score(self, vectorstore, sample_documents):
        """Test similarity search with scores"""
        vectorstore.add_documents(sample_documents)

        results = vectorstore.similarity_search_with_score("finance", k=2)

        assert len(results) <= 2
        for doc, score in results:
            assert isinstance(doc, Document)
            assert isinstance(score, (int, float))

    def test_as_retriever(self, vectorstore, sample_documents):
        """Test getting retriever interface"""
        vectorstore.add_documents(sample_documents)

        retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 2}
        )

        assert retriever is not None

        # Test retriever
        results = retriever.invoke("finance")
        assert len(results) <= 2

    def test_as_retriever_mmr(self, vectorstore, sample_documents):
        """Test MMR retriever"""
        vectorstore.add_documents(sample_documents)

        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 2, "fetch_k": 3, "lambda_mult": 0.7}
        )

        results = retriever.invoke("finance")
        assert len(results) <= 2

    def test_get_stats(self, vectorstore, sample_documents):
        """Test getting vector store statistics"""
        vectorstore.add_documents(sample_documents)

        stats = vectorstore.get_stats()

        assert "provider" in stats
        assert "collection_name" in stats
        assert stats["provider"] == "qdrant"

    def test_delete_collection(self, embeddings_service, test_database_dir):
        """Test deleting collection"""
        store = VectorStoreService(
            embeddings=embeddings_service.embeddings,
            provider="qdrant",
            collection_name="test_delete",
            path=str(test_database_dir)
        )

        # Add some documents
        docs = [Document(page_content="Test")]
        store.add_documents(docs)

        # Delete
        store.delete_collection()

        # Should succeed without error


class TestVectorStoreServiceErrors:
    """Test error handling"""

    def test_invalid_provider(self):
        """Test initialization with invalid provider"""
        embeddings = EmbeddingsService(provider="local", model_name="multilingual-mini")

        with pytest.raises(ValueError, match="Unsupported provider"):
            VectorStoreService(
                embeddings=embeddings.embeddings,
                provider="invalid_provider",
                collection_name="test"
            )

    def test_pgvector_without_connection_string(self):
        """Test PGVector without connection string"""
        embeddings = EmbeddingsService(provider="local", model_name="multilingual-mini")

        with pytest.raises(ValueError, match="connection_string"):
            VectorStoreService(
                embeddings=embeddings.embeddings,
                provider="pgvector",
                collection_name="test"
                # Missing connection_string
            )
