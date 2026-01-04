# RAG FINANCE - Système RAG avec LangChain

Plateforme de Retrieval-Augmented Generation (RAG) permettant l'analyse de documents PDF, la génération de réponses intelligentes via LLM, et la prédiction des taux de change EUR/MAD et USD/MAD avec un modèle LSTM.

## 📋 Stack Technique

### Backend
- **FastAPI** - Framework web asynchrone Python
- **LangChain 0.3.27** - Orchestration LLM et RAG
- **PostgreSQL (pgvector)** - Base de données relationnelle avec support vectoriel
- **Qdrant** - Base de données vectorielle pour embeddings
- **SQLAlchemy + Alembic** - ORM et migrations
- **Python 3.10** - Version unifiée (Docker + CI/CD)

### LLM & Embeddings
- **Ollama** - LLM local (gemma2:2b)
- **Groq API** - LLM cloud rapide et gratuit (llama-3.3-70b-versatile par défaut)
- **HuggingFace sentence-transformers** - Embeddings locaux (paraphrase-multilingual-mpnet-base-v2, 768 dimensions)
- **Support multi-providers** - Groq (défaut), OpenAI, Cohere, Ollama

### Frontend
- **React** - Interface utilisateur
- **Nginx** - Reverse proxy

### Monitoring
- **Prometheus** - Métriques système et applicatives
- **Grafana** - Dashboards de visualisation
- **Node Exporter** - Métriques système
- **PostgreSQL Exporter** - Métriques base de données

### Machine Learning
- **TensorFlow/Keras** - Modèle LSTM pour prédiction des taux de change
- **Scikit-learn** - Prétraitement et métriques (MAE, RMSE, R²)
- **Prédiction EUR/MAD et USD/MAD** - 30 jours historiques → 7 jours futurs
- **API Bank Al-Maghrib** - Source de données officielles

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

## 📁 Structure du Projet

