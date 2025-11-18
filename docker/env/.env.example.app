#APP
APP_NAME=rag_finance
APP_VERSION=1.0.0
SECRET_KEY=your-secret-key-here-change-in-production

#FILE
FILE_ALLOWED_TYPES= ["text/plain","application/pdf"]
FILE_MAX_SIZE= 10
FILE_DEFAULT_CHUNK_SIZE= 512000 # 512 kb

#BAM API KEYS
CLE_API_CHANGES=
CLE_API_CHANGES_2=
CLE_API_BDT=
CLE_API_BDT_2=
CLE_API_OBLIG=
CLE_API_OBLIG_2=

#POSTGRES
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=your-postgres-password
POSTGRES_HOST=pgvector
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE=minirag

# ========================= LLM Config (LangChain) =========================
# Generation Backend: "openai" or "cohere"
GENERATION_BACKEND=openai
GENERATION_MODEL_ID=gpt-3.5-turbo-0125
GENERATION_DAFAULT_MAX_TOKENS=200
GENERATION_DAFAULT_TEMPERATURE=0.1

# ========================= Embeddings Config (LangChain) =========================
# Embedding Backend: "local" (HuggingFace - FREE!), "openai", or "cohere"
# Recommended: "local" for cost savings and privacy
EMBEDDING_BACKEND=local

# For LOCAL embeddings (HuggingFace):
# Options:
#   - "multilingual" = paraphrase-multilingual-mpnet-base-v2 (768 dims, FR/EN/AR)
#   - "multilingual-mini" = paraphrase-multilingual-MiniLM-L12-v2 (384 dims, faster)
#   - "english" = all-mpnet-base-v2 (768 dims, EN only)
#   - "english-mini" = all-MiniLM-L6-v2 (384 dims, EN only, fastest)
EMBEDDING_MODEL_ID=multilingual
EMBEDDING_MODEL_SIZE=768
EMBEDDING_DEVICE=cpu

# API Keys (only needed if EMBEDDING_BACKEND != "local")
OPENAI_API_KEY=
OPENAI_API_URL=
COHERE_API_KEY=

# Legacy settings (backward compatibility)
GENERATION_MODEL_ID_LITERAL=["gemma2:9b-instruct-q5_0","gpt-4o-mini", "gpt-4o"]
INPUT_DAFAULT_MAX_CHARACTERS=1024

# ========================= Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL=["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND=PGVECTOR
VECTOR_DB_PATH=qdrant_db
VECTOR_DB_DISTANCE_METHOD=cosine
VECTOR_DB_PGVEC_INDEX_THRESHOLD=100

# ========================= Template/Language Configs =========================
PRIMARY_LANG=en
DEFAULT_LANG=en

# ========================= HuggingFace Cache (Docker) =========================
# These are set automatically in docker-compose.yml
# TRANSFORMERS_CACHE=/root/.cache/huggingface
# SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface
