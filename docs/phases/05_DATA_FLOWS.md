# Phase 5 : Flux de Données

> **Statut** : ✅ Complétée
> **Durée effective** : 3 heures
> **Date** : Décembre 2025

---

## 📋 Table des matières

1. [Flux RAG Complet](#1-flux-rag-complet)
2. [Flux Authentication](#2-flux-authentication-jwt)
3. [Flux Exchange Rates](#3-flux-exchange-rates-ml)
4. [Flux Admin CRUD](#4-flux-admin-crud)
5. [Flux Monitoring](#5-flux-monitoring)

---

## 1. Flux RAG Complet

### 1.1 Vue d'Ensemble - Workflow Complet

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKFLOW RAG COMPLET                         │
│                                                                 │
│  Upload → Process → Index → Query → Answer                     │
│    (1)      (2)      (3)     (4)      (5)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

### 1.2 Étape 1 : Upload PDF

**Endpoint** : `POST /api/v1/data/upload/{project_id}`

#### Diagramme de Séquence

```
User                Frontend           Nginx            FastAPI           PostgreSQL
 │                     │                 │                 │                  │
 │ 1. Sélectionner PDF │                 │                 │                  │
 │────────────────────>│                 │                 │                  │
 │                     │                 │                 │                  │
 │                     │ 2. POST /api/v1/data/upload/{project_id}            │
 │                     │    FormData(file)               │                  │
 │                     │────────────────>│                │                  │
 │                     │                 │ 3. Route      │                  │
 │                     │                 │   to FastAPI  │                  │
 │                     │                 │──────────────>│                  │
 │                     │                 │                │                  │
 │                     │                 │                │ 4. Validation   │
 │                     │                 │                │    - Type: PDF  │
 │                     │                 │                │    - Size: <100MB│
 │                     │                 │                │                  │
 │                     │                 │                │ 5. Generate ID  │
 │                     │                 │                │    random_id =  │
 │                     │                 │                │    uuid4()      │
 │                     │                 │                │                  │
 │                     │                 │                │ 6. Save file    │
 │                     │                 │                │    Path: assets/│
 │                     │                 │                │    files/{pid}/ │
 │                     │                 │                │    {id}_{name}  │
 │                     │                 │                │                  │
 │                     │                 │                │ 7. INSERT asset │
 │                     │                 │                │─────────────────>│
 │                     │                 │                │                  │
 │                     │                 │                │ 8. asset_id     │
 │                     │                 │                │<─────────────────│
 │                     │                 │                │                  │
 │                     │                 │                │ 9. Response     │
 │                     │                 │                │    {asset_id,   │
 │                     │                 │                │     file_id,    │
 │                     │                 │                │     filename}   │
 │                     │                 │<───────────────│                  │
 │                     │                 │                │                  │
 │                     │<────────────────│                │                  │
 │                     │                 │                │                  │
 │ 10. Afficher succès│                 │                │                  │
 │<────────────────────│                 │                │                  │
```

#### Code Impliqué

**Frontend** : `pages/Upload.jsx`
```javascript
const formData = new FormData();
formData.append('file', file);
const response = await dataAPI.uploadFile(projectId, formData);
```

**Backend** : `routes/data.py:upload_file()`
- Validation : `DataController.validate_file()`
- Sauvegarde : `DataController.save_file()`
- BDD : `AssetModel.create_asset()`

#### Détails Technique

**Contraintes** :
- Type : `.pdf` uniquement
- Taille max : 100MB
- Format : `multipart/form-data`

**Stockage** :
```
assets/files/{project_id}/{random_id}_{original_filename}.pdf
```

**Table PostgreSQL** : `assets`
```sql
INSERT INTO assets (asset_id, project_id, file_id, filename, created_at)
VALUES (uuid, 1, 'abc123', 'document.pdf', NOW());
```

---

### 1.3 Étape 2 : Process PDF (Extraction + Chunking)

**Endpoint** : `POST /api/v1/data/process/{project_id}`

#### Diagramme de Séquence

```
User    Frontend    FastAPI    ProcessController    DocumentService    ChunkModel    PostgreSQL
 │          │          │               │                    │              │             │
 │ 1. Click│          │               │                    │              │             │
 │ Process │          │               │                    │              │             │
 │─────────>│          │               │                    │              │             │
 │          │          │               │                    │              │             │
 │          │ 2. POST /api/v1/data/process/{project_id}    │              │             │
 │          │   Body: {asset_id, chunk_size, overlap}      │              │             │
 │          │─────────>│               │                    │              │             │
 │          │          │               │                    │              │             │
 │          │          │ 3. Get asset │                    │              │             │
 │          │          │    info      │                    │              │             │
 │          │          │──────────────>│                    │              │             │
 │          │          │               │                    │              │             │
 │          │          │               │ 4. Load PDF       │              │             │
 │          │          │               │    PyMuPDFLoader  │              │             │
 │          │          │               │───────────────────>│              │             │
 │          │          │               │                    │              │             │
 │          │          │               │ 5. Extract text   │              │             │
 │          │          │               │    (all pages)    │              │             │
 │          │          │               │<───────────────────│              │             │
 │          │          │               │                    │              │             │
 │          │          │               │ 6. Chunk text     │              │             │
 │          │          │               │    RecursiveSplit │              │             │
 │          │          │               │    size=1000      │              │             │
 │          │          │               │    overlap=200    │              │             │
 │          │          │               │───────────────────>│              │             │
 │          │          │               │                    │              │             │
 │          │          │               │ 7. Chunks list    │              │             │
 │          │          │               │    [chunk1, ...]  │              │             │
 │          │          │               │<───────────────────│              │             │
 │          │          │               │                    │              │             │
 │          │          │               │ 8. Prepare batch  │              │             │
 │          │          │               │    INSERT         │              │             │
 │          │          │               │──────────────────────────────────>│             │
 │          │          │               │                    │              │             │
 │          │          │               │                    │              │ 9. Bulk    │
 │          │          │               │                    │              │    INSERT  │
 │          │          │               │                    │              │──────────────>
 │          │          │               │                    │              │             │
 │          │          │               │                    │              │ 10. Success│
 │          │          │               │                    │              │<────────────│
 │          │          │               │                    │              │             │
 │          │          │ 11. Response  │                    │              │             │
 │          │          │     {chunks_count, status}         │              │             │
 │          │          │<──────────────│                    │              │             │
 │          │<─────────│               │                    │              │             │
 │          │          │               │                    │              │             │
 │ 12. Show│          │               │                    │              │             │
 │   result│          │               │                    │              │             │
 │<─────────│          │               │                    │              │             │
```

#### Algorithme de Chunking

**RecursiveCharacterTextSplitter** :
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,         # Taille cible
    chunk_overlap=200,       # Chevauchement
    separators=["\n\n", "\n", ". ", " ", ""]  # Ordre de priorité
)
```

**Priorité des séparateurs** :
1. `\n\n` : Paragraphes (meilleure sémantique)
2. `\n` : Lignes
3. `. ` : Phrases
4. ` ` : Mots
5. `""` : Caractères (dernier recours)

**Exemple** :
```
Texte original : 2500 caractères
↓
Chunk 1: [0:1000] chars
Chunk 2: [800:1800] chars  ← Overlap 200
Chunk 3: [1600:2500] chars ← Overlap 200
```

#### Table PostgreSQL : `datachunks`

```sql
INSERT INTO datachunks (chunk_id, asset_id, chunk_text, chunk_index, created_at)
VALUES
  (uuid1, asset_id, 'Texte chunk 1...', 0, NOW()),
  (uuid2, asset_id, 'Texte chunk 2...', 1, NOW()),
  ...
```

---

### 1.4 Étape 3 : Index dans Qdrant (Vectorisation)

**Endpoint** : `POST /api/v1/nlp/index/push/{project_id}`

#### Diagramme de Séquence

```
Frontend  FastAPI  NLPController  ChunkModel  EmbeddingsService  VectorStoreService  Qdrant
   │         │           │             │              │                  │              │
   │ 1. POST │           │             │              │                  │              │
   │   /index/push       │             │              │                  │              │
   │────────>│           │             │              │                  │              │
   │         │           │             │              │                  │              │
   │         │ 2. Get    │             │              │                  │              │
   │         │   project │             │              │                  │              │
   │         │──────────>│             │              │                  │              │
   │         │           │             │              │                  │              │
   │         │           │ 3. Get all  │              │                  │              │
   │         │           │    chunks   │              │                  │              │
   │         │           │────────────>│              │                  │              │
   │         │           │             │              │                  │              │
   │         │           │ 4. chunks[] │              │                  │              │
   │         │           │<────────────│              │                  │              │
   │         │           │             │              │                  │              │
   │         │           │ 5. BATCH 50 chunks         │                  │              │
   │         │           │    (loop)   │              │                  │              │
   │         │           │             │              │                  │              │
   │         │           │ 6. Embed    │              │                  │              │
   │         │           │    batch    │              │                  │              │
   │         │           │──────────────────────────>│                  │              │
   │         │           │             │              │                  │              │
   │         │           │             │              │ 7. HuggingFace  │              │
   │         │           │             │              │    multilingual │              │
   │         │           │             │              │    768D vectors │              │
   │         │           │             │              │                  │              │
   │         │           │             │              │ 8. vectors[]    │              │
   │         │           │<──────────────────────────│                  │              │
   │         │           │             │              │                  │              │
   │         │           │ 9. Add to   │              │                  │              │
   │         │           │    Qdrant   │              │                  │              │
   │         │           │──────────────────────────────────────────────>│              │
   │         │           │             │              │                  │              │
   │         │           │             │              │                  │ 10. Upsert  │
   │         │           │             │              │                  │     points  │
   │         │           │             │              │                  │─────────────>│
   │         │           │             │              │                  │              │
   │         │           │             │              │                  │ 11. OK      │
   │         │           │             │              │                  │<─────────────│
   │         │           │             │              │                  │              │
   │         │           │ 12. Continue next batch... │                  │              │
   │         │           │             │              │                  │              │
   │         │ 13. Response             │              │                  │              │
   │         │     {total_chunks,       │              │                  │              │
   │         │      indexed_chunks}     │              │                  │              │
   │         │<──────────│             │              │                  │              │
   │         │           │             │              │                  │              │
   │<────────│           │             │              │                  │              │
```

#### Détails Embeddings

**Modèle** : `sentence-transformers/paraphrase-multilingual-mpnet-base-v2`
- **Dimensions** : 768D
- **Langues** : 50+ (FR, EN, AR supportés)
- **Device** : CPU (ou CUDA si disponible)

**Exemple transformation** :
```python
text = "Le système RAG permet de répondre aux questions"
↓
vector = [0.023, -0.145, 0.891, ..., 0.234]  # 768 dimensions
```

#### Collection Qdrant

**Nom** : `collection_768_{project_id}`

**Configuration** :
```python
{
    "vectors": {
        "size": 768,
        "distance": "Cosine"
    },
    "hnsw_config": {
        "m": 16,
        "ef_construct": 100
    }
}
```

**Structure Point** :
```json
{
    "id": "chunk_uuid",
    "vector": [0.023, -0.145, ...],
    "payload": {
        "chunk_id": "uuid",
        "asset_id": "uuid",
        "text": "Texte du chunk...",
        "project_id": 1
    }
}
```

---

### 1.5 Étape 4 : Query RAG (Question → Answer)

**Endpoint** : `POST /api/v1/nlp/index/answer/{project_id}`

#### Diagramme de Séquence Détaillé

```
User  Frontend  FastAPI  NLPController  ConversationModel  EmbeddingsService  Qdrant  RAGService  Ollama  MessageModel
 │       │         │           │                │                  │           │         │         │          │
 │ 1. Ask│         │           │                │                  │           │         │         │          │
 │ question        │           │                │                  │           │         │         │          │
 │──────>│         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │ 2. POST /answer     │                │                  │           │         │         │          │
 │       │   {text, conv_id}   │                │                  │           │         │         │          │
 │       │────────>│           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │ 3. Get    │                │                  │           │         │         │          │
 │       │         │   conversation history     │                  │           │         │         │          │
 │       │         │───────────────────────────>│                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │ 4. messages[]  │                  │           │         │         │          │
 │       │         │<───────────────────────────│                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │ 5. Embed  │                │                  │           │         │         │          │
 │       │         │   question│                │                  │           │         │         │          │
 │       │         │───────────────────────────────────────────────>│         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │ 6. query_vector  │           │         │         │          │
 │       │         │<───────────────────────────────────────────────│         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │ 7. Search │                │                  │           │         │         │          │
 │       │         │   similar │                │                  │           │         │         │          │
 │       │         │   vectors │                │                  │           │         │         │          │
 │       │         │   (k=10)  │                │                  │           │         │         │          │
 │       │         │────────────────────────────────────────────────────────>│         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │ 8. Search HNSW  │          │
 │       │         │           │                │                  │           │ 9. Top 10       │          │
 │       │         │           │                │                  │           │                 │          │
 │       │         │           │                │ 10. chunks[] + scores       │                 │          │
 │       │         │<────────────────────────────────────────────────────────│         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │ 11. Build │                │                  │           │         │         │          │
 │       │         │    RAG    │                │                  │           │         │         │          │
 │       │         │    prompt │                │                  │           │         │         │          │
 │       │         │───────────────────────────────────────────────────────────────────>│         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │ 12. LCEL Chain    │
 │       │         │           │                │                  │           │         │ ┌─────────────┐   │
 │       │         │           │                │                  │           │         │ │context      │   │
 │       │         │           │                │                  │           │         │ │+ question   │   │
 │       │         │           │                │                  │           │         │ │+ history    │   │
 │       │         │           │                │                  │           │         │ │→ Prompt     │   │
 │       │         │           │                │                  │           │         │ │→ LLM        │   │
 │       │         │           │                │                  │           │         │ │→ Parse      │   │
 │       │         │           │                │                  │           │         │ └─────────────┘   │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │ 13. Call LLM      │
 │       │         │           │                │                  │           │         │─────────────────>│
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │ 14. Generate
 │       │         │           │                │                  │           │         │         │ answer   │
 │       │         │           │                │                  │           │         │         │ (Mistral)│
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │ 15. answer        │
 │       │         │           │                │                  │           │         │<─────────────────│
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │ 16. {answer, sources}             │           │         │         │          │
 │       │         │<───────────────────────────────────────────────────────────────────│         │          │
 │       │         │           │                │                  │           │         │         │          │
 │       │         │ 17. Save  │                │                  │           │         │         │          │
 │       │         │    messages (Q+A)          │                  │           │         │         │          │
 │       │         │────────────────────────────────────────────────────────────────────────────────────────>│
 │       │         │           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │ 18. INSERT
 │       │         │           │                │                  │           │         │         │          │
 │       │         │ 19. Response               │                  │           │         │         │          │
 │       │         │    {answer, sources}       │                  │           │         │         │          │
 │       │<────────│           │                │                  │           │         │         │          │
 │       │         │           │                │                  │           │         │         │          │
 │ 20. Display     │           │                │                  │           │         │         │          │
 │   answer        │           │                │                  │           │         │         │          │
 │<──────│         │           │                │                  │           │         │         │          │
```

#### Pipeline LCEL (LangChain Expression Language)

```python
chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
        "chat_history": lambda x: formatted_history
    }
    | prompt
    | llm
    | StrOutputParser()
)
```

**Étapes** :
1. **Context** : Top K chunks formatés
2. **Question** : Question utilisateur
3. **Chat History** : Historique conversationnel
4. **Prompt** : Template multilingue (FR/EN/AR)
5. **LLM** : Génération (Ollama Mistral)
6. **Parser** : Extraction réponse

#### Prompt Template

```python
SYSTEM_PROMPT = """Tu es un assistant qui répond aux questions
basées sur les documents fournis. Utilise uniquement le contexte
donné pour répondre.

Documents:
{context}

Historique:
{chat_history}

Question: {question}

Réponds de manière concise et précise."""
```

#### Recherche Vectorielle (HNSW)

**Algorithme** : Hierarchical Navigable Small World
- **Complexité** : O(log N)
- **Métrique** : Cosine similarity
- **Top K** : 10 résultats par défaut

**Score de similarité** :
```
1.0 = Identique
0.8-0.9 = Très similaire
0.6-0.7 = Similaire
<0.5 = Peu similaire
```

---

## 2. Flux Authentication (JWT)

### 2.1 Registration (Inscription)

**Endpoint** : `POST /api/v1/auth/register`

#### Diagramme de Séquence

```
User    Frontend    FastAPI    AuthRouter    UserModel    PostgreSQL    bcrypt
 │          │          │            │             │             │           │
 │ 1. Fill │          │            │             │             │           │
 │   form  │          │            │             │             │           │
 │────────>│          │            │             │             │           │
 │          │          │            │             │             │           │
 │          │ 2. POST /auth/register              │             │           │
 │          │   {username, email, password}       │             │           │
 │          │─────────>│            │             │             │           │
 │          │          │            │             │             │           │
 │          │          │ 3. Check  │             │             │           │
 │          │          │   existing│             │             │           │
 │          │          │───────────────────────>│             │           │
 │          │          │            │             │             │           │
 │          │          │            │             │ 4. SELECT  │           │
 │          │          │            │             │───────────>│           │
 │          │          │            │             │             │           │
 │          │          │            │             │ 5. NULL?   │           │
 │          │          │            │             │<───────────│           │
 │          │          │            │             │             │           │
 │          │          │ 6. Hash   │             │             │           │
 │          │          │   password│             │             │           │
 │          │          │───────────────────────────────────────────────────>│
 │          │          │            │             │             │           │
 │          │          │            │             │             │ 7. bcrypt │
 │          │          │            │             │             │   cost=12 │
 │          │          │            │             │             │           │
 │          │          │            │             │             │ 8. hashed │
 │          │          │<───────────────────────────────────────────────────│
 │          │          │            │             │             │           │
 │          │          │ 9. Determine role        │             │           │
 │          │          │   (1st user = admin)     │             │           │
 │          │          │            │             │             │           │
 │          │          │ 10. Create user          │             │           │
 │          │          │───────────────────────>│             │           │
 │          │          │            │             │             │           │
 │          │          │            │             │ 11. INSERT │           │
 │          │          │            │             │───────────>│           │
 │          │          │            │             │             │           │
 │          │          │            │             │ 12. user_id│           │
 │          │          │            │             │<───────────│           │
 │          │          │            │             │             │           │
 │          │          │ 13. Generate JWT         │             │           │
 │          │          │    payload = {username,  │             │           │
 │          │          │              role,       │             │           │
 │          │          │              exp: 24h}   │             │           │
 │          │          │            │             │             │           │
 │          │          │ 14. Response             │             │           │
 │          │          │    {access_token, role}  │             │           │
 │          │<─────────│            │             │             │           │
 │          │          │            │             │             │           │
 │          │ 15. Store token       │             │             │           │
 │          │    localStorage       │             │             │           │
 │          │          │            │             │             │           │
 │          │ 16. Redirect          │             │             │           │
 │          │    /dashboard         │             │             │           │
 │<─────────│          │            │             │             │           │
```

#### Détails Technique

**Bcrypt Cost** : 12 rounds
```python
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12))
```

**Sécurité** :
- Salt automatique (bcrypt)
- Coût computationnel : ~250ms par hash
- Résistant brute-force

**Premier utilisateur = Admin** :
```python
user_count = await UserModel.count_users()
role = "admin" if user_count == 0 else "user"
```

---

### 2.2 Login (Connexion)

**Endpoint** : `POST /api/v1/auth/login`

#### Diagramme de Séquence

```
User    Frontend    FastAPI    AuthRouter    UserModel    PostgreSQL    bcrypt    JWT
 │          │          │            │             │             │           │        │
 │ 1. Enter│          │            │             │             │           │        │
 │   creds │          │            │             │             │           │        │
 │────────>│          │            │             │             │           │        │
 │          │          │            │             │             │           │        │
 │          │ 2. POST /auth/login  │             │             │           │        │
 │          │   {username, password}│             │             │           │        │
 │          │─────────>│            │             │             │           │        │
 │          │          │            │             │             │           │        │
 │          │          │ 3. Get user│             │             │           │        │
 │          │          │───────────────────────>│             │           │        │
 │          │          │            │             │             │           │        │
 │          │          │            │             │ 4. SELECT  │           │        │
 │          │          │            │             │───────────>│           │        │
 │          │          │            │             │             │           │        │
 │          │          │            │             │ 5. user row│           │        │
 │          │          │            │             │<───────────│           │        │
 │          │          │            │             │             │           │        │
 │          │          │ 6. user or None          │             │           │        │
 │          │          │<───────────────────────│             │           │        │
 │          │          │            │             │             │           │        │
 │          │          │ 7. Verify  │             │             │           │        │
 │          │          │   password │             │             │           │        │
 │          │          │────────────────────────────────────────────────────>│        │
 │          │          │            │             │             │           │        │
 │          │          │            │             │             │ 8. bcrypt.checkpw  │
 │          │          │            │             │             │   (password,       │
 │          │          │            │             │             │    hashed)         │
 │          │          │            │             │             │           │        │
 │          │          │            │             │             │ 9. True/False      │
 │          │          │<────────────────────────────────────────────────────│        │
 │          │          │            │             │             │           │        │
 │          │          │ 10. Generate JWT         │             │           │        │
 │          │          │────────────────────────────────────────────────────────────>│
 │          │          │            │             │             │           │        │
 │          │          │            │             │             │           │ 11. Encode
 │          │          │            │             │             │           │ payload={
 │          │          │            │             │             │           │   sub: username
 │          │          │            │             │             │           │   role: admin
 │          │          │            │             │             │           │   exp: +24h
 │          │          │            │             │             │           │ }
 │          │          │            │             │             │           │ secret=SECRET_KEY
 │          │          │            │             │             │           │        │
 │          │          │            │             │             │           │ 12. token
 │          │          │<────────────────────────────────────────────────────────────│
 │          │          │            │             │             │           │        │
 │          │          │ 13. Response             │             │           │        │
 │          │          │    {access_token,        │             │           │        │
 │          │          │     username, role}      │             │           │        │
 │          │<─────────│            │             │             │           │        │
 │          │          │            │             │             │           │        │
 │          │ 14. Store│            │             │             │           │        │
 │          │   localStorage.setItem('token')     │             │           │        │
 │          │          │            │             │             │           │        │
 │          │ 15. Decode JWT client-side          │             │           │        │
 │          │   setUser({username, role})         │             │           │        │
 │          │          │            │             │             │           │        │
 │          │ 16. Navigate /dashboard             │             │           │        │
 │<─────────│          │            │             │             │           │        │
