from fastapi import FastAPI
from routes import base, data, nlp, auth, conversation
from helpers.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette_exporter import PrometheusMiddleware, handle_metrics

# LangChain services
from services import EmbeddingsService, PromptService

app = FastAPI()

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware, app_name="rag_finance", group_paths=True)

async def startup_span():
    settings = get_settings()

    # PostgreSQL Database Connection
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        app.db_engine, class_=AsyncSession, expire_on_commit=False
    )

    # ============================================
    # LangChain Services
    # ============================================

    # Embeddings Service - Unified interface (local or API)
    app.embeddings_service = EmbeddingsService(
        provider=settings.EMBEDDING_BACKEND,  # "local", "openai", or "cohere"
        model_name=settings.EMBEDDING_MODEL_ID if settings.EMBEDDING_BACKEND != "local" else "multilingual",
        api_key=settings.OPENAI_API_KEY if settings.EMBEDDING_BACKEND == "openai" else settings.COHERE_API_KEY,
        device=getattr(settings, "EMBEDDING_DEVICE", "cpu")  # or "cuda" if GPU available
    )

    # Prompt Service - Multi-language support
    app.prompt_service = PromptService(language=settings.PRIMARY_LANG)

    # Store embedding dimension for database operations
    app.embedding_dimension = app.embeddings_service.get_embedding_dimension()


async def shutdown_span():
    await app.db_engine.dispose()

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(auth.auth_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(conversation.conversation_router)

# Add Prometheus metrics endpoint (obscured path for security)
app.add_route("/TrhBVe_m5gg2002_E5VVqS", handle_metrics)