```
fil_rouge/
├── .github/
│   └── workflows/
│       └── unit-tests.yml              # CI/CD GitHub Actions
│
├── docker/
│   ├── env/
│   │   ├── .env.app.example            # Config application (LLM, embeddings, API keys)
│   │   └── .env.postgres.example       # Config PostgreSQL
│   ├── frontend/
│   │   ├── Dockerfile                  # Image React + Nginx
│   │   └── nginx.conf                  # Config Nginx frontend
│   ├── minirag/
│   │   ├── Dockerfile                  # Image FastAPI + Python 3.10
│   │   ├── alembic.ini                 # Config migrations Alembic
│   │   └── entrypoint.sh               # Script démarrage
│   ├── nginx/
│   │   └── default.conf                # Config Nginx reverse proxy
│   ├── prometheus/
│   │   └── prometheus.yml              # Config collecte métriques
│   └── docker-compose.yml              # Orchestration 10 services
│
├── frontend/
│   ├── public/                         # Assets statiques
│   ├── src/
│   │   ├── components/                 # Composants React
│   │   ├── pages/                      # Pages principales
│   │   ├── services/
│   │   │   └── api.js                  # Client API FastAPI
│   │   └── App.jsx                     # Application React
│   ├── package.json
│   └── Dockerfile
│
├── src/
│   ├── controllers/
│   │   ├── BaseController.py           # Contrôleur de base
│   │   ├── DataController.py           # Upload et validation fichiers
│   │   ├── NLPController.py            # Opérations RAG
│   │   ├── ProcessController.py        # Traitement documents
│   │   └── ProjectController.py        # Gestion projets
│   │
│   ├── services/
│   │   ├── document_service.py         # Chargement et découpage docs (LangChain)
│   │   ├── embeddings_service.py       # Génération embeddings (768D)
│   │   ├── vectorstore_service.py      # Gestion Qdrant/pgvector
│   │   ├── rag_service.py              # Pipeline RAG complet (LCEL)
│   │   └── prompt_service.py           # Prompts multilingues (FR/EN/AR)
│   │
│   ├── exchange_rates/
│   │   ├── jobs/
│   │   │   ├── fetch_rates_job.py      # Job quotidien taux de change
│   │   │   ├── initial_backfill.py     # Backfill historique
│   │   │   └── scheduler.py            # APScheduler
│   │   ├── ml/
│   │   │   └── lstm_model.py           # Modèle LSTM (TensorFlow/Keras)
│   │   ├── models/
│   │   │   └── ExchangeRateModel.py    # ORM taux de change
│   │   ├── routes/
│   │   │   └── exchange_routes.py      # API endpoints taux/prédictions
│   │   ├── services/
│   │   │   ├── bam_api_client.py       # Client API Bank Al-Maghrib
│   │   │   └── prediction_service.py   # Service prédictions LSTM
│   │   └── metrics.py                  # Métriques Prometheus
│   │
│   ├── models/
│   │   ├── db_schemes/
│   │   │   └── minirag/
│   │   │       ├── alembic/            # Migrations base de données
│   │   │       └── schemes/            # Schémas SQLAlchemy
│   │   │           ├── user.py
│   │   │           ├── project.py
│   │   │           ├── asset.py
│   │   │           ├── datachunk.py
│   │   │           ├── conversation.py
│   │   │           └── exchange_rate.py
│   │   ├── UserModel.py
│   │   ├── ProjectModel.py
│   │   ├── AssetModel.py
│   │   ├── ChunkModel.py
│   │   └── ConversationModel.py
│   │
│   ├── routes/
│   │   ├── auth.py                     # Authentification JWT
│   │   ├── data.py                     # Upload documents
│   │   ├── nlp.py                      # RAG endpoints
│   │   ├── conversation.py             # Historique conversations
│   │   └── admin.py                    # Administration
│   │
│   ├── helpers/
│   │   ├── auth.py                     # JWT, bcrypt
│   │   └── config.py                   # Configuration app
│   │
│   ├── main.py                         # Application FastAPI
│   ├── requirements.txt                # Dépendances complètes (286 tests)
│   ├── requirements-test.txt           # Dépendances CI/CD (113 tests)
│   └── .env.example
│
├── tests/
│   ├── unit/
│   │   ├── controllers/                # 12 tests
│   │   ├── services/                   # 71 tests
│   │   ├── helpers/                    # 15 tests
│   │   └── models/                     # 57 tests
│   ├── integration/                    # 25 tests
│   ├── ml/                             # 27 tests LSTM
│   ├── conftest.py                     # Fixtures pytest
│   └── pytest.ini
│
├── .gitignore
└── README.md
```

### Points clés de l'architecture

