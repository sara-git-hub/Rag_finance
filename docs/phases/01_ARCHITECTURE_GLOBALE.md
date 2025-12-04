# Phase 1 : Architecture Globale

> **Statut** : ✅ Complétée
> **Durée** : 2 heures
> **Date** : Décembre 2025

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Cartographie des services Docker](#cartographie-des-services-docker)
3. [Architecture des flux](#architecture-des-flux)
4. [Points d'entrée de l'application](#points-dentrée-de-lapplication)
5. [Schéma d'architecture global](#schéma-darchitecture-global)
6. [Dépendances entre services](#dépendances-entre-services)
7. [Sécurité & Configuration](#sécurité--configuration)
8. [Performance & Ressources](#performance--ressources)

---

## 🎯 Vue d'ensemble

Le projet **fil_rouge** est une application de **Retrieval-Augmented Generation (RAG)** spécialisée dans l'analyse de documents financiers avec des capacités de prédiction de taux de change intégrées.

### Type d'architecture

**Microservices** orchestrés par Docker Compose avec **11 conteneurs** interconnectés via un réseau bridge.

### Technologies clés

- **Backend** : FastAPI (Python 3.10)
- **Frontend** : React 18 + Vite
- **Database** : PostgreSQL 17 + PGVector
- **Vector DB** : Qdrant v1.13.6
- **LLM** : Ollama (local, gratuit)
- **Monitoring** : Prometheus + Grafana

---

## 🏗️ Cartographie des services Docker

### Liste complète des 11 conteneurs

| # | Service | Image | Port(s) | Rôle | Dépendances | Ressources |
|---|---------|-------|---------|------|-------------|------------|
| 1 | **ollama** | `ollama/ollama:latest` | 11434 | LLM local (Mistral, Llama) | Aucune | 8GB max, 4GB réservé |
| 2 | **fastapi** | Custom (Python 3.10 + uv) | 8000 | API Backend REST | pgvector, ollama | 4GB max, 2GB réservé |
| 3 | **frontend** | Custom (Node 18 + Nginx) | 3001 | Interface React (SPA) | fastapi | - |
| 4 | **nginx** | `nginx:stable-alpine3.20-perl` | **80** | Reverse Proxy (entrée unique) | fastapi, frontend | - |
| 5 | **pgvector** | `pgvector/pgvector:0.8.1-pg17` | 5432 | PostgreSQL + extension vectors | Aucune | - |
| 6 | **qdrant** | `qdrant/qdrant:v1.13.6` | 6333, 6334 | Vector Database (similarité) | Aucune | - |
| 7 | **prometheus** | `prom/prometheus:v3.3.0` | 9090 | Collecte métriques (15s) | Aucune | - |
| 8 | **grafana** | `grafana/grafana:11.6.0-ubuntu` | 3000 | Dashboards monitoring | prometheus | - |
| 9 | **node-exporter** | `prom/node-exporter:v1.9.1` | 9100 | Métriques système (CPU, RAM) | Aucune | - |
| 10 | **postgres-exporter** | `postgres-exporter:v0.17.1` | 9187 | Métriques PostgreSQL | pgvector | - |

### Réseau Docker

- **Nom** : `backend`
- **Type** : Bridge network
- **Isolation** : Tous les services communiquent via le réseau interne Docker
- **Exposition** : Seul **Nginx (port 80)** est exposé publiquement en production

### Volumes persistants (7 volumes)

| Volume | Service(s) | Taille estimée | Contenu | Criticité |
|--------|-----------|----------------|---------|-----------|
| `ollama_models` | ollama | ~5-10GB | Modèles LLM (Mistral, Llama, etc.) | Moyenne (re-téléchargeables) |
| `fastapi_data` | fastapi | ~100MB-1GB | Assets uploadés (PDFs) | **HAUTE** (données user) |
| `huggingface_cache` | fastapi | ~420MB | Modèle embeddings multilingual | Faible (re-téléchargeable) |
| `pgvector` | pgvector | ~500MB-5GB | PostgreSQL + vecteurs | **CRITIQUE** (données principales) |
| `qdrant_data` | qdrant | ~200MB-2GB | Collections de vecteurs | Haute (peut être ré-indexé) |
| `prometheus_data` | prometheus | ~100MB | Métriques historiques | Faible (monitoring) |
| `grafana_data` | grafana | ~50MB | Dashboards et config | Faible (re-configurable) |

**Total volumes** : ~6-20GB (selon usage)

**⚠️ Volumes à sauvegarder** : `pgvector`, `fastapi_data`, `qdrant_data`

---

## 🔀 Architecture des flux

### Flux 1 : Requête HTTP utilisateur

```
┌─────────────────────────────────────────────────────────────┐
│                      UTILISATEUR                             │
│                   (Navigateur Web)                           │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP (port 80)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 NGINX (Reverse Proxy)                        │
│                      nginx:80                                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Règles de routage:                                  │   │
│  │  - /api/*          → fastapi:8000                    │   │
│  │  - /TrhBVe_*       → fastapi:8000 (métriques)        │   │
│  │  - /*              → frontend:80                     │   │
│  │                                                       │   │
│  │  Timeouts: 1000s (RAG peut être long)               │   │
│  │  Max body: 100MB (upload PDFs)                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────┬─────────────────────────┬─────────────────────┘
              │                         │
              ▼                         ▼
┌─────────────────────────┐   ┌───────────────────────────────┐
│   FRONTEND (React)      │   │   FASTAPI (Backend)           │
│   frontend:80           │   │   fastapi:8000                │
│   - Nginx static files  │   │   - 7 routers                 │
│   - Build Vite          │   │   - LangChain services        │
│   - 18 routes           │   │   - 40+ endpoints             │
└─────────────────────────┘   └──────────┬────────────────────┘
                                         │
                    ┌────────────────────┼──────────────────┐
                    │                    │                  │
                    ▼                    ▼                  ▼
        ┌───────────────────┐  ┌─────────────────┐  ┌─────────────┐
        │   PGVECTOR        │  │   QDRANT        │  │   OLLAMA    │
        │   pgvector:5432   │  │   qdrant:6333   │  │  ollama:11434│
        │   - PostgreSQL 17 │  │   - Vecteurs    │  │  - LLM      │
        │   - Extension 0.8.1│  │   - Similarité  │  │  - Mistral  │
        │   - 7 tables      │  │   - HNSW index  │  │  - Llama 3.1│
        └───────────────────┘  └─────────────────┘  └─────────────┘
```

### Flux 2 : Monitoring (Prometheus → Grafana)

```
┌──────────────────────────────────────────────────────────┐
│               PROMETHEUS (9090)                           │
│       Collecte métriques toutes les 15s                   │
│   ┌──────────────────────────────────────────────────┐   │
│   │  Scrape configs:                                 │   │
│   │  - fastapi:8000/TrhBVe_* (métriques app)        │   │
│   │  - node-exporter:9100 (métriques système)       │   │
│   │  - postgres-exporter:9187 (métriques DB)        │   │
│   │  - qdrant:6333/metrics (métriques Qdrant)       │   │
│   └──────────────────────────────────────────────────┘   │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│                  GRAFANA (3000)                           │
│            Dashboards & Visualisations                    │
│  - FastAPI Observability                                 │
│  - Node Exporter Full                                    │
│  - PostgreSQL Exporter                                   │
│  - Qdrant Metrics                                        │
└──────────────────────────────────────────────────────────┘
```

### Flux 3 : Données RAG

```
USER → Upload PDF
  ↓
FastAPI (/api/v1/data/upload)
  ↓
AssetModel → PostgreSQL (assets table)
  ↓
FastAPI (/api/v1/data/process)
  ↓
ProcessController (PyMuPDF + LangChain)
  ├─ Extract text
  ├─ Chunk (RecursiveTextSplitter)
  └─ ChunkModel → PostgreSQL (datachunks table)
  ↓
FastAPI (/api/v1/nlp/index/push)
  ↓
NLPController
  ├─ Get chunks (ChunkModel)
  ├─ Generate embeddings (EmbeddingsService)
  └─ Index vectors → Qdrant/PGVector
  ↓
USER → Query (Q&A)
  ↓
FastAPI (/api/v1/nlp/index/answer)
  ↓
RAGService (LangChain LCEL)
  ├─ Vector search (VectorStoreService)
  ├─ Format context (PromptService)
  ├─ Generate answer (Ollama LLM)
  └─ Save conversation → PostgreSQL
  ↓
USER ← Answer + Sources
```

---

## 🚪 Points d'entrée de l'application

### Backend : `src/main.py`

**Rôle** : Point d'entrée FastAPI avec lifecycle management (startup/shutdown)

**Composants initialisés au démarrage** :

1. **Database Connection**
   ```python
   postgres_conn = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
   app.db_engine = create_async_engine(postgres_conn)
   app.db_client = sessionmaker(app.db_engine, class_=AsyncSession)
   ```

2. **LangChain Services**
   - `EmbeddingsService` : Embeddings multi-provider (local/OpenAI/Cohere)
   - `PromptService` : Templates multi-langue (FR/EN/AR)

3. **Configuration LLM**
   - Backend : Ollama/OpenAI/Cohere/Groq (via .env)
   - API keys selon provider
   - Base URL Ollama : `http://ollama:11434`

4. **Vector DB Configuration**
   - Backend : Qdrant (URL Docker) ou PGVector (sync connection string)
   - Qdrant URL : `http://qdrant:6333`

5. **Exchange Rates Scheduler**
   - Job quotidien à 9h00 (fetch BAM API)
   - Backfill initial : 90 jours
   - Fetch immédiat si taux du jour manquants

6. **Prometheus Middleware**
   ```python
   app.add_middleware(PrometheusMiddleware, app_name="rag_finance")
   ```

**Routers inclus (7)** :
```python
app.include_router(base.base_router)           # Health checks
app.include_router(auth.auth_router)           # /api/v1/auth/*
app.include_router(data.data_router)           # /api/v1/data/*
app.include_router(nlp.nlp_router)             # /api/v1/nlp/*
app.include_router(conversation.conversation_router)  # /api/v1/conversations/*
app.include_router(admin.admin_router)         # /api/v1/admin/*
app.include_router(exchange_routes.exchange_router)  # /api/v1/exchange-rates/*
```

**Métriques endpoint** (obfusqué pour sécurité) :
```python
app.add_route("/TrhBVe_m5gg2002_E5VVqS", handle_metrics)
```

**Shutdown** :
- Arrêt du scheduler Exchange Rates
- Fermeture des connexions DB

---

### Frontend : `frontend/src/main.jsx`

**Rôle** : Point d'entrée React avec StrictMode

```javascript
ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
```

**Composant racine** : `<App />` (défini dans `App.jsx`)

---

### Application React : `frontend/src/App.jsx`

**Architecture** :
- **Router** : React Router v6 (BrowserRouter)
- **Context** : AuthProvider (gestion JWT globale)
- **Protection** : ProtectedRoute HOC (auth + rôle admin)

**Routes définies (18 routes)** :

#### Routes publiques (2)
| Path | Component | Rôle |
|------|-----------|------|
| `/` | Redirect → `/login` | Redirection racine |
| `/login` | Login | Authentification |
| `/register` | Register | Inscription |

#### Routes utilisateur (4) - Auth requis
| Path | Component | Rôle |
|------|-----------|------|
| `/dashboard` | Dashboard | Page d'accueil user |
| `/search` | Search | Recherche vectorielle sémantique |
| `/qa` | QA | RAG conversationnel avec historique |
| `/exchange-rates` | ExchangeRates | Graphiques taux MAD/EUR, MAD/USD |

#### Routes admin (12) - Admin uniquement
| Path | Component | Rôle |
|------|-----------|------|
| `/upload` | Upload | Upload PDFs par projet |
| `/process` | Process | Processing documents (extraction + chunking) |
| `/index` | IndexPage | Indexation vectorielle dans Qdrant/PGVector |
| `/users` | Users | Gestion utilisateurs |
| `/admin/projects` | AdminProjects | CRUD projets |
| `/admin/assets` | AdminAssets | CRUD assets (fichiers) |
| `/admin/chunks` | AdminChunks | CRUD chunks (morceaux de texte) |
| `/admin/conversations` | AdminConversations | CRUD conversations |
| `/admin/messages` | AdminMessages | CRUD messages (Q&A) |
| `/admin/vectors` | AdminVectors | Gestion collections vectorielles |
| `/admin/exchange-rates` | AdminExchangeRates | Admin taux de change (train ML, etc.) |

**Pattern de protection** :
```jsx
// Admin uniquement
<ProtectedRoute requireAdmin>
  <Upload />
</ProtectedRoute>

// User + Admin
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```

---

## 📊 Schéma d'architecture global

### Architecture en couches (N-Tier)

```
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE PRÉSENTATION                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  React 18 + Vite (SPA)                               │   │
│  │  - 18 routes (2 publiques, 4 user, 12 admin)        │   │
│  │  - Context (AuthContext)                             │   │
│  │  - Hooks (useConversation)                           │   │
│  │  - Services (api.js avec Axios interceptors)        │   │
│  │  - Tailwind CSS                                      │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/REST (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE REVERSE PROXY                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Nginx (Routing, Load Balancing, Timeouts)          │   │
│  │  - /api/* → fastapi:8000                            │   │
│  │  - /* → frontend:80                                  │   │
│  │  - Timeout: 1000s                                    │   │
│  │  - Max body: 100MB                                   │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    COUCHE APPLICATIVE                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI (Python 3.10)                               │   │
│  │  ├─ Routes (7 routers, 40+ endpoints)                │   │
│  │  │  ├─ base (health)                                 │   │
│  │  │  ├─ auth (JWT)                                    │   │
│  │  │  ├─ data (upload, process)                        │   │
│  │  │  ├─ nlp (RAG: index, search, answer)             │   │
│  │  │  ├─ conversation (CRUD)                           │   │
│  │  │  ├─ admin (CRUD multi-tables)                     │   │
│  │  │  └─ exchange_rates (taux + ML)                    │   │
│  │  │                                                    │   │
│  │  ├─ Controllers (4)                                   │   │
│  │  │  ├─ NLPController (RAG logic)                     │   │
│  │  │  ├─ DataController (validation)                   │   │
│  │  │  ├─ ProcessController (PDF + chunking)           │   │
│  │  │  └─ ProjectController (paths)                     │   │
│  │  │                                                    │   │
│  │  ├─ Services (5 LangChain)                           │   │
│  │  │  ├─ RAGService (LCEL pipeline)                    │   │
│  │  │  ├─ EmbeddingsService (multi-provider)           │   │
│  │  │  ├─ VectorStoreService (Qdrant/PGVector)         │   │
│  │  │  ├─ PromptService (templates FR/EN/AR)           │   │
│  │  │  └─ DocumentService (PDF loader)                  │   │
│  │  │                                                    │   │
│  │  ├─ Models (7 SQLAlchemy)                            │   │
│  │  │  ├─ UserModel, ProjectModel, AssetModel          │   │
│  │  │  ├─ ChunkModel, ConversationModel                │   │
│  │  │  └─ ExchangeRateModel                             │   │
│  │  │                                                    │   │
│  │  └─ Exchange Rates Module                            │   │
│  │     ├─ Jobs (APScheduler: fetch daily 9h)           │   │
│  │     ├─ ML (LSTM TensorFlow)                         │   │
│  │     ├─ Services (BAM API client, predictions)       │   │
│  │     └─ Metrics (Prometheus)                          │   │
│  └──────────────────────────────────────────────────────┘   │
└──────┬─────────────────────┬─────────────────┬──────────────┘
       │                     │                 │
       ▼                     ▼                 ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐
│  COUCHE DATA    │  │ VECTOR LAYER │  │   AI LAYER       │
│  ┌───────────┐  │  │ ┌──────────┐ │  │  ┌────────────┐  │
│  │PostgreSQL │  │  │ │ Qdrant   │ │  │  │  Ollama    │  │
│  │17+PGVector│  │  │ │ v1.13.6  │ │  │  │  (local)   │  │
│  │0.8.1      │  │  │ │          │ │  │  │            │  │
│  │           │  │  │ │- 768D    │ │  │  │- Mistral   │  │
│  │Tables:    │  │  │ │- Cosine  │ │  │  │- Llama 3.1 │  │
│  │- users    │  │  │ │- HNSW    │ │  │  │- Gemma     │  │
│  │- projects │  │  │ │          │ │  │  │            │  │
│  │- assets   │  │  │ │Collections│ │  │  │- FREE     │  │
│  │- chunks   │  │  │ │per project│ │  │  │- No API   │  │
│  │- convs    │  │  │ │          │ │  │  │  key       │  │
│  │- messages │  │  │ └──────────┘ │  │  └────────────┘  │
│  │- exch_rate│  │  │              │  │                  │
│  └───────────┘  │  │ Alternative: │  │  Alternatives:   │
│                 │  │ PGVector     │  │  - OpenAI        │
│                 │  │ (same DB)    │  │  - Cohere        │
│                 │  │              │  │  - Groq          │
│  └─────────────┘  └──────────────┘  └──────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                  COUCHE OBSERVABILITÉ                        │
│  ┌──────────────────┐  ┌───────────────────────────────┐    │
│  │   Prometheus     │→ │        Grafana                │    │
│  │   (Métriques)    │  │      (Dashboards)             │    │
│  │                  │  │                               │    │
│  │ - FastAPI (HTTP) │  │ - FastAPI Observability       │    │
│  │ - Node (Système) │  │ - Node Exporter Full          │    │
│  │ - Postgres (DB)  │  │ - PostgreSQL Database         │    │
│  │ - Qdrant (Vec)   │  │ - Qdrant Metrics              │    │
│  └──────────────────┘  └───────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Dépendances entre services

### Graphe de dépendances

```
ollama ──────────────┐
                     │
pgvector ────────────┼──→ fastapi ───→ frontend ───┐
  (healthcheck)      │    (depends)     (depends)   │
                     │                              │
qdrant ──────────────┘                              ├──→ nginx ──→ USER
                                                    │    (port 80)
                                                    │
prometheus ──→ grafana ─────────────────────────────┘
  (scrape)      (depends)

node-exporter ──┐
                ├──→ prometheus
postgres-exporter─┘    (scrape)
```

### Ordre de démarrage optimal

Docker Compose gère automatiquement l'ordre grâce aux `depends_on`, mais voici la séquence logique :

**Étape 1** : Services indépendants
1. `pgvector` (avec healthcheck `pg_isready`)
2. `ollama`
3. `qdrant`
4. `prometheus`
5. `node-exporter`

**Étape 2** : Services dépendants de la base
6. `postgres-exporter` (après `pgvector`)

**Étape 3** : Application backend
7. `fastapi` (après `pgvector` healthy et `ollama` started)

**Étape 4** : Application frontend
8. `frontend` (après `fastapi`)

**Étape 5** : Monitoring
9. `grafana` (après `prometheus`)

**Étape 6** : Point d'entrée
10. `nginx` (après `fastapi` et `frontend`)

### Conditions de santé (healthchecks)

**PGVector** :
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
  start_period: 10s
```

Les autres services utilisent `condition: service_started` (attendent juste le démarrage).

---

## 🔐 Sécurité & Configuration

### Variables d'environnement

#### Fichier `docker/env/.env.app` (FastAPI)

**Secrets critiques** :
```bash
SECRET_KEY=<générer_clé_sécurisée_64_chars>  # JWT signing
POSTGRES_PASSWORD=<mot_de_passe_fort>
```

**Database** :
```bash
POSTGRES_USERNAME=postgres
POSTGRES_HOST=pgvector
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE=minirag
```

**BAM API** (taux de change) :
```bash
CLE_API_CHANGES=<clé_api_bam_principale>
CLE_API_CHANGES_2=<clé_api_bam_secours>
```

**LLM Configuration** :
```bash
GENERATION_BACKEND=ollama  # ou openai, cohere, groq
GENERATION_MODEL_ID=mistral
OLLAMA_BASE_URL=http://ollama:11434

# Si OpenAI/Cohere/Groq
OPENAI_API_KEY=sk-...
COHERE_API_KEY=...
GROQ_API_KEY=...
```

**Embeddings Configuration** :
```bash
EMBEDDING_BACKEND=local  # ou openai, cohere
EMBEDDING_MODEL_ID=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
EMBEDDING_DEVICE=cpu  # ou cuda
```

**Vector DB Configuration** :
```bash
VECTOR_DB_BACKEND=qdrant  # ou pgvector
VECTOR_DB_PATH=assets/database  # pour Qdrant local
QDRANT_URL=http://qdrant:6333  # pour Qdrant Docker
```

**Langue** :
```bash
PRIMARY_LANG=fr  # ou en, ar
```

#### Fichier `docker/env/.env.postgres` (PGVector)

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<même_que_.env.app>
POSTGRES_DB=minirag
```

#### Fichier `docker/env/.env.grafana` (Grafana)

```bash
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=<mot_de_passe_admin>
```

#### Fichier `docker/env/.env.postgres-exporter` (Metrics)

```bash
DATA_SOURCE_NAME=postgresql://postgres:<password>@pgvector:5432/minirag?sslmode=disable
```

### Ports exposés

| Port | Service | Accès | Usage | Exposition production |
|------|---------|-------|-------|----------------------|
| **80** | nginx | **PUBLIC** | Point d'entrée unique | ✅ Exposé |
| 3000 | grafana | Local | Dashboard admin monitoring | ❌ VPN/Firewall |
| 3001 | frontend | Local | Dev direct (bypass nginx) | ❌ Fermé |
| 5432 | pgvector | Local | Admin base de données | ❌ Localhost only |
| 6333, 6334 | qdrant | Local | Dashboard + gRPC | ❌ Localhost only |
| 8000 | fastapi | Local | API direct (bypass nginx) | ❌ Fermé |
| 9090 | prometheus | Local | Métriques raw | ❌ Localhost only |
| 9100 | node-exporter | Local | Métriques système | ❌ Localhost only |
| 9187 | postgres-exporter | Local | Métriques PostgreSQL | ❌ Localhost only |
| 11434 | ollama | Local | LLM API | ❌ Localhost only |

**⚠️ Sécurité Production** :
- Exposer UNIQUEMENT le port 80 (Nginx)
- Tous les autres ports accessibles via localhost ou VPN
- Configurer firewall (ufw, iptables)
- Activer HTTPS (Let's Encrypt)

### Nginx configuration

**Fichier** : `docker/nginx/default.conf`

**Routing** :
- `/api/*` → `fastapi:8000` (API)
- `/TrhBVe_m5gg2002_E5VVqS` → `fastapi:8000` (Prometheus metrics, obfusqué)
- `/*` → `frontend:80` (React SPA)

**Timeouts** :
```nginx
proxy_connect_timeout 1000s;
proxy_send_timeout 1000s;
proxy_read_timeout 1000s;
```
→ RAG answer generation peut prendre du temps (LLM)

**Upload size** :
```nginx
client_max_body_size 100M;
```
→ Permettre upload PDFs volumineux

---

## 📈 Performance & Ressources

### Limites mémoire par service

| Service | Limite | Réservé | Utilisation réelle (estimée) | Critique |
|---------|--------|---------|------------------------------|----------|
| ollama | 8GB | 4GB | 5-6GB (avec modèle Mistral chargé) | Ajustable |
| fastapi | 4GB | 2GB | 2-3GB (embeddings 768D + app) | Ajustable |
| pgvector | - | - | 500MB-2GB (selon données) | Selon data |
| qdrant | - | - | 200MB-1GB (selon collections) | Selon data |
| prometheus | - | - | 100-200MB (15 jours rétention) | Fixe |
| grafana | - | - | 50-100MB | Fixe |
| frontend | - | - | <50MB (static Nginx) | Fixe |
| nginx | - | - | <20MB | Fixe |
| node-exporter | - | - | <20MB | Fixe |
| postgres-exporter | - | - | <30MB | Fixe |

**Total RAM utilisée** : ~8-12GB (usage normal)

**RAM recommandée** :
- **Minimum** : 16GB (production légère)
- **Recommandé** : 20-24GB (production normale)
- **Optimal** : 32GB+ (production intensive + plusieurs modèles Ollama)

### CPU

- **Minimum** : 4 cores
- **Recommandé** : 8 cores (RAG + ML simultanés)

### Disque

- **Système** : ~10GB
- **Volumes Docker** : 6-20GB (selon usage)
- **Total** : **30-50GB recommandé**

### Réseau

- **Bande passante** : Faible (API REST)
- **Latence** : Critique pour UX (utiliser SSD pour DB)

### Optimisations possibles

**Pour réduire la RAM** :
1. Utiliser modèles Ollama plus petits (Phi3, Gemma 2B)
2. Réduire limite Ollama à 6GB
3. Utiliser embeddings API (OpenAI) au lieu de local

**Pour améliorer les performances** :
1. Ajouter Redis pour caching
2. Activer PostgreSQL connection pooling
3. Utiliser GPU pour Ollama (CUDA)
4. Augmenter workers Uvicorn (actuellement 2)

---

## ✅ Résumé Phase 1

### Ce qui a été documenté

✅ **11 services Docker** avec rôles, ports, dépendances
✅ **Architecture N-Tier** (Présentation → Proxy → App → Data/Vector/AI → Monitoring)
✅ **Flux HTTP** (User → Nginx → Frontend/API → DB/Vector/LLM)
✅ **Flux Monitoring** (Prometheus scrape → Grafana)
✅ **Flux RAG** (Upload → Process → Index → Query → Answer)
✅ **Points d'entrée** (`main.py`, `App.jsx`)
✅ **18 routes React** (2 publiques, 4 user, 12 admin)
✅ **7 routers FastAPI** (40+ endpoints)
✅ **7 volumes persistants** (~6-20GB)
✅ **Ordre de démarrage** optimal
✅ **Configuration sécurité** (4 fichiers .env)
✅ **Ports et exposition** (production vs dev)
✅ **Ressources** (RAM, CPU, disque)

### Prochaine étape

**Phase 2 : Analyse Backend** (FastAPI + RAG)
- Routes & Endpoints détaillés
- Contrôleurs
- Services LangChain
- Modèles & Database
- Module Exchange Rates

---

**Dernière mise à jour** : Décembre 2025
**Durée** : 2 heures
**Statut** : ✅ Complétée