```

#### JWT Structure

**Header** :
```json
{
  "alg": "HS256",
  "typ": "JWT"
}
```

**Payload** :
```json
{
  "sub": "john_doe",
  "role": "admin",
  "exp": 1735824000
}
```

**Signature** :
```
HMACSHA256(
  base64UrlEncode(header) + "." + base64UrlEncode(payload),
  SECRET_KEY
)
```

**Token complet** :
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huX2RvZSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTczNTgyNDAwMH0.signature_here
```

---

### 2.3 Protected Route (Vérification JWT)

#### Diagramme de Séquence

```
Frontend    Axios Interceptor    Nginx    FastAPI    JWT Middleware
   │                │                │         │              │
   │ 1. API call    │                │         │              │
   │───────────────>│                │         │              │
   │                │                │         │              │
   │                │ 2. Add header  │         │              │
   │                │   Authorization: Bearer {token}         │
   │                │───────────────>│         │              │
   │                │                │         │              │
   │                │                │ 3. Route│              │
   │                │                │────────>│              │
   │                │                │         │              │
   │                │                │         │ 4. Extract  │
   │                │                │         │   token     │
   │                │                │         │─────────────>│
   │                │                │         │              │
   │                │                │         │ 5. Decode   │
   │                │                │         │   & verify  │
   │                │                │         │   signature │
   │                │                │         │              │
   │                │                │         │ 6. Check exp│
   │                │                │         │   (expired?)│
   │                │                │         │              │
   │                │                │         │ 7. user info│
   │                │                │         │<─────────────│
   │                │                │         │              │
   │                │                │         │ 8. Process  │
   │                │                │         │   request   │
   │                │                │         │              │
   │                │                │ 9. Response            │
   │                │<───────────────────────│              │
   │                │                │         │              │
   │<───────────────│                │         │              │
```