**Backend (src/)** :
- **Controllers** : Orchestration entre routes et services
- **Services** : Logique métier (RAG, embeddings, LSTM)
- **Models** : ORM SQLAlchemy (8 tables PostgreSQL)
- **Routes** : 7 fichiers de routes (auth, data, nlp, conversation, admin, base, exchange_rates)
- **exchange_rates/** : Module autonome pour taux de change

**Frontend (frontend/)** :
- Application React 18
- Client API centralisé (`api.js`)
- Servi par Nginx

**Infrastructure (docker/)** :
- 10 services orchestrés avec Docker Compose
- Configurations séparées par environnement
- Monitoring complet (Prometheus + Grafana)

## 🚀 Installation

### Prérequis
- Docker & Docker Compose
- Git

### Démarrage rapide

```bash
# Cloner le repository
git clone <https://github.com/sara-git-hub/Rag_finance.git>
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

### Développement local (sans Docker)

Si vous préférez développer en local sans Docker :

```bash
# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r src/requirements.txt

# Configurer les variables d'environnement
cp src/.env.example src/.env
# Éditer src/.env avec vos clés API

# Lancer le backend (nécessite PostgreSQL et Qdrant installés localement)
cd src
uvicorn main:app --reload
```

**Frontend (dans un autre terminal)** :

```bash
# Modifier la configuration pour pointer vers localhost
# Éditer frontend/vite.config.js ligne 11 : target: 'http://localhost:8000'

# Installer et lancer
cd frontend
npm install
npm run dev
```

**Accès** : http://localhost:5173 (frontend) → proxie vers http://localhost:8000 (backend API)

## ⚙️ Configuration

### Variables d'environnement essentielles

Éditer `docker/env/.env.app` avec vos clés API :

```bash
# LLM Provider (choix: openai, cohere, groq, ollama)
GENERATION_BACKEND=groq
GROQ_API_KEY=votre_clé_groq         # Gratuit sur https://console.groq.com/keys
GENERATION_MODEL_ID=llama-3.3-70b-versatile

# Embeddings (local par défaut, gratuit)
EMBEDDING_BACKEND=local
EMBEDDING_MODEL_ID=multilingual      # 768 dimensions

# Vector Database
VECTOR_DB_BACKEND=QDRANT
QDRANT_URL=http://qdrant:6333       # URL Docker

# API Bank Al-Maghrib (taux de change)
CLE_API_CHANGES=votre_clé_bam
CLE_API_CHANGES_2=clé_secours        # Optionnel

# Backfill automatique au démarrage
ENABLE_INITIAL_BACKFILL=true
BACKFILL_DAYS=175                    # Historique initial (défaut: 175 jours)

# JWT Authentication
SECRET_KEY=votre_clé_secrète_jwt
```

**Providers LLM supportés** :
- **Groq** (recommandé) : Gratuit, rapide, llama-3.3-70b-versatile
- **OpenAI** : gpt-3.5-turbo, gpt-4o-mini (clé API requise)
- **Cohere** : command-r, command-r-plus (clé API requise)
- **Ollama** : gemma2 (local, gratuit, Docker requis)

### Accès aux services

- **Application web**: http://localhost (via Nginx)
- **API FastAPI**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs
- **Frontend direct**: http://localhost:3001
- **Grafana**: http://localhost:3000
  - **Dashboard Exchange Rates**: http://localhost:3000/d/exchange-rates-monitoring
- **Prometheus**: http://localhost:9090
- **Qdrant**: http://localhost:6333/dashboard

## 🔌 Endpoints API

### Authentification (`/api/v1/auth`)
- `POST /register` - Créer un compte utilisateur
- `POST /login` - Connexion (retourne token JWT)
- `GET /me` - Informations utilisateur connecté

### RAG & NLP (`/api/v1/nlp`)
- `POST /index/push/{project_id}` - Indexer documents dans Qdrant (admin)
- `GET /index/info/{project_id}` - Infos collection vectorielle (admin)
- `POST /index/search/{project_id}` - Recherche sémantique
- `POST /index/answer/{project_id}` - Génération RAG avec contexte

### Taux de Change (`/api/v1/exchange-rates`)
**Routes utilisateurs** :
- `GET /latest` - Derniers taux EUR/MAD et USD/MAD
- `GET /predictions?currency_pair=EUR/MAD&days_history=30&days_ahead=7` - Prédictions LSTM
- `GET /history?currency_pair=USD/MAD&days=365` - Historique

**Routes admin** :
- `POST /admin/train-model?currency_pair=EUR/MAD` - Entraîner modèle LSTM
- `POST /admin/generate-predictions` - Générer prédictions
- `POST /admin/fetch-rates-now` - Récupérer taux manuellement
- `GET /admin/scheduler/status` - Statut du scheduler

### Conversations (`/api/v1/conversations`)
- `POST /` - Créer nouvelle conversation
- `GET /` - Lister conversations utilisateur
- `GET /{conversation_id}` - Historique conversation
- `DELETE /{conversation_id}` - Supprimer conversation

### Documents (`/api/v1/data`)
- `POST /upload/{project_id}` - Upload fichier PDF/TXT
- `GET /files/{project_id}` - Lister fichiers projet

## 🎯 Fonctionnalités Système

### Scheduler Automatique
- **Job quotidien** : Récupération taux EUR/MAD et USD/MAD à **9h00** (API Bank Al-Maghrib)
- **Backfill initial** : Au démarrage, récupère automatiquement l'historique (configurable via `BACKFILL_DAYS`)
- **Gestion d'erreurs** : Clé API de secours (`CLE_API_CHANGES_2`) en cas d'échec

### Authentification & Autorisation
- **JWT** : Tokens d'authentification avec expiration
- **Rôles** : `user` (lecture) et `admin` (écriture, entraînement LSTM)
- **Protection** : Endpoints sensibles réservés aux admins

### Système de Conversations
- **Historique contextuel** : Le LLM se souvient des échanges précédents
- **Persistance** : Conversations sauvegardées en PostgreSQL
- **Multi-projets** : Conversations liées aux projets RAG

### Monitoring en Temps Réel
- **Métriques Prometheus** : Requêtes API, latence, erreurs, taux de change
- **Dashboard Grafana** : Visualisation taux EUR/MAD, USD/MAD, prédictions LSTM
- **Alertes** : Configurables via Grafana (échec récupération taux, modèle non entraîné)

## 🧪 Tests

### Lancer les tests en local

```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r src/requirements.txt

# Tous les tests (286 tests)
cd tests
pytest -v --cov=../src --cov-report=term-missing

# Tests unitaires
pytest unit/ -v

# Tests d'intégration
pytest integration/ -v
```

**286 tests au total** | **Couverture: 32%**

Voir `tests/README.md` pour la documentation complète.

## 🔄 CI/CD

Ce projet utilise GitHub Actions pour l'intégration continue.

### Workflow Tests Unitaires

Le workflow `.github/workflows/unit-tests.yml` s'exécute automatiquement:
- À chaque push sur les branches `main` et `develop`
- À chaque pull request vers ces branches

**Ce qu'il fait:**
1. Configure Python 3.10 (identique à la production Docker)
2. Installe les dépendances lightweight depuis `src/requirements-test.txt`
3. Crée un fichier `.env` de test avec des valeurs mock
4. Exécute les tests unitaires compatibles CI/CD (113 tests)
5. Génère un rapport de couverture XML
6. Ajoute un commentaire sur les PR avec le pourcentage de couverture

### Tests CI/CD vs Tests Locaux

**CI/CD (GitHub Actions)** - 113 tests légers (~11s)
- Tests des services: `document_service`, `prompt_service`
- Tests des contrôleurs (partiels): `base_controller`, `data_controller`, `project_controller`
- Tests des helpers: `auth`, `config`
- **Exclusions**:
  - PostgreSQL, ML packages (torch, tensorflow)
  - Tests RAG/embeddings/vectorstore
  - 18 tests désélectionnés (incompatibles avec CI/CD ou nécessitant dépendances lourdes)

**Local** - 286 tests complets (~6min)
- Tous les 113 tests CI/CD
- 18 tests désélectionnés du CI/CD (nécessitant PostgreSQL, VectorStore ou ML)
- Tests d'intégration avec PostgreSQL (25 tests)
- Tests ML (LSTM, 27 tests)
- Tests modèles de base de données (57 tests)
- Tests RAG, embeddings, vectorstore (46 tests)

**Pourquoi cette séparation?**
- GitHub Actions a une limite de 14GB d'espace disque
- Les packages ML (torch ~3GB, tensorflow ~500MB) dépassent cette limite
- Certains tests nécessitent PostgreSQL/Qdrant/VectorStore non disponibles en CI/CD
- Les tests lourds s'exécutent uniquement en local

**Note sur les versions Python:**
- **Production (Docker)**: Python 3.10
- **CI/CD (GitHub Actions)**: Python 3.10
- **Développement local (venv)**: Python 3.12 recommandé mais non obligatoire
- Les 286 tests passent tous avec Python 3.12 en local
- 18 tests sont désélectionnés du CI/CD (nécessitent dépendances lourdes ou bases de données)

### Voir les résultats

- Résultats des tests: onglet **Actions** du repository GitHub
- Status des PR: affichage automatique du statut vert/rouge
- Couverture: commentaire automatique sur chaque PR