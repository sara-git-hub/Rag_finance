"""
NLPController - Version LangChain
Gère les opérations RAG avec les nouveaux services
"""

from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from typing import List, Optional
from langchain_core.documents import Document
from services import VectorStoreService, RAGService
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere


class NLPController(BaseController):
    """Controller NLP utilisant les services LangChain"""

    def __init__(self, embeddings_service, prompt_service, generation_backend: str,
                 generation_model: str, api_key: str, vector_db_backend: str = "qdrant",
                 vector_db_path: str = "assets/database"):
        """
        Initialize NLP Controller with LangChain services

        Args:
            embeddings_service: EmbeddingsService instance
            prompt_service: PromptService instance
            generation_backend: "openai" or "cohere"
            generation_model: Model ID
            api_key: API key for generation
            vector_db_backend: "qdrant" or "pgvector"
            vector_db_path: Path for vector DB storage
        """
        super().__init__()

        self.embeddings_service = embeddings_service
        self.prompt_service = prompt_service
        self.generation_backend = generation_backend
        self.generation_model = generation_model
        self.api_key = api_key
        self.vector_db_backend = vector_db_backend
        self.vector_db_path = vector_db_path

        # Cache for vector stores (one per project)
        self._vectorstores = {}

    def create_collection_name(self, project_id: str) -> str:
        """Generate collection name for project"""
        embedding_size = self.embeddings_service.get_embedding_dimension()
        return f"collection_{embedding_size}_{project_id}".strip()

    def _get_vectorstore(self, project: Project) -> VectorStoreService:
        """
        Get or create VectorStoreService for a project

        Args:
            project: Project instance

        Returns:
            VectorStoreService instance
        """
        project_id = project.project_id
        collection_name = self.create_collection_name(project_id)

        # Return cached if exists
        if project_id in self._vectorstores:
            return self._vectorstores[project_id]

        # Create new VectorStoreService
        vectorstore = VectorStoreService(
            embeddings=self.embeddings_service.embeddings,
            provider=self.vector_db_backend,
            collection_name=collection_name,
            path=self.vector_db_path,
            distance="cosine"
        )

        # Cache it
        self._vectorstores[project_id] = vectorstore

        return vectorstore

    def _get_llm(self):
        """Get LLM instance based on configuration"""
        if self.generation_backend == "openai":
            return ChatOpenAI(
                model=self.generation_model,
                openai_api_key=self.api_key,
                temperature=0.7,
                max_tokens=1000
            )
        elif self.generation_backend == "cohere":
            return ChatCohere(
                model=self.generation_model,
                cohere_api_key=self.api_key,
                temperature=0.7,
                max_tokens=1000
            )
        else:
            raise ValueError(f"Unsupported generation backend: {self.generation_backend}")

    async def reset_vector_db_collection(self, project: Project) -> bool:
        """
        Reset (delete) vector DB collection for a project

        Args:
            project: Project instance

        Returns:
            True if successful
        """
        try:
            vectorstore = self._get_vectorstore(project)
            vectorstore.delete_collection()

            # Remove from cache
            if project.project_id in self._vectorstores:
                del self._vectorstores[project.project_id]

            return True
        except Exception as e:
            print(f"Error resetting collection: {e}")
            return False

    async def get_vector_db_collection_info(self, project: Project) -> dict:
        """
        Get vector DB collection information

        Args:
            project: Project instance

        Returns:
            Dictionary with collection info
        """
        vectorstore = self._get_vectorstore(project)
        return vectorstore.get_stats()

    async def index_into_vector_db(
        self,
        project: Project,
        chunks: List[DataChunk],
        chunks_ids: List[int],
        do_reset: bool = False
    ) -> bool:
        """
        Index chunks into vector database

        Args:
            project: Project instance
            chunks: List of DataChunk objects
            chunks_ids: List of chunk IDs
            do_reset: Whether to reset collection before indexing

        Returns:
            True if successful
        """
        try:
            # Reset if requested
            if do_reset:
                await self.reset_vector_db_collection(project)

            # Get vectorstore
            vectorstore = self._get_vectorstore(project)

            # Convert DataChunk to LangChain Documents
            documents = [
                Document(
                    page_content=chunk.chunk_text,
                    metadata={
                        "chunk_id": chunk_id,
                        "project_id": project.project_id,
                        **(chunk.chunk_metadata or {})
                    }
                )
                for chunk, chunk_id in zip(chunks, chunks_ids)
            ]

            # Add documents to vector store
            vectorstore.add_documents(documents, batch_size=50)

            return True

        except Exception as e:
            print(f"Error indexing into vector DB: {e}")
            return False

    async def search_vector_db_collection(
        self,
        project: Project,
        text: str,
        limit: int = 10
    ) -> Optional[List[dict]]:
        """
        Search vector DB collection

        Args:
            project: Project instance
            text: Query text
            limit: Number of results

        Returns:
            List of search results or None
        """
        try:
            vectorstore = self._get_vectorstore(project)

            # Search with scores
            results = vectorstore.similarity_search_with_score(text, k=limit)

            if not results:
                return None

            # Format results to match old interface
            formatted_results = []
            for doc, score in results:
                formatted_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": float(score),
                    "chunk_id": doc.metadata.get("chunk_id")
                })

            return formatted_results

        except Exception as e:
            print(f"Error searching vector DB: {e}")
            return None

    async def answer_rag_question(
        self,
        project: Project,
        query: str,
        limit: int = 10,
        conversation_history: Optional[List[dict]] = None
    ) -> tuple:
        """
        Generate RAG answer using LangChain

        Args:
            project: Project instance
            query: User question
            limit: Number of documents to retrieve
            conversation_history: Optional conversation history
                                  Format: [{"role": "user", "content": "..."}, ...]

        Returns:
            Tuple: (answer, sources, conversation_context)
        """
        try:
            # Get vectorstore and LLM
            vectorstore = self._get_vectorstore(project)
            llm = self._get_llm()

            # Update retriever config
            vectorstore_service = vectorstore

            # Create RAG service
            rag_service = RAGService(
                vectorstore_service=vectorstore_service,
                llm=llm,
                prompt_service=self.prompt_service,
                language=self.prompt_service.language
            )

            # Update retriever to fetch more documents
            rag_service.update_retriever_config(search_type="similarity", k=limit)

            # Generate answer with sources
            result = rag_service.answer_with_sources(query)

            answer = result.get("answer", "")
            sources = result.get("sources", [])

            # Format sources for compatibility
            formatted_sources = [
                {
                    "text": src["content"],
                    "metadata": src["metadata"]
                }
                for src in sources
            ]

            # Return in old format
            return answer, formatted_sources, conversation_history

        except Exception as e:
            print(f"Error answering RAG question: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None

    async def stream_rag_answer(self, project: Project, query: str, limit: int = 10):
        """
        Stream RAG answer token by token

        Args:
            project: Project instance
            query: User question
            limit: Number of documents to retrieve

        Yields:
            Answer tokens
        """
        try:
            vectorstore = self._get_vectorstore(project)
            llm = self._get_llm()

            rag_service = RAGService(
                vectorstore_service=vectorstore,
                llm=llm,
                prompt_service=self.prompt_service
            )

            rag_service.update_retriever_config(k=limit)

            # Stream answer
            for token in rag_service.stream_answer(query):
                yield token

        except Exception as e:
            print(f"Error streaming answer: {e}")
            yield f"Error: {str(e)}"
