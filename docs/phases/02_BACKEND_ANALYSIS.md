# Phase 2 : Analyse Backend (FastAPI + RAG)

> **Statut** : ✅ Complétée
> **Durée effective** : 6 heures
> **Date** : Décembre 2025

---

## 📋 Synthèse Globale

**Backend FastAPI complet analysé** :
- **39 endpoints** répartis sur 7 routers
- **5 contrôleurs** (~714 lignes de code)
- **5 services LangChain** (~1252 lignes)
- **7 tables PostgreSQL** avec relations
- **1 module ML** (LSTM pour taux de change)
- **Total** : ~4100 lignes de code Python

---

## 1. Routes & Endpoints (39 endpoints)

### Vue d'ensemble

| Router | Fichier | Endpoints | Auth | Rôle Principal |
|--------|---------|-----------|------|----------------|
| Base | `base.py` | 1 | Public | Info API |
| Auth | `auth.py` | 4 | Mixed | JWT + bcrypt |
| Data | `data.py` | 4 | Admin | Upload & Processing PDF |
| Conversation | `conversation.py` | 4 | User | Historique chat |
| NLP | `nlp.py` | 4 | Mixed | **Pipeline RAG complet** |
| Admin | `admin.py` | 15 | Admin | CRUD toutes entités |
| Exchange | `exchange_routes.py` | 7 | Mixed | Prédictions ML |

### 1.1 Auth Router - Authentification JWT

**4 endpoints** pour l'authentification avec JWT (24h) et bcrypt (cost 12).

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/api/v1/auth/register` | POST | Public | Inscription (1er user = admin auto) |
| `/api/v1/auth/login` | POST | Public | Login → JWT token (24h) |
| `/api/v1/auth/me` | GET | User | Infos utilisateur actuel |
| `/api/v1/auth/users` | GET | Admin | Liste tous les users |

**Caractéristiques** :
- JWT payload : `{username, role, exp}`
- Expiration : 24 heures
- Rôles : `admin` ou `user`
- Premier utilisateur inscrit devient automatiquement admin

### 1.2 Data Router - Gestion Fichiers

**4 endpoints** pour upload et traitement des PDF.

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/data/upload/{project_id}` | POST (Admin) | Upload PDFs (max 100MB) |
| `/api/v1/data/process/{project_id}` | POST (Admin) | Process PDFs → chunks |
| `/api/v1/data/project/{id}/language` | GET (User) | Récupérer langue + nom projet |
| `/api/v1/data/project/{id}/language` | PUT (Admin) | Modifier langue (FR/EN/AR) |

**Paramètres processing** :
- `chunk_size` : Taille des chunks (défaut : 1000)
- `overlap_size` : Chevauchement (défaut : 200)
- `do_reset=1` : Supprime vecteurs + chunks avant reprocessing

### 1.3 NLP Router - Pipeline RAG

**4 endpoints** pour le RAG complet (indexation + recherche + Q&A).

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/v1/nlp/index/push/{project_id}` | POST (Admin) | Indexer chunks → Qdrant (batch 50) |
| `/api/v1/nlp/index/info/{project_id}` | GET (User) | Stats collection vecteurs |
| `/api/v1/nlp/index/search/{project_id}` | POST (User) | Recherche similarité (top K) |
| `/api/v1/nlp/index/answer/{project_id}` | POST (User) | **RAG Q&A avec historique** |

**Pipeline RAG** : Question → Embed → Search (k=10) → Context + Prompt → LLM → Answer

**Code clé (endpoint answer)** :
```python
# Si conversation_id fourni, récupérer l'historique
if conversation_id:
    messages = await get_messages_by_conversation_id(conversation_id)
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

