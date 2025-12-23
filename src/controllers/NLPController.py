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
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
import os


class NLPController(BaseController):
    """Controller NLP utilisant les services LangChain"""

    def __init__(self, embeddings_service, prompt_service, generation_backend: str,
                 generation_model: str, api_key: str, vector_db_backend: str = "qdrant",
                 vector_db_path: str = "assets/database", connection_string: str = None,
                 qdrant_url: str = None, max_tokens: int = 1000, temperature: float = 0.7):
        """
        Initialize NLP Controller with LangChain services

        Args:
            embeddings_service: EmbeddingsService instance
            prompt_service: PromptService instance
            generation_backend: "openai", "cohere", "ollama", or "groq"
            generation_model: Model ID
            api_key: API key for generation (not needed for ollama)
            vector_db_backend: "qdrant" or "pgvector"
            vector_db_path: Path for vector DB storage (for local Qdrant)
            connection_string: PostgreSQL connection string (for PGVector)
            qdrant_url: URL for remote Qdrant (e.g. http://qdrant:6333 in Docker)
            max_tokens: Maximum tokens for generation (default: 1000)
            temperature: Temperature for generation (default: 0.7)
        """
        super().__init__()

        self.embeddings_service = embeddings_service
        self.prompt_service = prompt_service
        self.generation_backend = generation_backend
        self.generation_model = generation_model
        self.api_key = api_key
        self.vector_db_backend = vector_db_backend
        self.vector_db_path = vector_db_path
        self.connection_string = connection_string
        self.qdrant_url = qdrant_url
        self.max_tokens = max_tokens
        self.temperature = temperature

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

        # Prepare config based on provider
        #config = {"distance": "cosine"}
        config = {"distance": self.app_settings.VECTOR_DB_DISTANCE_METHOD or "cosine"}

        if self.vector_db_backend == "pgvector":
            # For PGVector, use connection_string
            config["connection_string"] = self.connection_string
        else:
            # For Qdrant: use URL if provided (Docker), otherwise use path (local)
            if self.qdrant_url:
                config["url"] = self.qdrant_url
            else:
                config["path"] = self.vector_db_path

        # Create new VectorStoreService with async_client
        vectorstore = VectorStoreService(
            embeddings=self.embeddings_service.embeddings,
            provider=self.vector_db_backend,
            collection_name=collection_name,
            **config
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
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        elif self.generation_backend == "cohere":
            return ChatCohere(
                model=self.generation_model,
                cohere_api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        elif self.generation_backend == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            return ChatOllama(
                model=self.generation_model,
                base_url=base_url,
                temperature=self.temperature,
                num_predict=self.max_tokens
            )
        elif self.generation_backend == "groq":
            return ChatGroq(
                model=self.generation_model,
                groq_api_key=self.api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported generation backend: {self.generation_backend}. Supported: openai, cohere, ollama, groq")

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

    async def delete_vectors_by_chunk_ids(self, project: Project, chunk_ids: List[int]) -> bool:
        """
        Delete vectors from collection by chunk IDs

        Args:
            project: Project instance
            chunk_ids: List of chunk IDs to delete

        Returns:
            True if successful
        """
        try:
            if not chunk_ids:
                return True

            vectorstore = self._get_vectorstore(project)

            # Delete vectors with matching chunk_ids in metadata
            success = vectorstore.delete_by_metadata({"chunk_id": {"$in": chunk_ids}})

            return success
        except Exception as e:
            print(f"Error deleting vectors by chunk_ids: {e}")
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

    def search_vector_db_collection(
        self,
        project: Project,
        text: str,
        limit: int = 10
    ) -> Optional[List[dict]]:
        """
        Search vector DB collection (SYNC version - deprecated, use async version)

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
                # Convert distance to similarity for better UX
                # PGVector returns distance (smaller = more similar)
                # We convert to similarity (larger = more similar)
                if self.vector_db_backend == "pgvector":
                    # For cosine distance: similarity = 1 - distance
                    similarity_score = 1.0 - float(score)
                else:
                    # For other backends, keep original score
                    similarity_score = float(score)

                formatted_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": similarity_score,
                    "chunk_id": doc.metadata.get("chunk_id")
                })

            return formatted_results

        except Exception as e:
            print(f"Error searching vector DB: {e}")
            return None

    async def asearch_vector_db_collection(
        self,
        project: Project,
        text: str,
        limit: int = 10
    ) -> Optional[List[dict]]:
        """
        ASYNC version: Search vector DB collection

        Args:
            project: Project instance
            text: Query text
            limit: Number of results

        Returns:
            List of search results or None
        """
        try:
            vectorstore = self._get_vectorstore(project)

            # Use async search method
            results = await vectorstore.asimilarity_search_with_score(text, k=limit)

            if not results:
                return None

            # Format results to match old interface
            formatted_results = []
            for doc, score in results:
                # Convert distance to similarity for better UX
                # PGVector returns distance (smaller = more similar)
                # We convert to similarity (larger = more similar)
                if self.vector_db_backend == "pgvector":
                    # For cosine distance: similarity = 1 - distance
                    similarity_score = 1.0 - float(score)
                else:
                    # For other backends, keep original score
                    similarity_score = float(score)

                formatted_results.append({
                    "text": doc.page_content,
                    "metadata": doc.metadata,
                    "score": similarity_score,
                    "chunk_id": doc.metadata.get("chunk_id")
                })

            return formatted_results

        except Exception as e:
            print(f"Error searching vector DB (async): {e}")
            return None

    async def aanswer_rag_question(
        self,
        project: Project,
        query: str,
        limit: int = 10,
        conversation_history: Optional[List[dict]] = None
    ) -> tuple:
        """
        ASYNC version: Generate RAG answer using LangChain native async

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

            # Get project language (default to "fr" if not set)
            project_language = getattr(project, 'project_language', 'fr')

            # Create PromptService with project-specific language
            from services import PromptService
            project_prompt_service = PromptService(language=project_language)

            # Create RAG service with project-specific language
            rag_service = RAGService(
                vectorstore_service=vectorstore_service,
                llm=llm,
                prompt_service=project_prompt_service,
                language=project_language
            )

            # Update retriever to fetch more documents
            rag_service.update_retriever_config(search_type="similarity", k=limit)

            # Generate answer with sources using ASYNC method
            # Use conversational method if history is provided
            if conversation_history:
                result = await rag_service.aanswer_with_sources_and_history(
                    question=query,
                    chat_history=conversation_history
                )
            else:
                result = await rag_service.aanswer_with_sources(query)

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
            print(f"Error answering RAG question (async): {e}")
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

            # Get project language (default to "fr" if not set)
            project_language = getattr(project, 'project_language', 'fr')

            # Create PromptService with project-specific language
            from services import PromptService
            project_prompt_service = PromptService(language=project_language)

            rag_service = RAGService(
                vectorstore_service=vectorstore,
                llm=llm,
                prompt_service=project_prompt_service,
                language=project_language
            )

            rag_service.update_retriever_config(k=limit)

            # Stream answer
            for token in rag_service.stream_answer(query):
                yield token

        except Exception as e:
            print(f"Error streaming answer: {e}")
            yield f"Error: {str(e)}"