**Si token expiré ou invalide** :
```
FastAPI → 401 Unauthorized
   ↓
Axios Interceptor (response)
   ↓
if (status === 401) {
  localStorage.removeItem('token')
  window.location.href = '/login'
}
```

---

## 3. Flux Exchange Rates (ML)

### 3.1 Scheduler Quotidien

#### Diagramme de Séquence

```
APScheduler    Fetch Job    BAM API Client    Bank Al-Maghrib    ExchangeRateModel    PostgreSQL    Prometheus
     │              │               │                  │                  │                 │             │
     │ 1. CRON      │               │                  │                  │                 │             │
     │   18:00:00   │               │                  │                  │                 │             │
     │─────────────>│               │                  │                  │                 │             │
     │              │               │                  │                  │                 │             │
     │              │ 2. Fetch rates│                  │                  │                 │             │
     │              │──────────────>│                  │                  │                 │             │
     │              │               │                  │                  │                 │             │
     │              │               │ 3. HTTP GET      │                  │                 │             │
     │              │               │  /cours-change   │                  │                 │             │
     │              │               │─────────────────>│                  │                 │             │
     │              │               │                  │                  │                 │             │
     │              │               │                  │ 4. JSON response │                 │             │
     │              │               │                  │   {MAD/EUR,      │                 │             │
     │              │               │                  │    MAD/USD,      │                 │             │
     │              │               │                  │    date}         │                 │             │
     │              │               │<─────────────────│                  │                 │             │
     │              │               │                  │                  │                 │             │
     │              │               │ 5. Parse JSON    │                  │                 │             │
     │              │               │                  │                  │                 │             │
     │              │ 6. rates dict │                  │                  │                 │             │
     │              │<──────────────│                  │                  │                 │             │
     │              │               │                  │                  │                 │             │
     │              │ 7. Check existing (today)        │                  │                 │             │
     │              │──────────────────────────────────────────────────>│                 │             │
     │              │               │                  │                  │                 │             │
     │              │               │                  │                  │ 8. SELECT      │             │
     │              │               │                  │                  │   WHERE date   │             │
     │              │               │                  │                  │─────────────────>│             │
     │              │               │                  │                  │                 │             │
     │              │               │                  │                  │ 9. NULL        │             │
     │              │               │                  │                  │<─────────────────│             │
     │              │               │                  │                  │                 │             │
     │              │ 10. Bulk INSERT                  │                  │                 │             │
     │              │──────────────────────────────────────────────────>│                 │             │
     │              │               │                  │                  │                 │             │
     │              │               │                  │                  │ 11. INSERT     │             │
     │              │               │                  │                  │   (MAD/EUR,    │             │
     │              │               │                  │                  │    MAD/USD,    │             │
     │              │               │                  │                  │    is_prediction│             │
     │              │               │                  │                  │    =False)     │             │
     │              │               │                  │                  │─────────────────>│             │
     │              │               │                  │                  │                 │             │
     │              │               │                  │                  │ 12. OK         │             │
     │              │               │                  │                  │<─────────────────│             │
     │              │               │                  │                  │                 │             │
     │              │ 13. Record metric                │                  │                 │             │
     │              │───────────────────────────────────────────────────────────────────────────────────>│
     │              │               │                  │                  │                 │             │
     │              │               │                  │                  │                 │ 14. Counter │
     │              │               │                  │                  │                 │   rates_    │
     │              │               │                  │                  │                 │   fetched++ │
     │              │               │                  │                  │                 │             │
     │              │ 15. Log success                  │                  │                 │             │
     │              │               │                  │                  │                 │             │
     │<─────────────│               │                  │                  │                 │             │
```