# RAG avec historique conversationnel
answer, sources = await nlp_controller.aanswer_rag_question(
    project=project,
    query=text,
    limit=10,
    conversation_history=conversation_history
)
```

### 1.4 Admin Router - CRUD Complet

**15 endpoints** pour gérer toutes les entités (admin only).

**Entités gérées** :
- Projects (4 endpoints) : Liste, Récupérer un projet, Modifier nom, Suppression
- Assets (2 endpoints) : Liste par projet, Suppression
- Chunks (2 endpoints) : Liste par projet, Suppression
- Conversations (2 endpoints) : Liste toutes, Suppression
- Messages (2 endpoints) : Liste par conversation, Suppression
- Vectors (3 endpoints) : Liste, Suppression par projet, Suppression collection

**Nouveaux endpoints projects** :
- `GET /admin/projects/{id}` : Récupérer un projet spécifique
- `PATCH /admin/projects/{id}/name` : Modifier le nom d'un projet

**Pagination** : `page=1`, `page_size=20` (défaut)

**Suppression cascade** : Project → Assets → Chunks → Vectors

### 1.5 Exchange Rates Router - ML

**7 endpoints** pour prédictions taux MAD/EUR et MAD/USD.

**Public** :
- `GET /latest` : Derniers taux
- `GET /predictions` : Prédictions LSTM (7 jours)
- `GET /history` : Historique avec plage dates

**Admin** :
- `POST /admin/train-model` : Entraîner LSTM
- `POST /admin/generate-predictions` : Générer prédictions
- `POST /admin/fetch-rates-now` : Fetch immédiat Bank Al-Maghrib
- `GET /admin/scheduler/status` : Statut scheduler

---

## 2. Contrôleurs (5 classes, ~714 lignes)

### Vue d'ensemble

| Contrôleur | Lignes | Méthodes | Rôle Principal |
|------------|--------|----------|----------------|
| BaseController | 35 | 2 | Configuration commune |
| ProjectController | 22 | 1 | Gestion répertoires projets |
| DataController | 55 | 4 | Validation et upload fichiers |
| ProcessController | 136 | 6 | Processing PDF → Chunks |
| **NLPController** | 466 | 11 | **Orchestration RAG complet** |

### 2.1 NLPController - Le Plus Important

**Responsabilités** :
- Orchestration complète du pipeline RAG
- Gestion multi-provider (LLM, embeddings, vector DB)
- Cache des vectorstores par projet
- Indexation et recherche vectorielle
- Génération réponses avec contexte + historique

**Méthodes clés** :

| Méthode | Description |
|---------|-------------|
| `_get_llm()` | Factory multi-provider (OpenAI/Ollama/Cohere/Groq) |
| `_get_vectorstore()` | Cache vectorstore par projet |
| `create_collection_name()` | Génère nom : `collection_{dim}_{project_id}` |
| `index_into_vector_db()` | Indexation chunks (batch 50) |
| `asearch_in_vector_db()` | Recherche similarité async |
| `aanswer_rag_question()` | **RAG Q&A avec historique conversationnel** |

**Code clé (Factory LLM)** :
```python
def _get_llm(self):
    """Factory pattern : 4 providers supportés"""
    if self.generation_backend == "openai":
        return ChatOpenAI(
            model=self.generation_model,
            api_key=self.api_key,
            temperature=0.7,
            max_tokens=1000
        )
    elif self.generation_backend == "ollama":
        return ChatOllama(
            model=self.generation_model,
            base_url="http://ollama:11434",
            temperature=0.7,
            num_predict=1000
        )
    # + cohere, groq
```

**Code clé (Cache vectorstore)** :
```python
def _get_vectorstore(self, project):
    """Pattern Cache : 1 vectorstore par projet en mémoire"""
    collection_name = self.create_collection_name(project.project_id)

    if collection_name not in self._vectorstores:
        self._vectorstores[collection_name] = VectorStoreService(
            embeddings=self.embeddings_service,
            provider=self.vector_db_backend,
            collection_name=collection_name,
            path=self.database_dir,
            url=self.vector_db_url
        )

    return self._vectorstores[collection_name]
```

**Patterns** : Factory, Cache, Facade, Strategy

---

## 3. Services LangChain (5 services, ~1252 lignes)

### Vue d'ensemble

| Service | Lignes | Méthodes | Rôle Principal |
|---------|--------|----------|----------------|
| **RAGService** | 423 | 11 | Pipeline LCEL + historique |
| EmbeddingsService | 173 | 8 | Multi-provider embeddings |
| VectorStoreService | 301 | 11 | Interface Qdrant unifiée |
| PromptService | 178 | 7 | Prompts multilingues |
| DocumentService | 177 | 9 | Loading & Chunking |

### 3.1 RAGService - Pipeline LCEL

**LCEL** (LangChain Expression Language) : composition fonctionnelle du pipeline RAG.

**Architecture pipeline** :
```python
chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

**Méthodes principales** :

| Méthode | Type | Description |
|---------|------|-------------|
| `_build_rag_chain()` | - | Construction pipeline LCEL |
| `answer_with_sources()` | Sync | Réponse + sources |
| `aanswer_with_sources()` | Async | Réponse + sources (async) |
| `aanswer_with_sources_and_history()` | Async | **RAG conversationnel** |
| `stream_answer()` | Generator | Streaming token par token |

