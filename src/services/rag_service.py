"""
RAG Service
Complete RAG pipeline using LangChain Expression Language (LCEL)
Handles retrieval, context building, and generation
"""

from typing import List, Optional, Callable
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_cohere import ChatCohere
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os

from .vectorstore_service import VectorStoreService
from .prompt_service import PromptService


class RAGService:
    """Complete RAG service using LCEL"""

    def __init__(
        self,
        vectorstore_service: VectorStoreService,
        llm: BaseChatModel,
        prompt_service: Optional[PromptService] = None,
        language: str = "en"
    ):
        """
        Initialize RAG Service

        Args:
            vectorstore_service: Vector store service for retrieval
            llm: LangChain chat model
            prompt_service: Prompt service (optional, will create default)
            language: Language for prompts
        """
        self.vectorstore_service = vectorstore_service
        self.llm = llm
        self.language = language

        # Initialize prompt service
        self.prompt_service = prompt_service or PromptService(language=language)

        # Build RAG chain
        self.chain = self._build_rag_chain()

    def _build_rag_chain(self):
        """
        Build RAG chain using LCEL

        Pipeline:
        1. Retrieve relevant documents
        2. Format documents as context
        3. Create prompt with context + question
        4. Generate answer with LLM
        5. Parse output
        """
        # Get retriever from vector store
        retriever = self.vectorstore_service.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

        # Get prompt template
        prompt = self.prompt_service.create_rag_prompt()

        # Build LCEL chain
        chain = (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return chain

    def _format_docs(self, docs: List[Document]) -> str:
        """Format documents for context"""
        return self.prompt_service.format_documents(docs, self.language)

    def answer(
        self,
        question: str,
        return_sources: bool = False
    ) -> dict:
        """
        Answer a question using RAG

        Args:
            question: User question
            return_sources: Whether to return source documents

        Returns:
            Dictionary with answer and optionally sources
        """
        # Generate answer
        answer = self.chain.invoke(question)

        result = {"answer": answer}

        # Optionally include source documents
        if return_sources:
            retriever = self.vectorstore_service.as_retriever(
                search_kwargs={"k": 5}
            )
            sources = retriever.invoke(question)
            result["sources"] = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in sources
            ]

        return result

    def answer_with_sources(self, question: str) -> dict:
        """
        Answer with source documents included

        Args:
            question: User question

        Returns:
            Dictionary with answer and sources
        """
        # Build chain that returns both answer and sources
        retriever = self.vectorstore_service.as_retriever(
            search_kwargs={"k": 5}
        )

        prompt = self.prompt_service.create_rag_prompt()

        # Parallel chain: retrieve docs and pass question
        chain_with_sources = RunnableParallel(
            {
                "answer": (
                    {
                        "context": retriever | self._format_docs,
                        "question": RunnablePassthrough()
                    }
                    | prompt
                    | self.llm
                    | StrOutputParser()
                ),
                "sources": retriever
            }
        )

        result = chain_with_sources.invoke(question)

        # Format sources
        result["sources"] = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result["sources"]
        ]

        return result

    async def aanswer_with_sources(self, question: str) -> dict:
        """
        ASYNC version: Answer with source documents included

        Args:
            question: User question

        Returns:
            Dictionary with answer and sources
        """
        # Build chain that returns both answer and sources
        retriever = self.vectorstore_service.as_retriever(
            search_kwargs={"k": 5}
        )

        prompt = self.prompt_service.create_rag_prompt()

        # Parallel chain: retrieve docs and pass question
        chain_with_sources = RunnableParallel(
            {
                "answer": (
                    {
                        "context": retriever | self._format_docs,
                        "question": RunnablePassthrough()
                    }
                    | prompt
                    | self.llm
                    | StrOutputParser()
                ),
                "sources": retriever
            }
        )

        # Use ainvoke for async execution
        result = await chain_with_sources.ainvoke(question)

        # Format sources
        result["sources"] = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result["sources"]
        ]

        return result

    async def aanswer_with_sources_and_history(
        self,
        question: str,
        chat_history: Optional[List[dict]] = None
    ) -> dict:
        """
        ASYNC version: Answer with source documents and conversation history

        Args:
            question: User question
            chat_history: Optional conversation history
                         Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

        Returns:
            Dictionary with answer and sources
        """
        # Build chain that returns both answer and sources
        retriever = self.vectorstore_service.as_retriever(
            search_kwargs={"k": 5}
        )

        # Use conversational prompt if history provided
        if chat_history:
            from langchain_core.messages import HumanMessage, AIMessage

            prompt = self.prompt_service.create_conversational_rag_prompt()

            # Convert history to LangChain message format
            formatted_history = []
            for msg in chat_history:
                if msg["role"] == "user":
                    formatted_history.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    formatted_history.append(AIMessage(content=msg["content"]))

            # Parallel chain with history
            chain_with_sources = RunnableParallel(
                {
                    "answer": (
                        {
                            "context": retriever | self._format_docs,
                            "question": RunnablePassthrough(),
                            "chat_history": lambda x: formatted_history  # Pass history
                        }
                        | prompt
                        | self.llm
                        | StrOutputParser()
                    ),
                    "sources": retriever
                }
            )
        else:
            # Use regular prompt without history
            prompt = self.prompt_service.create_rag_prompt()

            chain_with_sources = RunnableParallel(
                {
                    "answer": (
                        {
                            "context": retriever | self._format_docs,
                            "question": RunnablePassthrough()
                        }
                        | prompt
                        | self.llm
                        | StrOutputParser()
                    ),
                    "sources": retriever
                }
            )

        # Use ainvoke for async execution
        result = await chain_with_sources.ainvoke(question)

        # Format sources
        result["sources"] = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in result["sources"]
        ]

        return result

    def stream_answer(self, question: str):
        """
        Stream answer token by token

        Args:
            question: User question

        Yields:
            Answer tokens
        """
        for chunk in self.chain.stream(question):
            yield chunk

    def batch_answer(self, questions: List[str]) -> List[str]:
        """
        Answer multiple questions in batch

        Args:
            questions: List of questions

        Returns:
            List of answers
        """
        return self.chain.batch(questions)

    def update_retriever_config(
        self,
        search_type: str = "similarity",
        k: int = 5,
        **kwargs
    ):
        """
        Update retriever configuration and rebuild chain

        Args:
            search_type: Type of search ("similarity", "mmr", etc.)
            k: Number of documents to retrieve
            **kwargs: Additional search arguments
        """
        search_kwargs = {"k": k, **kwargs}

        # Rebuild chain with new retriever
        retriever = self.vectorstore_service.as_retriever(
            search_type=search_type,
            search_kwargs=search_kwargs
        )

        prompt = self.prompt_service.create_rag_prompt()

        self.chain = (
            {
                "context": retriever | self._format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def set_language(self, language: str):
        """
        Change prompt language

        Args:
            language: New language ("en", "fr", "ar")
        """
        self.language = language
        self.prompt_service.set_language(language)

        # Rebuild chain with new prompts
        self.chain = self._build_rag_chain()

    def get_stats(self) -> dict:
        """Get RAG service statistics"""
        return {
            "language": self.language,
            "llm_model": getattr(self.llm, "model_name", "unknown"),
            "vectorstore": self.vectorstore_service.get_stats()
        }


def create_rag_service(
    vectorstore_service: VectorStoreService,
    llm_provider: str = "openai",
    model_name: str = None,
    api_key: str = None,
    language: str = "en",
    **llm_kwargs
) -> RAGService:
    """
    Factory function to create RAG service

    Args:
        vectorstore_service: Vector store service
        llm_provider: LLM provider ("openai" or "cohere")
        model_name: Model name
        api_key: API key
        language: Prompt language
        **llm_kwargs: Additional LLM arguments

    Returns:
        RAGService instance
    """
    # Initialize LLM
    if llm_provider == "openai":
        model_name = model_name or "gpt-4"
        llm = ChatOpenAI(
            model=model_name,
            openai_api_key=api_key,
            temperature=llm_kwargs.get("temperature", 0.7),
            max_tokens=llm_kwargs.get("max_tokens", 1000)
        )
    elif llm_provider == "cohere":
        model_name = model_name or "command-r-plus"
        llm = ChatCohere(
            model=model_name,
            cohere_api_key=api_key,
            temperature=llm_kwargs.get("temperature", 0.7),
            max_tokens=llm_kwargs.get("max_tokens", 1000)
        )
    elif llm_provider == "ollama":
        model_name = model_name or "mistral"
        # Get Ollama base URL from environment or use default
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=llm_kwargs.get("temperature", 0.7),
            num_predict=llm_kwargs.get("max_tokens", 1000)
        )
    elif llm_provider == "groq":
        model_name = model_name or "llama-3.1-70b-versatile"
        llm = ChatGroq(
            model=model_name,
            groq_api_key=api_key,
            temperature=llm_kwargs.get("temperature", 0.7),
            max_tokens=llm_kwargs.get("max_tokens", 1000)
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}. Supported: openai, cohere, ollama, groq")

    # Initialize prompt service
    prompt_service = PromptService(language=language)

    # Create RAG service
    return RAGService(
        vectorstore_service=vectorstore_service,
        llm=llm,
        prompt_service=prompt_service,
        language=language
    )