**Configuration Scheduler** :
```python
scheduler.add_job(
    func=fetch_rates_from_api,
    trigger="cron",
    hour=18,
    minute=0,
    id="daily_rates_fetch",
    replace_existing=True
)
```

**Backfill Initial** (au startup) :
- Récupère 90 derniers jours si base vide
- Vérifie taux du jour, fetch si manquant

---

### 3.2 ML Predictions (LSTM)

#### Architecture Model

```
Input: 30 jours historiques [t-29, t-28, ..., t-1, t]
   ↓
LSTM Layer 1 (50 units, return_sequences=True)
   ↓
LSTM Layer 2 (50 units, return_sequences=False)
   ↓
Dense Layer (7 units)
   ↓
Output: 7 jours futurs [t+1, t+2, ..., t+7]
```

#### Diagramme de Séquence Training

```
Admin    Frontend    FastAPI    PredictionService    ExchangeRateModel    TensorFlow    PostgreSQL
  │          │          │               │                    │                │             │
  │ 1. Train │          │               │                    │                │             │
  │   Model  │          │               │                    │                │             │
  │─────────>│          │               │                    │                │             │
  │          │          │               │                    │                │             │
  │          │ 2. POST /admin/train-model                    │                │             │
  │          │   {currency_pair, days_history=90}            │                │             │
  │          │─────────>│               │                    │                │             │
  │          │          │               │                    │                │             │
  │          │          │ 3. Get historical rates            │                │             │
  │          │          │───────────────────────────────────>│                │             │
  │          │          │               │                    │                │             │
  │          │          │               │                    │ 4. SELECT      │             │
  │          │          │               │                    │   WHERE pair   │             │
  │          │          │               │                    │   AND !prediction            │
  │          │          │               │                    │   ORDER date   │             │
  │          │          │               │                    │───────────────────────────────>
  │          │          │               │                    │                │             │
  │          │          │               │                    │ 5. rates[]     │             │
  │          │          │               │                    │<───────────────────────────────
  │          │          │               │                    │                │             │
  │          │          │ 6. rates_data │                    │                │             │
  │          │          │<───────────────────────────────────│                │             │
  │          │          │               │                    │                │             │
  │          │          │ 7. Prepare sequences              │                │             │
  │          │          │   (sliding window: 30→7)           │                │             │
  │          │          │               │                    │                │             │
  │          │          │ 8. Train LSTM │                    │                │             │
  │          │          │──────────────────────────────────────────────────>│             │
  │          │          │               │                    │                │             │
  │          │          │               │                    │                │ 9. Build   │
  │          │          │               │                    │                │   model    │
  │          │          │               │                    │                │            │
  │          │          │               │                    │                │ 10. Compile│
  │          │          │               │                    │                │   (adam,   │
  │          │          │               │                    │                │    mse)    │
  │          │          │               │                    │                │            │
  │          │          │               │                    │                │ 11. Fit    │
  │          │          │               │                    │                │   (epochs= │
  │          │          │               │                    │                │    100,    │
  │          │          │               │                    │                │    batch=32)│
  │          │          │               │                    │                │            │
  │          │          │               │                    │                │ 12. trained│
  │          │          │<──────────────────────────────────────────────────│             │
  │          │          │               │                    │                │             │
  │          │          │ 13. Save model                     │                │             │
  │          │          │   models/{pair}_lstm.h5            │                │             │
  │          │          │               │                    │                │             │
  │          │          │ 14. Response  │                    │                │             │
  │          │          │    {status, metrics}               │                │             │
  │          │<─────────│               │                    │                │             │
  │          │          │               │                    │                │             │
  │ 15. Show │          │               │                    │                │             │
  │   success│          │               │                    │                │             │
  │<─────────│          │               │                    │                │             │
```