**Code clé (RAG conversationnel)** :
```python
async def aanswer_with_sources_and_history(
    self, question: str, chat_history: Optional[List[dict]] = None
):
    """RAG avec historique conversationnel"""
    retriever = self.vectorstore_service.as_retriever(search_kwargs={"k": 5})

    if chat_history:
        from langchain_core.messages import HumanMessage, AIMessage

        # Convertir historique en format LangChain
        formatted_history = []
        for msg in chat_history:
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                formatted_history.append(AIMessage(content=msg["content"]))

        # Pipeline avec historique
        prompt = self.prompt_service.create_conversational_rag_prompt()
        chain_with_sources = RunnableParallel({
            "answer": (
                {
                    "context": retriever | self._format_docs,
                    "question": RunnablePassthrough(),
                    "chat_history": lambda x: formatted_history
                }
                | prompt | self.llm | StrOutputParser()
            ),
            "sources": retriever
        })

    result = await chain_with_sources.ainvoke(question)
    return result
```

**Patterns** : LCEL, Strategy, Builder, Async/Await

### 3.2 EmbeddingsService - Multi-provider

**3 providers supportés** :

| Provider | Type | Models Disponibles | Dimensions |
|----------|------|-------------------|------------|
| **local** | HuggingFace | multilingual, english | 384 ou 768 |
| **openai** | API | text-embedding-3-small/large | 1536 ou 3072 |
| **cohere** | API | embed-multilingual-v3.0 | 1024 |

**Modèles HuggingFace** :
```python
HUGGINGFACE_MODELS = {
    "multilingual": "paraphrase-multilingual-mpnet-base-v2",  # 768D (DÉFAUT)
    "multilingual-mini": "paraphrase-multilingual-MiniLM-L12-v2",  # 384D
    "english": "all-mpnet-base-v2",  # 768D
    "english-mini": "all-MiniLM-L6-v2"  # 384D
}
```

**Singleton pattern** :
```python
@lru_cache(maxsize=1)
def get_embeddings_instance(...) -> EmbeddingsService:
    """Cache instance pour éviter rechargement modèle"""
    return EmbeddingsService(...)
```

**Patterns** : Strategy, Singleton, Factory Method

### 3.3 VectorStoreService - Interface Qdrant

**Interface unifiée** pour Qdrant avec création automatique de collection.

**Méthodes clés** :

| Méthode | Type | Description |
|---------|------|-------------|
| `_init_qdrant()` | - | Config + création collection |
| `add_documents()` | Sync | Indexation batch |
| `asimilarity_search_with_score()` | Async | Recherche + scores |
| `as_retriever()` | - | Créer retriever pour LCEL |
| `delete_by_metadata()` | - | Suppression par filtre |

**Search types** :
- `similarity` : Recherche similarité standard
- `mmr` : Maximal Marginal Relevance (résultats diversifiés)
- `similarity_score_threshold` : Filtrage par score minimum

**Patterns** : Facade, Lazy Initialization, Adapter

### 3.4 PromptService - Multilingue

**Prompts en 3 langues** : EN, FR, AR.

**Templates disponibles** :
- `create_rag_prompt()` : Prompt RAG basique
- `create_conversational_rag_prompt()` : Avec historique conversationnel
- `format_documents()` : Formatage documents pour contexte

**Structure prompt conversationnel** :
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", self.system_prompt),  # Instructions
    ("system", "Documents:\n\n{context}"),  # Contexte
    ("placeholder", "{chat_history}"),  # Historique
    ("human", "{question}")  # Question actuelle
])
```

**Patterns** : Strategy (multi-langue), Template Method, Builder

### 3.5 DocumentService - Loading & Chunking

**Loading** : TextLoader (TXT), PyMuPDFLoader (PDF)

**Chunking intelligent** :
```python
RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)
```

**Ordre priorité séparateurs** :
1. `\n\n` : Paragraphes (contexte maximal)
2. `\n` : Lignes
3. `. ` : Phrases (préserve sémantique)
4. ` ` : Mots
5. `""` : Caractères (dernier recours)

**Patterns** : Factory Method, Strategy, Pipeline

---

## 4. Modèles & Database (7 tables)

### ERD (Entity Relationship Diagram)

```
┌──────────────┐
│    users     │
│──────────────│
│ user_id (PK) │◀───────┐
│ username     │        │
│ password     │        │ 1:N
│ role         │        │
└──────────────┘        │
                        │
┌──────────────┐        │
│   projects   │        │
│──────────────│        │
│ project_id   │        │
│ project_name │        │
│ language     │        │
└──────────────┘        │
       │                │
       │ 1:N            │
       ▼                │
