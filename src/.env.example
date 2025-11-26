#APP
APP_NAME=rag_finance
APP_VERSION=1.0.0

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
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
POSTGRES_MAIN_DATABASE="minirag"

# ========================= LLM Config - Multi Provider =========================
# 🎯 CHOISISSEZ VOTRE PROVIDER ICI : "openai", "cohere","Groq" ou "ollama"
GENERATION_BACKEND=ollama

# 📌 OpenAI Configuration
OPENAI_API_KEY=
# OPENAI_API_URL=  # Optionnel

# 📌 Cohere Configuration
COHERE_API_KEY=

# 📌 Groq Configuration
GROQ_API_KEY=

# 📌 Ollama Configuration (Local - Gratuit)
OLLAMA_BASE_URL=

# Modèle à utiliser selon le provider sélectionné
# Si GENERATION_BACKEND=openai -> utilise gpt-3.5-turbo-0125
# Si GENERATION_BACKEND=cohere -> utilise command-r
# Si GENERATION_BACKEND=ollama -> utilise gemma2:2b
GENERATION_MODEL_ID=gemma2:2b

# Liste des modèles disponibles par provider
GENERATION_MODEL_ID_LITERAL = ["gpt-3.5-turbo-0125","gpt-4o-mini","command-r","command-r-plus","mistral","llama3.1","gemma2:9b"]

# Paramètres de génération
GENERATION_DAFAULT_MAX_TOKENS=1000
GENERATION_DAFAULT_TEMPERATURE=0.7
INPUT_DAFAULT_MAX_CHARACTERS=1024

# ========================= Embeddings Config =========================
# 🎯 CHOISISSEZ : "local" (gratuit), "openai", ou "cohere"
EMBEDDING_BACKEND=local

# Pour embeddings locaux (HuggingFace - GRATUIT)
EMBEDDING_MODEL_ID=multilingual
EMBEDDING_MODEL_SIZE=768
EMBEDDING_DEVICE=cpu

# ========================= Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT"]
VECTOR_DB_BACKEND = "QDRANT"
VECTOR_DB_PATH = "qdrant_db"
VECTOR_DB_DISTANCE_METHOD = "cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD = 100

# ========================= Template Configs =========================
PRIMARY_LANG = "fr"
DEFAULT_LANG = "en"

# JWT Authentication
SECRET_KEY=


# ========================= GUIDE D'UTILISATION =========================
#
# Pour utiliser OpenAI :
#   1. Mettre GENERATION_BACKEND=openai
#   2. Mettre votre clé dans OPENAI_API_KEY
#   3. Choisir un modèle : GENERATION_MODEL_ID=gpt-3.5-turbo-0125
#
# Pour utiliser Cohere :
#   1. Mettre GENERATION_BACKEND=cohere
#   2. Mettre votre clé dans COHERE_API_KEY
#   3. Choisir un modèle : GENERATION_MODEL_ID=command-r
#
# Pour utiliser Ollama (Local - Gratuit) :
#   1. Mettre GENERATION_BACKEND=ollama
#   2. Démarrer le service Ollama : docker compose up -d ollama
#   3. Télécharger un modèle : docker exec ollama ollama pull mistral
#   4. Choisir un modèle : GENERATION_MODEL_ID=mistral
#

# Qdrant URL for Docker service
QDRANT_URL =