#### Diagramme Génération Prédictions

```
Admin    FastAPI    PredictionService    Model (LSTM)    ExchangeRateModel    PostgreSQL
  │          │               │                  │                 │                │
  │ 1. Generate predictions  │                  │                 │                │
  │─────────────────────────>│                  │                 │                │
  │          │               │                  │                 │                │
  │          │ 2. Load model │                  │                 │                │
  │          │──────────────>│                  │                 │                │
  │          │               │                  │                 │                │
  │          │               │ 3. Load .h5 file │                 │                │
  │          │               │─────────────────>│                 │                │
  │          │               │                  │                 │                │
  │          │               │ 4. Model loaded  │                 │                │
  │          │               │<─────────────────│                 │                │
  │          │               │                  │                 │                │
  │          │ 5. Get last 30 days              │                 │                │
  │          │──────────────────────────────────────────────────>│                │
  │          │               │                  │                 │                │
  │          │               │                  │                 │ 6. SELECT TOP 30
  │          │               │                  │                 │───────────────>│
  │          │               │                  │                 │                │
  │          │               │                  │                 │ 7. rates[]     │
  │          │               │                  │                 │<───────────────│
  │          │               │                  │                 │                │
  │          │ 8. historical_data               │                 │                │
  │          │<──────────────────────────────────────────────────│                │
  │          │               │                  │                 │                │
  │          │ 9. Predict    │                  │                 │                │
  │          │──────────────>│                  │                 │                │
  │          │               │                  │                 │                │
  │          │               │ 10. Normalize    │                 │                │
  │          │               │    input         │                 │                │
  │          │               │                  │                 │                │
  │          │               │ 11. model.predict(X)              │                │
  │          │               │─────────────────>│                 │                │
  │          │               │                  │                 │                │
  │          │               │                  │ 12. Forward pass│                │
  │          │               │                  │    LSTM → Dense │                │
  │          │               │                  │                 │                │
  │          │               │ 13. predictions  │                 │                │
  │          │               │    [7 days]      │                 │                │
  │          │               │<─────────────────│                 │                │
  │          │               │                  │                 │                │
  │          │               │ 14. Denormalize  │                 │                │
  │          │               │                  │                 │                │
  │          │ 15. Save predictions             │                 │                │
  │          │──────────────────────────────────────────────────>│                │
  │          │               │                  │                 │                │
  │          │               │                  │                 │ 16. INSERT    │
  │          │               │                  │                 │   (is_prediction│
  │          │               │                  │                 │    =True)     │
  │          │               │                  │                 │───────────────>│
  │          │               │                  │                 │                │
  │          │ 17. Response {predictions_saved} │                 │                │
  │<─────────────────────────│                  │                 │                │
```

