from fastapi import FastAPI
from routes import base, data, nlp, auth, conversation, admin
from helpers.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from starlette_exporter import PrometheusMiddleware, handle_metrics
from contextlib import asynccontextmanager

# LangChain services
from services import EmbeddingsService, PromptService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    await startup_span(app)

    yield

    # Shutdown
    await shutdown_span(app)

app = FastAPI(lifespan=lifespan)

# Add Prometheus metrics middleware
app.add_middleware(PrometheusMiddleware, app_name="rag_finance", group_paths=True)

async def startup_span(app: FastAPI):
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

    # ============================================
    # Application Configuration (for NLPController)
    # ============================================

    # Store settings for access in routes
    app.settings = settings

    # PostgreSQL connection string for PGVector (synchronous - psycopg, not asyncpg)
    app.postgres_conn_sync = f"postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    # Generation (LLM) configuration
    app.generation_backend = settings.GENERATION_BACKEND
    app.generation_model = settings.GENERATION_MODEL_ID

    # Set API key based on provider
    if settings.GENERATION_BACKEND == "openai":
        app.generation_api_key = settings.OPENAI_API_KEY
    elif settings.GENERATION_BACKEND == "cohere":
        app.generation_api_key = settings.COHERE_API_KEY
    elif settings.GENERATION_BACKEND == "groq":
        app.generation_api_key = settings.GROQ_API_KEY
    elif settings.GENERATION_BACKEND == "ollama":
        app.generation_api_key = None  # Ollama doesn't need an API key
    else:
        app.generation_api_key = None

    # Vector DB configuration
    app.vector_db_backend = settings.VECTOR_DB_BACKEND.lower()
    app.vector_db_path = settings.VECTOR_DB_PATH
    app.qdrant_url = settings.QDRANT_URL  # URL for remote Qdrant (Docker)


async def shutdown_span(app: FastAPI):
    # Close database connections
    await app.db_engine.dispose()

app.include_router(base.base_router)
app.include_router(auth.auth_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)
app.include_router(conversation.conversation_router)
app.include_router(admin.admin_router)

# Add Prometheus metrics endpoint (obscured path for security)
app.add_route("/TrhBVe_m5gg2002_E5VVqS", handle_metrics)