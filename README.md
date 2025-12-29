# MiniRAG - Système RAG avec LangChain

Plateforme de Retrieval-Augmented Generation (RAG) permettant l'analyse de documents PDF et la génération de réponses intelligentes via LLM.

## 📋 Stack Technique

### Backend
- **FastAPI** - Framework web asynchrone Python
- **LangChain 0.3.27** - Orchestration LLM et RAG
- **PostgreSQL (pgvector)** - Base de données relationnelle avec support vectoriel
- **Qdrant** - Base de données vectorielle pour embeddings
- **SQLAlchemy + Alembic** - ORM et migrations
- **Python 3.10** (Docker) / **Python 3.12** (CI/CD)

### LLM & Embeddings
- **Ollama** - LLM local (llama3.1, mistral, gemma2)
- **HuggingFace sentence-transformers** - Embeddings locaux (paraphrase-multilingual-mpnet-base-v2, 768 dimensions)
- **Support multi-providers** - Groq, OpenAI, Cohere

### Frontend
- **React** - Interface utilisateur
- **Nginx** - Reverse proxy

### Monitoring
- **Prometheus** - Métriques système et applicatives
- **Grafana** - Dashboards de visualisation
- **Node Exporter** - Métriques système
- **PostgreSQL Exporter** - Métriques base de données

## 🐳 Services Docker

Le projet utilise Docker Compose avec 10 services orchestrés:

| Service | Port | Description |
|---------|------|-------------|
| **nginx** | 80 | Reverse proxy principal |
| **frontend** | 3001 | Interface React |
| **fastapi** | 8000 | API Backend |
| **grafana** | 3000 | Dashboards monitoring |
| **ollama** | 11434 | LLM local (llama3.1, mistral, gemma2) |
| **pgvector** | 5432 | PostgreSQL avec extension vectorielle |
| **qdrant** | 6333, 6334 | Base de données vectorielle |
| **prometheus** | 9090 | Collecte métriques |
| **node-exporter** | 9100 | Métriques système |
| **postgres-exporter** | 9187 | Métriques PostgreSQL |

## 🚀 Installation

### Prérequis
- Docker & Docker Compose
- Git

### Démarrage rapide

```bash
# Cloner le repository
git clone <repo-url>
cd fil_rouge

# Configurer les variables d'environnement
cd docker/env
cp .env.app.example .env.app
cp .env.postgres.example .env.postgres
# Éditer les fichiers .env avec vos clés API

# Lancer tous les services
cd ..
docker-compose up -d

# Vérifier les logs
docker logs fastapi -f
```

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

### Accès aux services

- **Application web**: http://localhost (via Nginx)
- **API FastAPI**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Frontend direct**: http://localhost:3001
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090
- **Qdrant**: http://localhost:6333/dashboard

## 🧪 Tests

### Lancer les tests (environnement Docker)

```bash
# Tous les tests (286 tests complets)
docker exec fastapi bash -c "cd ../tests && pytest -v --cov=../src --cov-report=term-missing"

# Tests unitaires uniquement
docker exec fastapi bash -c "cd ../tests && pytest unit/ -v"

# Tests d'intégration uniquement
docker exec fastapi bash -c "cd ../tests && pytest integration/ -v"

# Tests avec rapport XML
docker exec fastapi bash -c "cd ../tests && pytest -v --cov=../src --cov-report=xml"
```

### Structure des tests

```
tests/
├── unit/
│   ├── controllers/    # Tests des contrôleurs (document, prompt, etc.)
│   ├── helpers/        # Tests des helpers (auth, config, file, etc.)
│   ├── models/         # Tests des modèles PostgreSQL
│   └── services/       # Tests des services (RAG, embeddings, document, prompt, vectorstore)
├── integration/        # Tests d'intégration end-to-end
├── conftest.py         # Configuration pytest et fixtures globales
├── pytest.ini          # Configuration pytest
└── README.md           # Documentation détaillée des tests

**286 tests au total** | **Couverture: 32%** | **11 modules à 100%**
```

Voir `tests/README.md` pour la documentation complète des tests.

## 🔄 CI/CD

Ce projet utilise GitHub Actions pour l'intégration continue.

### Workflow Tests Unitaires

Le workflow `.github/workflows/unit-tests.yml` s'exécute automatiquement:
- À chaque push sur les branches `main` et `develop`
- À chaque pull request vers ces branches

**Ce qu'il fait:**
1. Configure Python 3.12
2. Installe les dépendances lightweight depuis `src/requirements-test.txt`
3. Crée un fichier `.env` de test avec des valeurs mock
4. Exécute les tests unitaires compatibles CI/CD (131 tests)
5. Génère un rapport de couverture XML
6. Ajoute un commentaire sur les PR avec le pourcentage de couverture

### Tests CI/CD vs Tests Locaux

**CI/CD (GitHub Actions)** - 131 tests légers (~11s)
- Tests des services: `document_service`, `prompt_service`
- Tests des contrôleurs: `document_controller`, `prompt_controller`, etc.
- Tests des helpers: `auth`, `config`, etc.
- Exclusions: PostgreSQL, ML packages (torch, tensorflow), tests RAG/embeddings/vectorstore

**Local (Docker)** - 286 tests complets (~6min)
- Tous les tests CI/CD
- Tests d'intégration avec PostgreSQL
- Tests RAG, embeddings, vectorstore
- Tests modèles de base de données
- Tests avec ML packages complets

**Pourquoi cette séparation?**
- GitHub Actions a une limite de 14GB d'espace disque
- Les packages ML (torch ~3GB, tensorflow ~500MB) dépassent cette limite
- Les tests lourds s'exécutent uniquement en local avec Docker

### Voir les résultats

- Résultats des tests: onglet **Actions** du repository GitHub
- Status des PR: affichage automatique du statut vert/rouge
- Couverture: commentaire automatique sur chaque PR