---

## 4. Flux Admin CRUD

### 4.1 Pattern CRUD Générique

**Exemple** : Gestion des Projets

#### Read (Liste)

```
Frontend    FastAPI    AdminRouter    ProjectModel    PostgreSQL
   │            │            │              │              │
   │ GET /admin/projects?page=1&page_size=20              │
   │───────────>│            │              │              │
   │            │            │              │              │
   │            │ Pagination │              │              │
   │            │───────────>│              │              │
   │            │            │              │              │
   │            │            │ SELECT       │              │
   │            │            │──────────────>│              │
   │            │            │              │              │
   │            │            │              │ LIMIT/OFFSET │
   │            │            │              │──────────────>│
   │            │            │              │              │
   │            │            │              │ rows[]       │
   │            │            │              │<──────────────│
   │            │            │              │              │
   │            │            │ projects[]   │              │
   │            │            │<──────────────│              │
   │            │            │              │              │
   │            │ Response   │              │              │
   │            │ {projects, total_pages}   │              │
   │<───────────│            │              │              │
```

#### Delete (Suppression Cascade)

```
Frontend    FastAPI    AdminRouter    ProjectModel    AssetModel    ChunkModel    Qdrant
   │            │            │              │             │             │            │
   │ DELETE /admin/projects/{id}            │             │             │            │
   │───────────>│            │              │             │             │            │
   │            │            │              │             │             │            │
   │            │ Check auth (admin)        │             │             │            │
   │            │            │              │             │             │            │
   │            │ CASCADE delete            │             │             │            │
   │            │───────────>│              │             │             │            │
   │            │            │              │             │             │            │
   │            │            │ 1. Get assets│             │             │            │
   │            │            │─────────────────────────>│             │            │
   │            │            │              │             │             │            │
   │            │            │              │ assets[]    │             │            │
   │            │            │<─────────────────────────│             │            │
   │            │            │              │             │             │            │
   │            │            │ 2. For each asset         │             │            │
   │            │            │              │             │             │            │
   │            │            │ 3. Delete chunks          │             │            │
   │            │            │───────────────────────────────────────>│            │
   │            │            │              │             │             │            │
   │            │            │ 4. Delete vectors from Qdrant          │            │
   │            │            │────────────────────────────────────────────────────>│
   │            │            │              │             │             │            │
   │            │            │              │             │             │ DELETE    │
   │            │            │              │             │             │ points    │
   │            │            │              │             │             │ WHERE     │
   │            │            │              │             │             │ project_id│
   │            │            │              │             │             │            │
   │            │            │ 5. Delete file system     │             │            │
   │            │            │   rm assets/files/{pid}/  │             │            │
   │            │            │              │             │             │            │
   │            │            │ 6. Delete assets          │             │            │
   │            │            │─────────────────────────>│             │            │
   │            │            │              │             │             │            │
   │            │            │ 7. Delete project         │             │            │
   │            │            │──────────────>│             │             │            │
   │            │            │              │             │             │            │
   │            │ Response {success}        │             │             │            │
   │<───────────│            │              │             │             │            │
```