┌──────────────┐        │
│    assets    │        │
│──────────────│        │
│ asset_id (PK)│        │
│ project_id   │        │
│ file_id      │        │
└──────────────┘        │
       │                │
       │ 1:N            │
       ▼                │
┌──────────────┐        │
│    chunks    │        │
│──────────────│        │
│ chunk_id (PK)│        │
│ asset_id     │        │
│ chunk_text   │        │
└──────────────┘        │
                        │
┌──────────────────┐    │
│  conversations   │    │
│──────────────────│    │
│ conversation_id  │◀───┘
│ user_id (FK)     │
│ project_id       │
│ title            │
└──────────────────┘
       │
       │ 1:N
       ▼
┌──────────────────┐
│    messages      │
│──────────────────│
│ message_id (PK)  │
│ conversation_id  │
│ role             │
│ content          │
└──────────────────┘

┌──────────────────┐
│  exchange_rates  │
│──────────────────│
│ rate_id (PK)     │
│ currency_pair    │
│ rate             │
│ is_prediction    │
└──────────────────┘
```

### Tables Détaillées

| Table | Clé Primaire | Relations | Rôle |
|-------|--------------|-----------|------|
| **users** | user_id | 1:N conversations | Authentification JWT |
| **projects** | project_id | 1:N assets | Projets RAG |
| **assets** | asset_id | N:1 projects, 1:N chunks | Fichiers PDF uploadés |
| **chunks** | chunk_id | N:1 assets | Texte découpé (source vérité) |
| **conversations** | conversation_id | N:1 users, 1:N messages | Historique conversationnel |
| **messages** | message_id | N:1 conversations | Questions + Réponses |
| **exchange_rates** | rate_id | - | Taux historiques + prédictions |

### Configuration Database

**PostgreSQL 17** avec extension PGVector :
```python
DATABASE_URL = "postgresql+asyncpg://user:pass@postgres:5432/rag_finance"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

**Caractéristiques** :
- SQLAlchemy async (`asyncpg` driver)
- Connection pooling : 10 connexions (max 20)
- Suppression cascade : Project → Assets → Chunks → Vectors
- Index : `username`, `date` (exchange_rates)

---

## 5. Module Exchange Rates (ML)

### Architecture LSTM

**Modèle TensorFlow** :
```python
model = Sequential([
    LSTM(50, return_sequences=True, input_shape=(30, 1)),
    LSTM(50, return_sequences=False),
    Dense(7)  # 7 jours de prédictions
])

model.compile(optimizer='adam', loss='mse')
```

**Training** :
- Input : 30 jours historiques
- Output : 7 jours futurs
- Epochs : 100, Batch size : 32
- Validation split : 20%

### Scheduler APScheduler

**Job quotidien** : Fetch taux Bank Al-Maghrib à 18h00
```python
scheduler.add_job(
    func=fetch_rates_from_api,
    trigger="cron",
    hour=18, minute=0,
    id="daily_rates_fetch"
)
```

### API Bank Al-Maghrib

**Paires supportées** : MAD/EUR, MAD/USD

**Stockage** :
- `is_prediction=False` : Taux réels (Bank Al-Maghrib)
- `is_prediction=True` : Prédictions LSTM (7 jours)

---

## 6. Flux RAG Complet End-to-End

```
┌─────────────────────────────────────────────────────────┐
│              PIPELINE RAG COMPLET                       │
└─────────────────────────────────────────────────────────┘

1. UPLOAD (Admin)
   POST /api/v1/data/upload/{project_id}
   → DataController.validate() (PDF, max 100MB)
   → Stockage: assets/files/{project_id}/{random_id}_{name}.pdf
   → AssetModel.create_asset() → PostgreSQL

2. PROCESSING (Admin)
   POST /api/v1/data/process/{project_id}
   → ProcessController.process_file()
   → DocumentService.load_document() (PyMuPDFLoader)
   → DocumentService.chunk_documents() (RecursiveTextSplitter)
      • chunk_size=1000, overlap=200
      • separators=["\n\n", "\n", ". ", " ", ""]
   → ChunkModel.insert_many_chunks() → PostgreSQL

3. INDEXATION (Admin)
   POST /api/v1/nlp/index/push/{project_id}
   → NLPController.index_into_vector_db()
   → EmbeddingsService.embed_documents() (768D multilingual)
   → VectorStoreService.add_documents() (Qdrant, batch 50)

4. QUESTION ANSWERING (User)
   POST /api/v1/nlp/index/answer/{project_id}
   Body: {
     "text": "Question?",
     "conversation_id": 123  // optionnel
   }

   → Si conversation_id: récupérer historique (MessageModel)
   → NLPController.aanswer_rag_question()
   → EmbeddingsService.embed_query() → vecteur 768D
   → VectorStoreService.asearch(k=10) → Top 10 chunks
   → PromptService.format_documents() (contexte + question + history)
   → RAGService.aanswer_with_sources_and_history()
   → LCEL Chain:
       {context, question, chat_history}
       → Prompt (EN/FR/AR)
       → LLM (Ollama/OpenAI/Cohere/Groq)
       → Answer

   → MessageModel.create_message() (save Q&A)
   → Response: {"answer": "...", "sources": [...]}
```

