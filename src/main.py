from fastapi import FastAPI
from routes import base, data, nlp, auth, conversation
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette_exporter import PrometheusMiddleware, handle_metrics

# New LangChain services
from services import EmbeddingsService, PromptService

app = FastAPI()

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware, app_name="rag_finance", group_paths=True)

async def startup_span():
    settings = get_settings()

    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

    # ============================================
    # NEW: LangChain Services (Simplified)
    # ============================================

    # Embeddings Service - Unified interface (local or API)
    app.embeddings_service = EmbeddingsService(
        provider=settings.EMBEDDING_BACKEND,  # "local", "openai", or "cohere"
        model_name=settings.EMBEDDING_MODEL_ID if settings.EMBEDDING_BACKEND != "local" else "multilingual",
        api_key=settings.OPENAI_API_KEY if settings.EMBEDDING_BACKEND == "openai" else settings.COHERE_API_KEY,
        device="cpu"  # or "cuda" if GPU available
    )

    # Prompt Service - Multi-language support
    app.prompt_service = PromptService(language=settings.PRIMARY_LANG)

    # Store embedding dimension for database operations
    app.embedding_dimension = app.embeddings_service.get_embedding_dimension()

    # ============================================
    # LEGACY: Keep old clients for backward compatibility
    # TODO: Remove after full migration
    # ============================================

    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=app.db_client)

    # generation client
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

    # embedding client (LEGACY - will be replaced by app.embeddings_service)
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)

    # vector db client
    app.vectordb_client = vectordb_provider_factory.create(
        provider=settings.VECTOR_DB_BACKEND
    )
    await app.vectordb_client.connect()

    app.template_parser = TemplateParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )


async def shutdown_span():
    await app.db_engine.dispose()
    await app.vectordb_client.disconnect()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(auth.auth_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(conversation.conversation_router)

# Add Prometheus metrics endpoint (obscured path for security)
app.add_route("/TrhBVe_m5gg2002_E5VVqS", handle_metrics)