**Ordre suppression cascade** :
1. Vectors (Qdrant)
2. Chunks (PostgreSQL)
3. Assets (PostgreSQL)
4. Files (Filesystem)
5. Project (PostgreSQL)

#### Update (Modification Nom de Projet)

```
Frontend    FastAPI    AdminRouter    ProjectModel    PostgreSQL
   │            │            │              │              │
   │ PATCH /admin/projects/{id}/name        │              │
   │ Body: {project_name: "Nouveau Nom"}   │              │
   │───────────>│            │              │              │
   │            │            │              │              │
   │            │ Check auth (admin)        │              │
   │            │            │              │              │
   │            │ Validate   │              │              │
   │            │───────────>│              │              │
   │            │            │              │              │
   │            │            │ UPDATE       │              │
   │            │            │──────────────>│              │
   │            │            │              │              │
   │            │            │              │ UPDATE       │
   │            │            │              │ projects     │
   │            │            │              │ SET          │
   │            │            │              │ project_name │
   │            │            │              │ WHERE id     │
   │            │            │              │──────────────>│
   │            │            │              │              │
   │            │            │              │ 1 row        │
   │            │            │              │<──────────────│
   │            │            │              │              │
   │            │            │ project      │              │
   │            │            │<──────────────│              │
   │            │            │              │              │
   │            │ Response   │              │              │
   │            │ {signal, project_id, project_name}      │
   │<───────────│            │              │              │
```