---

## 7. Patterns Architecturaux Identifiés

| Pattern | Localisation | Usage |
|---------|--------------|-------|
| **LCEL** | RAGService | Composition fonctionnelle pipeline RAG |
| **Factory** | NLPController, Services | Multi-provider LLM/Embeddings/VectorDB |
| **Strategy** | RAGService, EmbeddingsService | Interchangeabilité providers |
| **Singleton** | EmbeddingsService | Cache instance avec @lru_cache |
| **Cache** | NLPController | Vectorstores par projet (dict) |
| **Facade** | VectorStoreService | Simplification API Qdrant complexe |
| **Repository** | Models | Abstraction accès données |
| **Dependency Injection** | FastAPI | Routes → Controllers → Services |
| **Async/Await** | Routes, Services | Performance I/O-bound |
| **Pipeline** | ProcessController | Load → Transform → Save |

---

## 8. Technologies & Versions

| Technologie | Version | Usage |
|-------------|---------|-------|
| **FastAPI** | 0.115+ | Framework async REST API |
| **LangChain** | 0.3+ | LCEL, embeddings, vector stores |
| **PostgreSQL** | 17 | Database principale + PGVector |
| **Qdrant** | 1.13.6 | Vector database (768D embeddings) |
| **TensorFlow** | 2.x | LSTM predictions exchange rates |
| **bcrypt** | - | Password hashing (cost 12) |
| **JWT** | - | Authentication tokens (24h) |
| **APScheduler** | - | Scheduler tâches quotidiennes |
| **SQLAlchemy** | 2.x | ORM async (asyncpg driver) |

---

## 9. Statistiques Finales

### Code Backend

- **Routes** : ~2134 lignes (7 fichiers)
- **Contrôleurs** : ~714 lignes (5 fichiers)
- **Services** : ~1252 lignes (5 fichiers)
- **Total backend** : ~4100 lignes Python

### Endpoints par Authentification

- **Admin only** : 70% (26/37 endpoints)
- **User** : 27% (10/37 endpoints)
- **Public** : 3% (1/37 endpoint)

### Performance

- **Batch indexation** : 50 documents/batch
- **Async/await** : Toutes opérations I/O
- **Connection pool** : 10 connexions (max 20)
- **Cache** : Vectorstores + Embeddings (singleton)
- **Embeddings** : 768 dimensions (multilingual)

---

## 10. Points d'Amélioration (→ Phase 6)

### Tests
- Tests unitaires : Controllers, Services
- Tests intégration : Routes → DB
- Tests E2E : RAG complet (upload → answer)

### Sécurité
- Rate limiting sur endpoints publics
- Input validation renforcée (sanitization)
- Secrets management (vault, non .env)
- CORS configuré strictement

### Performance
- Redis cache pour résultats RAG fréquents
- Compression HTTP (gzip)
- CDN pour assets statiques
- Index DB additionnels

### Monitoring
- Logging structuré (JSON format)
- Tracing distribué (OpenTelemetry)
- Alerting (Prometheus + Alertmanager)
- Métriques custom (latence RAG, tokens/s)

### Nouvelles Fonctionnalités
- Multi-tenant (isolation projets)
- Versioning documents
- Annotation chunks (feedback loop)
- Fine-tuning LLM sur données métier
- Streaming SSE pour réponses
- Support multimodal (images, tableaux)

---

## ✅ Phase 2 Complétée !

**Total analysé** :
- 7 routers (37 endpoints)
- 5 contrôleurs (714 lignes)
- 5 services LangChain (1252 lignes)
- 7 modèles DB (PostgreSQL + PGVector)
- 1 module ML (LSTM Exchange Rates)

**Prochaine étape** : **Phase 3 - Analyse Frontend (React)**
