FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm

WORKDIR /app

# Install additional system dependencies for lxml and other packages
# + PyTorch CPU dependencies for HuggingFace embeddings
RUN apt-get update && apt-get install -y \
    build-essential \
    libavif-dev pkg-config \
    libjpeg-dev \
    gcc unzip zip \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY src/requirements.txt .

# Install Python dependencies
RUN uv pip install -r requirements.txt --system

# Pre-download HuggingFace models to avoid runtime download
# This embeds the model in the Docker image (~420 MB)
RUN python3 -c "\
from sentence_transformers import SentenceTransformer; \
print('Downloading multilingual model...'); \
SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2', cache_folder='/root/.cache/huggingface'); \
print('Model downloaded successfully!'); \
"

COPY src/ .

# Create directory structure for Alembic
RUN mkdir -p /app/models/db_schemes/minirag/

COPY docker/minirag/alembic.ini /app/models/db_schemes/minirag/alembic.ini

COPY docker/minirag/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set environment variable for HuggingFace cache
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface
ENV SENTENCE_TRANSFORMERS_HOME=/root/.cache/huggingface

ENTRYPOINT ["/entrypoint.sh"]

# Command to run the application
# Reduced workers from 4 to 2 to save RAM with embeddings model
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]