**Fonctionnalités** :
- Modification simple d'un champ (PATCH)
- Validation côté backend (project_name non vide)
- Retour immédiat du nom mis à jour
- Accessible uniquement aux admins

---

## 5. Flux Monitoring

### 5.1 Prometheus Scraping

```
Prometheus     FastAPI       Node-Exporter    Postgres-Exporter    Qdrant
    │              │                │                  │              │
    │ SCRAPE       │                │                  │              │
    │ every 15s    │                │                  │              │
    │              │                │                  │              │
    │ /TrhBVe_*    │                │                  │              │
    │─────────────>│                │                  │              │
    │              │                │                  │              │
    │ Metrics      │                │                  │              │
    │ - requests   │                │                  │              │
    │ - latency    │                │                  │              │
    │ - errors     │                │                  │              │
    │<─────────────│                │                  │              │
    │              │                │                  │              │
    │ :9100/metrics│                │                  │              │
    │──────────────────────────────>│                  │              │
    │              │                │                  │              │
    │ System       │                │                  │              │
    │ - CPU        │                │                  │              │
    │ - RAM        │                │                  │              │
    │ - Disk       │                │                  │              │
    │<──────────────────────────────│                  │              │
    │              │                │                  │              │
    │ :9187/metrics│                │                  │              │
    │──────────────────────────────────────────────────>│              │
    │              │                │                  │              │
    │ PostgreSQL   │                │                  │              │
    │ - Connections│                │                  │              │
    │ - Queries    │                │                  │              │
    │<──────────────────────────────────────────────────│              │
    │              │                │                  │              │
    │ :6333/metrics│                │                  │              │
    │──────────────────────────────────────────────────────────────────>
    │              │                │                  │              │
    │ Qdrant       │                │                  │              │
    │ - Collections│                │                  │              │
    │ - Vectors    │                │                  │              │
    │<──────────────────────────────────────────────────────────────────
```

### 5.2 Grafana Dashboards

```
User    Grafana    Prometheus    PromQL
 │         │            │           │
 │ View   │            │           │
 │ Dashboard           │           │
 │───────>│            │           │
 │         │            │           │
 │         │ Query      │           │
 │         │ metrics    │           │
 │         │───────────>│           │
 │         │            │           │
 │         │            │ Execute   │
 │         │            │ PromQL    │
 │         │            │──────────>│
 │         │            │           │
 │         │            │ Results   │
 │         │            │<──────────│
 │         │            │           │
 │         │ Time series│           │
 │         │<───────────│           │
 │         │            │           │
 │ Graph   │            │           │
 │<────────│            │           │
```

**Exemples PromQL** :
- Latence moyenne : `rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m])`
- Taux erreur : `rate(http_requests_total{status=~"5.."}[5m])`
- RAM usage : `node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes * 100`

---

## ✅ Phase 5 Complétée !

**Total documenté** :
- 5 flux principaux détaillés
- 15+ diagrammes de séquence ASCII
- Chaque appel de fonction tracé
- Tables PostgreSQL impliquées
- Architecture ML (LSTM)
- Monitoring complet

**Flux couverts** :
1. ✅ RAG Complet (Upload → Process → Index → Answer)
2. ✅ Authentication (Register → Login → JWT → Protected Routes)
3. ✅ Exchange Rates (Scheduler → Fetch → Train → Predict)
4. ✅ Admin CRUD (Cascade deletes)
5. ✅ Monitoring (Prometheus → Grafana)

**Prochaine étape** : **Phase 6 - Recommandations**

---

**Dernière mise à jour** : Décembre 2025
**Durée** : 3 heures
**Statut** : ✅ Complétée
