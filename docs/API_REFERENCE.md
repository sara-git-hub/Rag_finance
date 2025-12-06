# 🔌 API Reference - Projet Fil Rouge

> Référence complète des 39 endpoints de l'API FastAPI
> **Base URL** : `http://localhost:8000` (développement) ou votre domaine en production
> **Dernière mise à jour** : Décembre 2025

---

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Base](#base) - 1 endpoint
3. [Authentication](#authentication) - 4 endpoints
4. [Data Management](#data-management) - 4 endpoints
5. [NLP / RAG](#nlp--rag) - 4 endpoints
6. [Conversations](#conversations) - 4 endpoints
7. [Exchange Rates](#exchange-rates) - 7 endpoints
8. [Admin](#admin) - 15 endpoints
9. [Codes d'erreur](#codes-derreur)

---

## Vue d'ensemble

### Architecture API

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Port 80)                      │
│                  Reverse Proxy                          │
└─────────────────┬───────────────────────────────────────┘
                  │
         ┌────────┴────────┐
         │                 │
    ┌────▼────┐      ┌────▼────┐
    │Frontend │      │FastAPI  │
    │React    │      │Backend  │
    │Port 3001│      │Port 8000│
    └─────────┘      └────┬────┘
                          │
            ┌─────────────┼─────────────┐
            │             │             │
       ┌────▼───┐   ┌────▼────┐   ┌───▼────┐
       │PostgreSQL   │ Qdrant  │   │ Ollama │
       │  PGVector   │ VectorDB│   │  LLM   │
       └────────┘   └─────────┘   └────────┘
```

### Authentication

**Méthode** : JWT (JSON Web Tokens)
**Header** : `Authorization: Bearer <token>`
**Expiration** : 24 heures
**Algorithm** : HS256

**Exemple de requête authentifiée** :
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6..." \
     http://localhost:8000/api/v1/auth/me
```

### Rôles Utilisateurs

| Rôle | Description | Endpoints accessibles |
|------|-------------|----------------------|
| **admin** | Administrateur (1er utilisateur inscrit) | Tous les endpoints |
| **user** | Utilisateur standard | Consultation + Q&A RAG |

---

## Base

### 0. API Info

**Endpoint** : `GET /api/v1/`
**Auth** : Public (aucune authentification requise)
**Description** : Retourne les informations de base sur l'API.

**Response (200 OK)** :
```json
{
  "app_name": "RAG Finance API",
  "app_version": "1.0",
  "message": "Bienvenue dans l'API de rag_finance!"
}
```

---

## Authentication

### 1. Register User

**Endpoint** : `POST /api/v1/auth/register`
**Auth** : Public (aucune authentification requise)
**Description** : Inscription d'un nouvel utilisateur. Le premier utilisateur devient automatiquement admin.

**Request Body** :
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecureP@ss123"
}
```

**Response (200 OK)** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "admin",
  "username": "johndoe"
}
```

**Errors** :
- `400 Bad Request` : Username or email already exists
- `422 Unprocessable Entity` : Invalid email format

---

### 2. Login

**Endpoint** : `POST /api/v1/auth/login`
**Auth** : Public
**Description** : Connexion avec username/password, retourne un token JWT.

**Request Body** :
```json
{
  "username": "johndoe",
  "password": "SecureP@ss123"
}
```

**Response (200 OK)** :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "role": "user",
  "username": "johndoe"
}
```

**Errors** :
- `401 Unauthorized` : Incorrect username or password
- `403 Forbidden` : User account is inactive

---

### 3. Get Current User

**Endpoint** : `GET /api/v1/auth/me`
**Auth** : User (JWT required)
**Description** : Récupère les informations de l'utilisateur connecté.

**Response (200 OK)** :
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true
}
```

**Errors** :
- `401 Unauthorized` : Token invalid or expired
- `404 Not Found` : User not found

---

### 4. List All Users

**Endpoint** : `GET /api/v1/auth/users`
**Auth** : Admin only
**Description** : Liste tous les utilisateurs (admin uniquement).
**Response (200 OK)** :
```json
[
  {
    "username": "admin",
    "email": "admin@example.com",
    "role": "admin",
    "is_active": true
  },
  {
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true
  }
]
```

**Errors** :
- `401 Unauthorized` : Not authenticated
- `403 Forbidden` : Not admin

---

## Data Management

### 5. Upload File

**Endpoint** : `POST /api/v1/data/upload/{project_id}`
**Auth** : Admin only
**Description** : Upload un fichier PDF vers un projet. Peut définir la langue du projet lors du premier upload.

**Path Parameters** :
- `project_id` (int) : ID du projet (créé automatiquement s'il n'existe pas)

**Query Parameters** :
- `language` (string, optional) : Langue du projet (`fr`, `en`, `ar`). Uniquement au premier upload.

**Request (multipart/form-data)** :
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "file=@document.pdf" \
  "http://localhost:8000/api/v1/data/upload/1?language=fr"
```

**Response (200 OK)** :
```json
{
  "signal": "FILE_UPLOAD_SUCCESS",
  "file_id": "42",
  "project_language": "fr"
}
```

**Validation** :
- Max size : 100 MB
- Allowed types : `application/pdf`

**Errors** :
- `400 Bad Request` : File too large, invalid type, or invalid language
- `403 Forbidden` : Not admin

---

### 6. Process Documents

**Endpoint** : `POST /api/v1/data/process/{project_id}`
**Auth** : Admin only
**Description** : Traite les PDFs uploadés : extraction de texte, découpage en chunks, stockage en base.

**Path Parameters** :
- `project_id` (int) : ID du projet

**Request Body** :
```json
{
  "chunk_size": 1000,
  "overlap_size": 200,
  "do_reset": false
}
```

**Parameters** :
- `chunk_size` (int, default: 1000) : Taille des chunks en caractères
- `overlap_size` (int, default: 200) : Chevauchement entre chunks
- `do_reset` (bool, default: false) : Si `true`, supprime les chunks existants avant reprocessing

**Response (200 OK)** :
```json
{
  "signal": "PROCESSING_SUCCESS",
  "chunks_created": 245,
  "files_processed": 3
}
```

**Process Pipeline** :
```
1. Load PDF files (PyMuPDF)
2. Extract text per page
3. Split with RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
4. Store chunks in PostgreSQL (datachunks table)
5. Generate metadata (page_number, asset_id)
```

**Errors** :
- `400 Bad Request` : No files to process
- `403 Forbidden` : Not admin

---

### 7. Get Project Language

**Endpoint** : `GET /api/v1/data/project/{project_id}/language`
**Auth** : User
**Description** : Récupère la langue configurée pour un projet ainsi que son nom.

**Response (200 OK)** :
```json
{
  "signal": "PROJECT_LANGUAGE_RETRIEVED",
  "project_id": 1,
  "project_name": "Project Alpha",
  "language": "fr",
  "file_count": 5,
  "can_change_language": false
}
```

**Fields** :
- `project_name` (string) : Nom du projet
- `language` (string) : Langue du projet (fr, en, ar)
- `file_count` (int) : Nombre de fichiers dans le projet
- `can_change_language` (bool) : Indique si la langue peut être modifiée (seulement si aucun fichier)

---

### 8. Update Project Language

**Endpoint** : `PUT /api/v1/data/project/{project_id}/language`
**Auth** : Admin only
**Description** : Modifie la langue d'un projet (influence les prompts RAG).

**Request Body** :
```json
{
  "language": "en"
}
```

**Allowed values** : `fr` (français), `en` (anglais), `ar` (arabe)

**Response (200 OK)** :
```json
{
  "signal": "LANGUAGE_UPDATED",
  "project_id": 1,
  "language": "en"
}
```

---

## NLP / RAG

### 9. Index to Vector DB

**Endpoint** : `POST /api/v1/nlp/index/push/{project_id}`
**Auth** : Admin only
**Description** : Indexe les chunks de texte dans Qdrant (vector database) avec embeddings.

**Request Body** :
```json
{
  "batch_size": 50,
  "do_reset": false
}
```

**Parameters** :
- `batch_size` (int, default: 50) : Nombre de chunks par batch
- `do_reset` (bool, default: false) : Si `true`, supprime la collection Qdrant avant indexation

**Response (200 OK)** :
```json
{
  "signal": "INSERT_INTO_VECTORDB_SUCCESS",
  "inserted_items_count": 245
}
```

**Indexation Pipeline** :
```
1. Récupérer chunks depuis PostgreSQL (pagination)
2. Générer embeddings (sentence-transformers multilingual, dim=768)
3. Batch insert dans Qdrant (HNSW algorithm, cosine similarity)
4. Collection name : collection_768_{project_id}
```

**Performance** :
- ~50 chunks/seconde (embeddings local CPU)
- ~200 chunks/seconde (embeddings GPU)

---

### 10. Get Index Info

**Endpoint** : `GET /api/v1/nlp/index/info/{project_id}`
**Auth** : Admin only
**Description** : Récupère les statistiques de la collection vectorielle Qdrant.

**Response (200 OK)** :
```json
{
  "signal": "VECTORDB_COLLECTION_RETRIEVED",
  "collection_info": {
    "vectors_count": 245,
    "indexed_vectors_count": 245,
    "points_count": 245,
    "segments_count": 1,
    "status": "green",
    "optimizer_status": "ok",
    "disk_usage_bytes": 2457600
  }
}
```

---

### 11. Semantic Search

**Endpoint** : `POST /api/v1/nlp/index/search/{project_id}`
**Auth** : User
**Description** : Recherche sémantique dans les documents (sans génération LLM).

**Request Body** :
```json
{
  "text": "What is the financial performance?",
  "limit": 10
}
```

**Parameters** :
- `text` (string) : Query de recherche
- `limit` (int, default: 10) : Nombre de résultats (top K)

**Response (200 OK)** :
```json
{
  "signal": "SEARCH_SUCCESS",
  "results": [
    {
      "chunk_id": 123,
      "content": "The company achieved strong financial performance...",
      "score": 0.92,
      "metadata": {
        "page_number": 15,
        "asset_id": 5,
        "filename": "annual_report_2024.pdf"
      }
    }
  ]
}
```

**Algorithm** :
- Embedding de la query (768D vector)
- Cosine similarity search dans Qdrant
- Retourne top K chunks triés par score

---

### 12. RAG Question Answering

**Endpoint** : `POST /api/v1/nlp/index/answer/{project_id}`
**Auth** : User
**Description** : **Endpoint principal RAG** - Pose une question, récupère contexte pertinent, génère réponse avec LLM.

**Request Body** :
```json
{
  "text": "Quel est le chiffre d'affaires de l'entreprise?",
  "limit": 10,
  "conversation_id": 42
}
```

**Parameters** :
- `text` (string) : Question de l'utilisateur
- `limit` (int, default: 10) : Nombre de chunks de contexte
- `conversation_id` (int, optional) : ID conversation pour historique contextuel

**Response (200 OK)** :
```json
{
  "signal": "ANSWER_SUCCESS",
  "answer": "Le chiffre d'affaires de l'entreprise en 2024 s'élève à 150 millions d'euros, soit une croissance de 12% par rapport à 2023.",
  "sources": [
    {
      "chunk_id": 156,
      "content": "...chiffre d'affaires 2024: 150M€...",
      "score": 0.94,
      "page_number": 8,
      "filename": "rapport_financier.pdf"
    }
  ],
  "message_id": 789,
  "conversation_id": 42
}
```

**RAG Pipeline Complet** :
```
1. Embed query (768D)
2. Search top K chunks in Qdrant (similarity cosine)
3. Retrieve conversation history (if conversation_id provided)
4. Build prompt:
   - System: "Tu es un assistant financier expert..."
   - Context: [chunks pertinents]
   - History: [messages précédents]
   - Question: [user query]
5. LLM Generation (Ollama/OpenAI/Cohere/Groq)
6. Store user message + AI response in PostgreSQL
7. Return answer + sources
```

**LLM Providers** :
- **Ollama** (local, gratuit) : Mistral, Llama3.1, Gemma2
- **OpenAI** : GPT-3.5-turbo, GPT-4o-mini
- **Cohere** : Command-R, Command-R-Plus
- **Groq** : Llama-3.1-70b-versatile (rapide)

---

## Conversations

### 13. Create Conversation

**Endpoint** : `POST /api/v1/conversations/create`
**Auth** : User
**Description** : Crée une nouvelle conversation pour un projet.

**Request Body** :
```json
{
  "project_id": 1,
  "title": "Questions sur le rapport Q2"
}
```

**Parameters** :
- `project_id` (int) : ID du projet
- `title` (string, optional) : Titre personnalisé (auto-généré si omis)

**Response (200 OK)** :
```json
{
  "conversation_id": 42,
  "project_id": 1,
  "title": "Questions sur le rapport Q2",
  "status": "active",
  "created_at": "2025-12-04T10:30:00",
  "updated_at": null
}
```

---

### 14. List Conversations

**Endpoint** : `GET /api/v1/conversations/project/{project_id}`
**Auth** : User
**Description** : Liste toutes les conversations de l'utilisateur pour un projet.

**Query Parameters** :
- `status_filter` (string, optional) : `active` ou `archived`

**Response (200 OK)** :
```json
{
  "project_id": 1,
  "conversations": [
    {
      "conversation_id": 42,
      "title": "Questions sur le rapport Q2",
      "status": "active",
      "created_at": "2025-12-04T10:30:00",
      "updated_at": "2025-12-04T14:20:00",
      "message_count": 8
    }
  ]
}
```

---

### 15. Get Messages

**Endpoint** : `GET /api/v1/conversations/{conversation_id}/messages`
**Auth** : User (owner only)
**Description** : Récupère tous les messages d'une conversation.

**Query Parameters** :
- `limit` (int, default: 100) : Nombre max de messages

**Response (200 OK)** :
```json
{
  "conversation_id": 42,
  "messages": [
    {
      "message_id": 101,
      "role": "user",
      "content": "Quel est le CA Q2?",
      "created_at": "2025-12-04T10:31:00"
    },
    {
      "message_id": 102,
      "role": "assistant",
      "content": "Le CA Q2 est de 38M€...",
      "created_at": "2025-12-04T10:31:05"
    }
  ]
}
```

**Security** : Vérifie que l'utilisateur est propriétaire de la conversation

---

### 16. Delete Conversation

**Endpoint** : `DELETE /api/v1/conversations/{conversation_id}`
**Auth** : User (owner only)
**Description** : Supprime une conversation et tous ses messages.

**Response (200 OK)** :
```json
{
  "message": "Conversation deleted successfully",
  "conversation_id": 42
}
```

**⚠️ Warning** : Opération irréversible. Suppression en cascade de tous les messages.

---

## Exchange Rates

### 17. Get Latest Rates

**Endpoint** : `GET /api/v1/exchange-rates/latest`
**Auth** : User
**Description** : Récupère les derniers taux de change MAD/EUR et MAD/USD.

**Response (200 OK)** :
```json
{
  "signal": "LATEST_RATES_RETRIEVED",
  "data": {
    "MAD/EUR": {
      "date": "2025-12-04",
      "achat": 10.85,
      "vente": 10.92,
      "moyenne": 10.885
    },
    "MAD/USD": {
      "date": "2025-12-04",
      "achat": 9.78,
      "vente": 9.85,
      "moyenne": 9.815
    }
  }
}
```

**Source** : Bank Al-Maghrib (BAM) API

---

### 18. Get Predictions

**Endpoint** : `GET /api/v1/exchange-rates/predictions`
**Auth** : User
**Description** : Récupère historique + prédictions ML (LSTM) pour une paire de devises.

**Query Parameters** :
- `currency_pair` (string, required) : `MAD/EUR` ou `MAD/USD`
- `days_history` (int, default: 30) : Jours d'historique (7-365)
- `days_ahead` (int, default: 7) : Jours de prédictions (1-30)

**Example Request** :
```bash
GET /api/v1/exchange-rates/predictions?currency_pair=MAD/EUR&days_history=30&days_ahead=7
```

**Response (200 OK)** :
```json
{
  "signal": "PREDICTIONS_RETRIEVED",
  "data": {
    "currency_pair": "MAD/EUR",
    "history": [
      {"date": "2025-11-04", "moyenne": 10.82, "type": "actual"},
      {"date": "2025-11-05", "moyenne": 10.83, "type": "actual"}
    ],
    "predictions": [
      {"date": "2025-12-05", "moyenne": 10.89, "type": "predicted"},
      {"date": "2025-12-06", "moyenne": 10.90, "type": "predicted"}
    ],
    "model_info": {
      "architecture": "LSTM",
      "input_window": 30,
      "forecast_horizon": 7,
      "training_samples": 2100
    }
  }
}
```

**ML Model** :
- Architecture : LSTM (2 layers, 50 units each)
- Input : 30 jours historiques
- Output : 7 jours prédictions
- Framework : TensorFlow 2.16+
- Réentraînement : Mensuel automatique

---

### 19. Get History

**Endpoint** : `GET /api/v1/exchange-rates/history`
**Auth** : User
**Description** : Récupère l'historique complet des taux de change.

**Query Parameters** :
- `currency_pair` (string, required) : `MAD/EUR` ou `MAD/USD`
- `days` (int, default: 365) : Nombre de jours (1-730)

**Response (200 OK)** :
```json
{
  "signal": "HISTORY_RETRIEVED",
  "data": {
    "currency_pair": "MAD/EUR",
    "records": [
      {
        "date": "2024-12-04",
        "achat": 10.75,
        "vente": 10.82,
        "moyenne": 10.785
      }
    ],
    "count": 365
  }
}
```

---

### 20. Train ML Model (Admin)

**Endpoint** : `POST /api/v1/exchange-rates/admin/train-model`
**Auth** : Admin only
**Description** : Entraîne le modèle LSTM sur les données historiques.

**Request Body** :
```json
{
  "currency_pair": "MAD/EUR",
  "training_days": 730,
  "validation_split": 0.2
}
```

**Response (200 OK)** :
```json
{
  "signal": "MODEL_TRAINING_COMPLETE",
  "metrics": {
    "loss": 0.0012,
    "val_loss": 0.0015,
    "mae": 0.03,
    "training_time_seconds": 45,
    "epochs": 100
  },
  "model_path": "/app/assets/models/exchange_rates/MAD_EUR_model.h5"
}
```

**Training Pipeline** :
1. Fetch historical data (730 days)
2. Normalize (MinMaxScaler)
3. Create sequences (30 days → 7 days)
4. Train LSTM (2 layers, 50 units, Adam optimizer)
5. Validate on 20% holdout
6. Save model (.h5 format)

---

### 21. Generate Predictions (Admin)

**Endpoint** : `POST /api/v1/exchange-rates/admin/generate-predictions`
**Auth** : Admin only
**Description** : Génère et stocke les prédictions pour les 7 prochains jours.

**Request Body** :
```json
{
  "currency_pair": "MAD/EUR"
}
```

**Response (200 OK)** :
```json
{
  "signal": "PREDICTIONS_GENERATED",
  "predictions_count": 7,
  "currency_pair": "MAD/EUR",
  "start_date": "2025-12-05",
  "end_date": "2025-12-11"
}
```

---

### 22. Fetch Rates Now (Admin)

**Endpoint** : `POST /api/v1/exchange-rates/admin/fetch-now`
**Auth** : Admin only
**Description** : Force la récupération immédiate des taux depuis l'API BAM.

**Response (200 OK)** :
```json
{
  "signal": "RATES_FETCHED",
  "success_count": 2,
  "currencies": ["MAD/EUR", "MAD/USD"],
  "date": "2025-12-04"
}
```

**Scheduler** :
- Auto-fetch quotidien : Tous les jours à 9h00 (APScheduler)
- Source : API Bank Al-Maghrib (BAM)

---

### 23. Get Model Info (Admin)

**Endpoint** : `GET /api/v1/exchange-rates/admin/model-info`
**Auth** : Admin only
**Description** : Récupère les métadonnées des modèles ML.

**Response (200 OK)** :
```json
{
  "models": [
    {
      "currency_pair": "MAD/EUR",
      "file_path": "/app/assets/models/exchange_rates/MAD_EUR_model.h5",
      "last_trained": "2025-11-28T14:30:00",
      "training_samples": 2100,
      "architecture": "LSTM(50) → LSTM(50) → Dense(7)"
    }
  ]
}
```

---

## Admin

### 24-36. Admin CRUD Endpoints

**Pattern général** : Tous les endpoints admin suivent la même structure.

#### Get Projects

**Endpoint** : `GET /api/v1/admin/projects`
**Auth** : Admin only

**Query Parameters** :
- `page` (int, default: 1)
- `page_size` (int, default: 20, max: 100)

**Response** :
```json
{
  "data": [
    {
      "id": 1,
      "name": "Project Alpha",
      "language": "fr",
      "created_at": "2025-11-01T10:00:00"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "total_pages": 8
}
```

---

#### Get Project by ID

**Endpoint** : `GET /api/v1/admin/projects/{project_id}`
**Auth** : Admin only
**Description** : Récupère les détails d'un projet spécifique.

**Response (200 OK)** :
```json
{
  "signal": "PROJECT_RETRIEVED",
  "project": {
    "project_id": 1,
    "project_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "project_name": "Project Alpha",
    "project_language": "fr",
    "created_at": "2025-11-01T10:00:00",
    "updated_at": "2025-12-01T14:30:00"
  }
}
```

---

#### Delete Project

**Endpoint** : `DELETE /api/v1/admin/projects/{project_id}`
**Auth** : Admin only

**Response** :
```json
{
  "message": "Project deleted successfully",
  "id": 1
}
```

**⚠️ Cascade** : Supprime assets, chunks, vectors, conversations, messages associés

---

#### Update Project Name

**Endpoint** : `PATCH /api/v1/admin/projects/{project_id}/name`
**Auth** : Admin only
**Description** : Modifie le nom d'un projet.

**Request Body** :
```json
{
  "project_name": "Nouveau nom du projet"
}
```

**Response (200 OK)** :
```json
{
  "signal": "PROJECT_NAME_UPDATED",
  "project": {
    "project_id": 1,
    "project_name": "Nouveau nom du projet",
    "project_language": "fr",
    "updated_at": "2025-12-06T23:45:00"
  }
}
```

**Errors** :
- `400 Bad Request` : project_name manquant
- `404 Not Found` : Projet inexistant

---

### Admin Endpoints Complets

| # | Endpoint | Method | Description |
|---|----------|--------|-------------|
| 24 | `/admin/projects` | GET | Liste projets (pagination) |
| 25 | `/admin/projects/{id}` | GET | Récupère un projet par ID |
| 26 | `/admin/projects/{id}` | DELETE | Supprime projet (cascade) |
| 27 | `/admin/projects/{id}/name` | PATCH | Modifie le nom d'un projet |
| 28 | `/admin/assets` | GET | Liste assets (filtres: project_id, type) |
| 29 | `/admin/assets/{id}` | DELETE | Supprime asset + fichier |
| 30 | `/admin/chunks` | GET | Liste chunks (filtres: project_id, asset_id) |
| 31 | `/admin/chunks/{id}` | DELETE | Supprime chunk |
| 32 | `/admin/conversations` | GET | Liste conversations (filtre: project_id) |
| 33 | `/admin/conversations/{id}` | DELETE | Supprime conversation + messages |
| 34 | `/admin/messages` | GET | Liste messages (filtre: conversation_id) |
| 35 | `/admin/messages/{id}` | DELETE | Supprime message |
| 36 | `/admin/vectors/collections` | GET | Liste toutes les collections Qdrant |
| 37 | `/admin/vectors/collections/{collection_name}` | GET | Stats d'une collection Qdrant |
| 38 | `/admin/vectors/collections/{collection_name}` | DELETE | Supprime une collection Qdrant |

**Filtres communs** :
- `page` (int) : Numéro de page
- `page_size` (int) : Taille de page (max 100)
- `project_id` (int) : Filtrer par projet
- `asset_id` (int) : Filtrer par asset
- `conversation_id` (int) : Filtrer par conversation

---

## Monitoring

### 37. Prometheus Metrics

**Endpoint** : `GET /TrhBVe_m5gg2002_E5VVqS`
**Auth** : Public (obscured URL for security)
**Description** : Endpoint Prometheus pour monitoring (format OpenMetrics).

**Response (text/plain)** :
```
# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1",method="GET",path="/api/v1/auth/me"} 245
http_request_duration_seconds_bucket{le="0.5",method="GET",path="/api/v1/auth/me"} 250
http_request_duration_seconds_sum{method="GET",path="/api/v1/auth/me"} 12.5

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/api/v1/auth/me",status="200"} 250
```

**Métriques disponibles** :
- `http_request_duration_seconds` : Latence des requêtes
- `http_requests_total` : Nombre total de requêtes
- `http_requests_in_progress` : Requêtes en cours

**Grafana Dashboard** : http://localhost:3000

---

## Codes d'erreur

### Codes HTTP Standards

| Code | Description | Exemples |
|------|-------------|----------|
| **200** | OK | Requête réussie |
| **400** | Bad Request | Paramètres invalides, validation échouée |
| **401** | Unauthorized | Token manquant ou invalide |
| **403** | Forbidden | Pas les permissions (besoin admin) |
| **404** | Not Found | Ressource inexistante |
| **413** | Payload Too Large | Fichier > 100MB |
| **422** | Unprocessable Entity | Erreur validation Pydantic |
| **500** | Internal Server Error | Erreur serveur |

### Response Signals Personnalisés

**Authentication** :
- `REGISTRATION_SUCCESS`
- `LOGIN_SUCCESS`
- `USERNAME_ALREADY_EXISTS`
- `EMAIL_ALREADY_EXISTS`

**Data Management** :
- `FILE_UPLOAD_SUCCESS`
- `FILE_UPLOAD_FAILED`
- `FILE_TOO_LARGE`
- `FILE_TYPE_NOT_ALLOWED`
- `PROCESSING_SUCCESS`
- `PROCESSING_ERROR`

**NLP/RAG** :
- `INSERT_INTO_VECTORDB_SUCCESS`
- `INSERT_INTO_VECTORDB_ERROR`
- `SEARCH_SUCCESS`
- `ANSWER_SUCCESS`
- `PROJECT_NOT_FOUND_ERROR`
- `VECTORDB_COLLECTION_RETRIEVED`

**Exchange Rates** :
- `LATEST_RATES_RETRIEVED`
- `PREDICTIONS_RETRIEVED`
- `HISTORY_RETRIEVED`
- `MODEL_TRAINING_COMPLETE`
- `PREDICTIONS_GENERATED`

**Structure erreur standard** :
```json
{
  "detail": "Error message here",
  "signal": "ERROR_SIGNAL_NAME"
}
```

---

## Exemples d'Utilisation

### Exemple 1 : Workflow RAG Complet

```bash
# 1. Register + Login
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!","email":"admin@test.com"}'

TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}' | jq -r '.access_token')

# 2. Upload PDF
curl -X POST http://localhost:8000/api/v1/data/upload/1?language=fr \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@rapport_annuel.pdf"

# 3. Process
curl -X POST http://localhost:8000/api/v1/data/process/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"chunk_size":1000,"overlap_size":200,"do_reset":false}'

# 4. Index
curl -X POST http://localhost:8000/api/v1/nlp/index/push/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"batch_size":50,"do_reset":false}'

# 5. Ask Question
curl -X POST http://localhost:8000/api/v1/nlp/index/answer/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"Quel est le chiffre d affaires?","limit":10}'
```

### Exemple 2 : Conversation avec Historique

```bash
# 1. Create conversation
CONV_ID=$(curl -X POST http://localhost:8000/api/v1/conversations/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"project_id":1,"title":"Questions Finance"}' | jq -r '.conversation_id')

# 2. Ask question 1
curl -X POST http://localhost:8000/api/v1/nlp/index/answer/1 \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\":\"Quel est le CA Q2?\",\"conversation_id\":$CONV_ID}"

# 3. Ask question 2 (avec contexte Q1)
curl -X POST http://localhost:8000/api/v1/nlp/index/answer/1 \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"text\":\"Et comparé au Q1?\",\"conversation_id\":$CONV_ID}"

# 4. Get full history
curl -X GET "http://localhost:8000/api/v1/conversations/$CONV_ID/messages" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Performance & Limites

### Rate Limiting (Recommandé)

| Endpoint | Limite recommandée |
|----------|-------------------|
| `/auth/login` | 5 requêtes/minute |
| `/auth/register` | 3 requêtes/heure |
| `/nlp/index/answer` | 20 requêtes/minute |
| `/data/upload` | 10 requêtes/heure |
| Autres endpoints | Pas de limite |

### Timeouts

| Opération | Timeout |
|-----------|---------|
| Upload fichier | 5 minutes |
| Process documents | 10 minutes |
| Indexation | 15 minutes |
| RAG answer | 30 secondes |
| ML training | 30 minutes |

### Limites de Taille

| Resource | Limite |
|----------|--------|
| Fichier upload | 100 MB |
| Request body | 10 MB |
| Query string | 8 KB |
| Chunk size | 10,000 caractères |
| Conversations par user | Illimité |
| Messages par conversation | Illimité |

---

## Changelog API

### Version 1.0 (Décembre 2025)
- ✅ 39 endpoints documentés
- ✅ Authentication JWT (24h expiration)
- ✅ RAG pipeline complet (Qdrant + Ollama)
- ✅ Exchange Rates ML (LSTM predictions)
- ✅ Admin CRUD (7 entities + gestion projets)
- ✅ Conversations with history
- ✅ Prometheus monitoring
- ✅ Project management (name, language)

---

**Documentation générée** : Décembre 2025
**Version API** : 1.0
**Base URL Dev** : http://localhost:8000
**Swagger UI** : http://localhost:8000/docs
**ReDoc** : http://localhost:8000/redoc

Pour toute question : Consulter [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
