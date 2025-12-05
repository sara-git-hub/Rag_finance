# 🔧 Troubleshooting Guide

> Guide complet de résolution des problèmes courants du projet Fil Rouge
> Dernière mise à jour : Décembre 2025

---

## 📋 Table des matières

1. [Problèmes Docker & Services](#problèmes-docker--services)
2. [Problèmes Base de Données](#problèmes-base-de-données)
3. [Problèmes Backend (FastAPI)](#problèmes-backend-fastapi)
4. [Problèmes Frontend (React)](#problèmes-frontend-react)
5. [Problèmes RAG & NLP](#problèmes-rag--nlp)
6. [Problèmes Exchange Rates & ML](#problèmes-exchange-rates--ml)
7. [Problèmes Authentication](#problèmes-authentication)
8. [Problèmes Monitoring](#problèmes-monitoring)
9. [Commandes de Diagnostic](#commandes-de-diagnostic)

---

## 🐳 Problèmes Docker & Services

### ❌ Problème : Ollama ne démarre pas

**Symptômes** :
```bash
docker ps  # ollama absent ou en status "restarting"
docker logs ollama  # Erreurs OOM (Out of Memory)
```

**Causes possibles** :
- Mémoire insuffisante (< 8GB disponible)
- Modèle trop volumineux pour la RAM disponible
- Conflit de port 11434

**Solutions** :

**Solution 1 : Vérifier la mémoire disponible**
```bash
# Vérifier stats Docker
docker stats ollama

# Vérifier mémoire système
free -h
```

**Solution 2 : Réduire la limite mémoire**

Éditer `docker/docker-compose.yml` :
```yaml
ollama:
  deploy:
    resources:
      limits:
        memory: 6G  # Au lieu de 8G
      reservations:
        memory: 3G  # Au lieu de 4G
```

Redémarrer :
```bash
cd docker
docker-compose down
docker-compose up -d ollama
```

**Solution 3 : Utiliser un modèle plus léger**

Au lieu de Mistral (4.1GB), utiliser Phi3 (2.3GB) ou Gemma (1.7GB) :
```bash
# Dans le container Ollama
docker exec -it ollama ollama pull phi3
```

Puis modifier `.env.app` :
```bash
GENERATION_MODEL_ID=phi3
```

**Solution 4 : Vérifier conflit de port**
```bash
# Vérifier port 11434
netstat -tuln | grep 11434

# Si occupé, arrêter le processus
sudo kill -9 $(lsof -ti:11434)
```

---

### ❌ Problème : FastAPI ne démarre pas

**Symptômes** :
```bash
docker logs fastapi
# Erreurs de connexion DB, imports manquants, ou timeout
```

**Causes possibles** :
- PostgreSQL pas prêt (healthcheck fail)
- Dépendances manquantes
- Erreur dans les variables d'environnement

**Solutions** :

**Solution 1 : Vérifier dépendances de démarrage**
```bash
# Vérifier que pgvector est healthy
docker ps | grep pgvector

# Healthcheck manuel
docker exec -it pgvector pg_isready -U postgres
```

**Solution 2 : Vérifier les variables d'environnement**
```bash
# Vérifier .env.app existe
ls docker/env/.env.app

# Vérifier contenu critique
cat docker/env/.env.app | grep -E "POSTGRES_|SECRET_KEY|OLLAMA"
```

**Solution 3 : Reconstruire le container**
```bash
cd docker
docker-compose down fastapi
docker-compose build --no-cache fastapi
docker-compose up -d fastapi
```

**Solution 4 : Vérifier les logs détaillés**
```bash
# Logs en temps réel
docker logs -f fastapi

# Dernières 100 lignes
docker logs --tail 100 fastapi
```

---

### ❌ Problème : Frontend ne se charge pas

**Symptômes** :
- Page blanche sur `http://localhost`
- Erreur 502 Bad Gateway (Nginx)
- Console navigateur : `ERR_CONNECTION_REFUSED`

**Causes possibles** :
- Nginx mal configuré
- FastAPI down (API calls fail)
- Build Vite échoué

**Solutions** :

**Solution 1 : Vérifier Nginx**
```bash
# Vérifier container nginx
docker ps | grep nginx

# Tester config nginx
docker exec -it nginx nginx -t

# Redémarrer nginx
docker-compose restart nginx
```

**Solution 2 : Vérifier build frontend**
```bash
# Logs build
docker logs frontend

# Rebuild si nécessaire
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

**Solution 3 : Tester API directement**
```bash
# Bypass nginx - tester FastAPI direct
curl http://localhost:8000/api/v1/base/
# Devrait retourner : {"message":"Hello from Fil Rouge"}

# Bypass nginx - tester Frontend direct
curl http://localhost:3001
# Devrait retourner HTML
```

**Solution 4 : Vérifier routing nginx**

Fichier `docker/nginx/default.conf` doit contenir :
```nginx
location /api/ {
    proxy_pass http://fastapi:8000;
}

location / {
    proxy_pass http://frontend:80;
}
```

---

### ❌ Problème : Tous les services redémarrent en boucle

**Symptômes** :
```bash
docker ps  # Status "Restarting" pour plusieurs services
```

**Causes possibles** :
- Réseau Docker corrompu
- Mémoire système saturée
- Volumes corrompus

**Solutions** :

**Solution 1 : Vérifier mémoire système**
```bash
# Système Linux
free -h
df -h

# Si RAM < 2GB libre, arrêter services non critiques
docker-compose stop grafana prometheus node-exporter
```

**Solution 2 : Recréer réseau Docker**
```bash
cd docker
docker-compose down
docker network prune -f
docker-compose up -d
```

**Solution 3 : Vérifier volumes**
```bash
# Lister volumes
docker volume ls

# Inspecter volume pgvector
docker volume inspect docker_pgvector

# Si corrompu (EXTRÊME - PERTE DE DONNÉES)
docker-compose down
docker volume rm docker_pgvector
docker-compose up -d
```

**Solution 4 : Restart complet Docker**
```bash
# Ubuntu/Debian
sudo systemctl restart docker

# Puis redémarrer services
cd docker
docker-compose up -d
```

---

## 💾 Problèmes Base de Données

### ❌ Problème : PostgreSQL - Connexion refusée

**Symptômes** :
```
sqlalchemy.exc.OperationalError: could not connect to server
Connection refused (port 5432)
```

**Solutions** :

**Solution 1 : Vérifier service pgvector**
```bash
# Status
docker ps | grep pgvector

# Test connexion
docker exec -it pgvector pg_isready -U postgres

# Logs
docker logs pgvector
```

**Solution 2 : Vérifier credentials**

Fichier `.env.app` et `.env.postgres` doivent avoir les **mêmes credentials** :
```bash
# .env.postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=votre_password
POSTGRES_DB=minirag

# .env.app (doit correspondre)
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=votre_password  # MÊME password
POSTGRES_MAIN_DATABASE=minirag
```

**Solution 3 : Reset PostgreSQL**
```bash
docker-compose restart pgvector

# Attendre healthcheck
sleep 10

# Tester à nouveau
docker exec -it pgvector psql -U postgres -d minirag -c "SELECT version();"
```

---

### ❌ Problème : Tables n'existent pas

**Symptômes** :
```
relation "users" does not exist
relation "projects" does not exist
```

**Causes** : Migration non exécutée

**Solutions** :

**Solution 1 : Vérifier tables existantes**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c "\dt"
```

**Solution 2 : Recréer les tables**

Les tables sont créées automatiquement au premier démarrage de FastAPI via SQLAlchemy.

Forcer recréation :
```bash
# Arrêter FastAPI
docker-compose stop fastapi

# Redémarrer
docker-compose up -d fastapi

# Vérifier logs
docker logs -f fastapi
# Devrait afficher : "✓ Database tables created"
```

**Solution 3 : Création manuelle (si automatique échoue)**
```bash
docker exec -it fastapi python -c "
from sqlalchemy import create_engine
from models.db_schemes import Base
from helpers.config import get_settings

settings = get_settings()
engine = create_engine(f'postgresql://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@pgvector:5432/{settings.POSTGRES_MAIN_DATABASE}')
Base.metadata.create_all(engine)
print('Tables created!')
"
```

---

### ❌ Problème : PGVector extension manquante

**Symptômes** :
```
ERROR: extension "vector" is not available
```

**Solutions** :

**Solution 1 : Vérifier l'image**

S'assurer d'utiliser `pgvector/pgvector:0.8.1-pg17` dans `docker-compose.yml` :
```yaml
pgvector:
  image: pgvector/pgvector:0.8.1-pg17
```

**Solution 2 : Activer extension manuellement**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Solution 3 : Reset complet**
```bash
docker-compose down
docker volume rm docker_pgvector
docker-compose up -d pgvector

# Attendre 10s
sleep 10

# Recréer extension
docker exec -it pgvector psql -U postgres -d minirag -c "CREATE EXTENSION vector;"
```

---

### ❌ Problème : Qdrant - Collection introuvable

**Symptômes** :
```
Collection "project_{id}" not found
```

**Causes** : Projet non indexé dans Qdrant

**Solutions** :

**Solution 1 : Vérifier collections Qdrant**
```bash
# Dashboard Qdrant (navigateur)
http://localhost:6333/dashboard

# Via API
curl http://localhost:6333/collections
```

**Solution 2 : Ré-indexer le projet**

Via frontend :
1. Aller sur `/index` (admin)
2. Sélectionner projet
3. Cliquer "Index Project"

Via API :
```bash
curl -X POST http://localhost/api/v1/nlp/index/push/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Solution 3 : Nettoyer Qdrant et ré-indexer**
```bash
# Supprimer collection via API
curl -X DELETE http://localhost/api/v1/admin/vectors/project_1 \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Ré-indexer
curl -X POST http://localhost/api/v1/nlp/index/push/1 \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## ⚙️ Problèmes Backend (FastAPI)

### ❌ Problème : Erreur 500 sur les endpoints API

**Symptômes** :
```json
{
  "detail": "Internal Server Error",
  "signal": "ERROR"
}
```

**Solutions** :

**Solution 1 : Vérifier logs FastAPI**
```bash
# Logs temps réel
docker logs -f fastapi

# Chercher erreurs Python
docker logs fastapi 2>&1 | grep -i "error\|exception\|traceback"
```

**Solution 2 : Tester health endpoint**
```bash
curl http://localhost/api/v1/base/
# Attendu: {"message":"Hello from Fil Rouge"}

# Si erreur, FastAPI est down
docker-compose restart fastapi
```

**Solution 3 : Vérifier variables d'environnement**
```bash
# Entrer dans container
docker exec -it fastapi bash

# Vérifier config
python -c "from helpers.config import get_settings; print(get_settings())"
```

---

### ❌ Problème : Timeout sur les requêtes

**Symptômes** :
- Requêtes prennent >60s
- Erreur 504 Gateway Timeout

**Causes** :
- RAG answer generation (LLM lent)
- Ollama modèle pas chargé en RAM

**Solutions** :

**Solution 1 : Vérifier timeouts Nginx**

Fichier `docker/nginx/default.conf` doit avoir :
```nginx
proxy_connect_timeout 1000s;
proxy_send_timeout 1000s;
proxy_read_timeout 1000s;
```

**Solution 2 : Pré-charger modèle Ollama**
```bash
# Entrer dans Ollama
docker exec -it ollama bash

# Lancer modèle (garde en RAM)
ollama run mistral "test"

# Devrait répondre instantanément après
```

**Solution 3 : Utiliser modèle plus rapide**

Éditer `.env.app` :
```bash
# Remplacer Mistral par Gemma (plus rapide)
GENERATION_MODEL_ID=gemma:2b
```

Puis :
```bash
docker exec -it ollama ollama pull gemma:2b
docker-compose restart fastapi
```

---

### ❌ Problème : Upload PDF échoue (413 Request Entity Too Large)

**Symptômes** :
```
413 Request Entity Too Large
```

**Solutions** :

**Solution 1 : Augmenter limite Nginx**

Éditer `docker/nginx/default.conf` :
```nginx
client_max_body_size 200M;  # Au lieu de 100M
```

Redémarrer :
```bash
docker-compose restart nginx
```

**Solution 2 : Vérifier taille fichier**
```bash
# Limite actuelle : 100MB
ls -lh votre_fichier.pdf

# Si > 100MB, compresser d'abord
```

---

### ❌ Problème : Import LangChain échoue

**Symptômes** :
```
ModuleNotFoundError: No module named 'langchain_xxx'
```

**Solutions** :

**Solution 1 : Rebuild container avec dépendances**
```bash
cd docker
docker-compose down fastapi
docker-compose build --no-cache fastapi
docker-compose up -d fastapi
```

**Solution 2 : Installer dépendance manuellement**
```bash
docker exec -it fastapi pip install langchain-qdrant langchain-community
docker-compose restart fastapi
```

---

## 🖥️ Problèmes Frontend (React)

### ❌ Problème : Erreur 401 (Unauthorized) après login

**Symptômes** :
- Login réussit
- Redirection immédiate vers `/login`
- Console : `401 Unauthorized`

**Causes** :
- Token JWT non sauvegardé dans localStorage
- SECRET_KEY backend changée (tokens invalides)
- Token expiré (>24h)

**Solutions** :

**Solution 1 : Vérifier token dans localStorage**

Console navigateur (F12) :
```javascript
// Vérifier token existe
localStorage.getItem('token')

// Devrait retourner : "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

// Si null, le login n'a pas sauvegardé le token
```

**Solution 2 : Vérifier SECRET_KEY n'a pas changé**

Fichier `.env.app` :
```bash
SECRET_KEY=votre_cle_secrete_64_caracteres_minimum
```

Si vous avez changé SECRET_KEY :
1. Tous les anciens tokens sont invalides
2. Se reconnecter pour générer nouveau token

**Solution 3 : Clear localStorage et reconnecter**

Console navigateur :
```javascript
localStorage.clear()
// Puis se reconnecter
```

**Solution 4 : Vérifier interceptor Axios**

Fichier `frontend/src/services/api.js` doit contenir :
```javascript
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

### ❌ Problème : Page blanche après build

**Symptômes** :
- Page blanche
- Console : Erreurs de chargement assets

**Solutions** :

**Solution 1 : Rebuild frontend**
```bash
cd docker
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

**Solution 2 : Vérifier base URL Vite**

Fichier `frontend/vite.config.js` doit avoir :
```javascript
export default defineConfig({
  plugins: [react()],
  base: '/',  // Important pour routing
})
```

**Solution 3 : Clear cache navigateur**
- Ctrl+Shift+R (Windows/Linux)
- Cmd+Shift+R (Mac)

---

### ❌ Problème : API calls échouent (CORS)

**Symptômes** :
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solutions** :

**Solution 1 : Vérifier CORS backend**

Fichier `src/main.py` doit avoir middleware CORS (si activé) :
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: spécifier domaines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Solution 2 : Utiliser proxy Nginx**

Toutes les requêtes doivent aller via `http://localhost/api/*` (pas directement `http://localhost:8000`)

Vérifier `frontend/src/services/api.js` :
```javascript
const api = axios.create({
  baseURL: '/api/v1'  // PAS http://localhost:8000/api/v1
});
```

---

## 🤖 Problèmes RAG & NLP

### ❌ Problème : Vector search ne retourne rien

**Symptômes** :
```json
{
  "results": [],
  "total": 0
}
```

**Causes** :
- Projet non indexé dans Qdrant
- Chunks vides en DB
- Embeddings dimension mismatch

**Solutions** :

**Solution 1 : Vérifier indexation**
```bash
# Via API
curl http://localhost/api/v1/nlp/index/info/1 \
  -H "Authorization: Bearer TOKEN"

# Devrait retourner :
# {
#   "total_vectors": 150,  # > 0 si indexé
#   "collection_name": "project_1"
# }
```

**Solution 2 : Vérifier chunks en DB**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c \
  "SELECT COUNT(*) FROM datachunks WHERE project_id=1;"

# Devrait retourner > 0
```

**Solution 3 : Pipeline complet**
```bash
# 1. Upload PDF
curl -X POST http://localhost/api/v1/data/upload/1 \
  -H "Authorization: Bearer TOKEN" \
  -F "files=@document.pdf" \
  -F "language=fr"

# 2. Process (chunking)
curl -X POST http://localhost/api/v1/data/process/1 \
  -H "Authorization: Bearer TOKEN"

# 3. Index (vectorization)
curl -X POST http://localhost/api/v1/nlp/index/push/1 \
  -H "Authorization: Bearer TOKEN"

# 4. Test search
curl -X POST http://localhost/api/v1/nlp/index/search/1 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"test", "top_k":5}'
```

---

### ❌ Problème : RAG answer génération échoue

**Symptômes** :
```json
{
  "detail": "Error generating answer",
  "signal": "ERROR"
}
```

**Causes** :
- Ollama modèle non chargé
- Context trop long (>4096 tokens)
- Erreur LLM provider

**Solutions** :

**Solution 1 : Vérifier Ollama modèle**
```bash
# Lister modèles
docker exec -it ollama ollama list

# Si mistral absent
docker exec -it ollama ollama pull mistral

# Tester modèle
docker exec -it ollama ollama run mistral "Bonjour"
```

**Solution 2 : Réduire top_k (context)**

Au lieu de `top_k=10`, utiliser `top_k=3` :
```bash
curl -X POST http://localhost/api/v1/nlp/index/answer/1 \
  -d '{"query":"test", "top_k":3}'  # Réduit le context
```

**Solution 3 : Changer LLM provider**

Éditer `.env.app` :
```bash
# Option 1 : OpenAI (plus fiable)
GENERATION_BACKEND=openai
GENERATION_MODEL_ID=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Option 2 : Groq (rapide + gratuit)
GENERATION_BACKEND=groq
GENERATION_MODEL_ID=llama-3.1-8b-instant
GROQ_API_KEY=gsk_...
```

Redémarrer :
```bash
docker-compose restart fastapi
```

---

### ❌ Problème : Embeddings service fail

**Symptômes** :
```
Failed to load embeddings model
```

**Solutions** :

**Solution 1 : Vérifier HuggingFace cache**
```bash
# Volume doit exister
docker volume inspect docker_huggingface_cache

# Logs téléchargement
docker logs fastapi | grep -i "download\|huggingface"
```

**Solution 2 : Retélécharger modèle**
```bash
# Supprimer cache
docker volume rm docker_huggingface_cache

# Recréer
docker-compose up -d fastapi

# Attendre téléchargement (420MB, ~5min)
docker logs -f fastapi
```

**Solution 3 : Utiliser embeddings API**

Éditer `.env.app` :
```bash
EMBEDDING_BACKEND=openai
EMBEDDING_MODEL_ID=text-embedding-3-small
OPENAI_API_KEY=sk-...
```

---

## 📊 Problèmes Exchange Rates & ML

### ❌ Problème : Taux de change non récupérés

**Symptômes** :
```json
{
  "latest_rates": null,
  "error": "No rates available"
}
```

**Causes** :
- Scheduler pas démarré
- Clés API BAM invalides
- Appel API BAM échoué

**Solutions** :

**Solution 1 : Vérifier scheduler**
```bash
docker logs fastapi | grep -i "scheduler"

# Devrait afficher :
# "✓ Exchange Rates Scheduler initialized and started"
```

**Solution 2 : Vérifier clés API BAM**

Fichier `.env.app` :
```bash
CLE_API_CHANGES=votre_cle_api_bam
CLE_API_CHANGES_2=votre_cle_secours
```

Tester clé manuellement :
```bash
curl "https://api.moroccanexchangerates.com/api/v1/changes?cle=VOTRE_CLE"
```

**Solution 3 : Fetch manuel**
```bash
# Via endpoint admin
curl -X POST http://localhost/api/v1/exchange-rates/admin/fetch-now \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Solution 4 : Vérifier table en DB**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c \
  "SELECT * FROM exchange_rates ORDER BY date DESC LIMIT 5;"
```

---

### ❌ Problème : Prédictions ML non disponibles

**Symptômes** :
```json
{
  "predictions": [],
  "error": "Model not trained"
}
```

**Causes** :
- Modèle LSTM non entraîné
- Données historiques insuffisantes (<90 jours)

**Solutions** :

**Solution 1 : Vérifier données historiques**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c \
  "SELECT COUNT(*) FROM exchange_rates WHERE rate_type='actual';"

# Devrait retourner > 90
```

**Solution 2 : Entraîner modèle**
```bash
# Via endpoint admin
curl -X POST http://localhost/api/v1/exchange-rates/admin/train-model \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Attendre ~2-5min
# Puis générer prédictions
curl -X POST http://localhost/api/v1/exchange-rates/admin/generate-predictions \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

**Solution 3 : Vérifier modèle info**
```bash
curl http://localhost/api/v1/exchange-rates/admin/model-info \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Devrait retourner :
# {
#   "model_exists": true,
#   "last_trained": "2025-12-04T10:00:00"
# }
```

---

### ❌ Problème : Graphiques Exchange Rates vides

**Symptômes** :
- Page `/exchange-rates` affiche graphiques vides
- Pas d'erreur console

**Solutions** :

**Solution 1 : Vérifier API response**

Console navigateur (F12) → Network → Refresh page :
```
GET /api/v1/exchange-rates/latest
Status: 200
Response: { "MAD_EUR": {...}, "MAD_USD": {...} }
```

**Solution 2 : Vérifier Recharts**

Fichier `frontend/package.json` doit avoir :
```json
{
  "dependencies": {
    "recharts": "^3.5.0"
  }
}
```

**Solution 3 : Clear cache + rebuild frontend**
```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 🔐 Problèmes Authentication

### ❌ Problème : Impossible de créer premier admin

**Symptômes** :
- Inscription réussit mais user n'est pas admin

**Causes** :
- Table users déjà contient un user
- Premier user SEULEMENT devient admin

**Solutions** :

**Solution 1 : Vérifier si users existent**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c \
  "SELECT id, username, role FROM users;"
```

**Solution 2 : Reset table users**
```bash
# ATTENTION : Supprime tous les users
docker exec -it pgvector psql -U postgres -d minirag -c \
  "TRUNCATE TABLE users CASCADE;"

# Puis créer premier user via /register
```

**Solution 3 : Promouvoir user existant en admin**
```bash
docker exec -it pgvector psql -U postgres -d minirag -c \
  "UPDATE users SET role='admin' WHERE username='votre_username';"
```

---

### ❌ Problème : Token JWT invalide

**Symptômes** :
```json
{
  "detail": "Could not validate credentials"
}
```

**Solutions** :

**Solution 1 : Vérifier SECRET_KEY**

Fichier `.env.app` :
```bash
SECRET_KEY=cle_secrete_minimum_32_caracteres
# NE PAS changer après avoir créé des tokens
```

**Solution 2 : Clear token + reconnecter**
```javascript
// Console navigateur
localStorage.removeItem('token')
localStorage.removeItem('user')
```

**Solution 3 : Vérifier format Authorization header**

Fichier `frontend/src/services/api.js` :
```javascript
// Doit être : "Bearer eyJhbG..."
config.headers.Authorization = `Bearer ${token}`;
```

---

### ❌ Problème : Password hash fail

**Symptômes** :
```
ValueError: Invalid salt
```

**Solutions** :

**Solution 1 : Vérifier bcrypt installé**
```bash
docker exec -it fastapi pip show bcrypt
# Devrait afficher version 4.0.1
```

**Solution 2 : Reinstaller bcrypt**
```bash
docker exec -it fastapi pip install --force-reinstall bcrypt==4.0.1
docker-compose restart fastapi
```

---

## 📈 Problèmes Monitoring

### ❌ Problème : Prometheus ne collecte pas de métriques

**Symptômes** :
- Dashboard Prometheus vide (`http://localhost:9090`)
- Grafana : "No data"

**Solutions** :

**Solution 1 : Vérifier targets Prometheus**

Navigateur → `http://localhost:9090/targets`

Devrait afficher :
- `fastapi` (UP)
- `node-exporter` (UP)
- `postgres-exporter` (UP)
- `qdrant` (UP)

**Solution 2 : Vérifier config Prometheus**

Fichier `docker/prometheus/prometheus.yml` doit contenir :
```yaml
scrape_configs:
  - job_name: 'fastapi'
    static_configs:
      - targets: ['fastapi:8000']
    metrics_path: '/TrhBVe_m5gg2002_E5VVqS'
```

**Solution 3 : Redémarrer Prometheus**
```bash
docker-compose restart prometheus

# Attendre 15s (scrape_interval)
sleep 15

# Vérifier http://localhost:9090/targets
```

---

### ❌ Problème : Grafana ne se connecte pas à Prometheus

**Symptômes** :
- Datasource Prometheus : "Connection failed"

**Solutions** :

**Solution 1 : Configurer datasource**

1. Aller sur `http://localhost:3000` (admin/admin)
2. Configuration → Data Sources → Add Prometheus
3. URL : `http://prometheus:9090` (pas localhost)
4. Save & Test

**Solution 2 : Vérifier réseau Docker**
```bash
# Grafana et Prometheus doivent être sur même réseau
docker inspect grafana | grep -i network
docker inspect prometheus | grep -i network

# Devrait afficher : "backend"
```

---

### ❌ Problème : Dashboard Grafana vide

**Symptômes** :
- Datasource connecté
- Mais dashboards n'affichent aucune donnée

**Solutions** :

**Solution 1 : Importer dashboards**

Grafana → Dashboards → Import :
- **FastAPI Observability** : ID `16110`
- **Node Exporter Full** : ID `1860`
- **PostgreSQL Database** : ID `9628`

**Solution 2 : Vérifier métriques existent**

Prometheus → Graph → Query :
```promql
# Métriques FastAPI
http_requests_total

# Métriques système
node_cpu_seconds_total

# Métriques PostgreSQL
pg_up
```

---

## 🛠️ Commandes de Diagnostic

### Vérifier état global

```bash
# Status tous services
docker-compose ps

# Resources (CPU, RAM)
docker stats

# Logs tous services
docker-compose logs --tail=50
```

---

### Healthcheck complet

```bash
#!/bin/bash
echo "=== Fil Rouge Healthcheck ==="

echo "1. Docker services status:"
docker-compose ps

echo -e "\n2. PostgreSQL:"
docker exec -it pgvector pg_isready -U postgres && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n3. FastAPI:"
curl -s http://localhost/api/v1/base/ | grep -q "Hello" && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n4. Frontend:"
curl -s http://localhost/ | grep -q "<!DOCTYPE html>" && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n5. Qdrant:"
curl -s http://localhost:6333/collections | grep -q "collections" && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n6. Ollama:"
docker exec -it ollama ollama list &>/dev/null && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n7. Prometheus:"
curl -s http://localhost:9090/-/ready | grep -q "Prometheus" && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n8. Grafana:"
curl -s http://localhost:3000/api/health | grep -q "ok" && echo "✓ OK" || echo "✗ FAIL"

echo -e "\n=== Healthcheck Complete ==="
```

Sauvegarder dans `scripts/healthcheck.sh` puis :
```bash
chmod +x scripts/healthcheck.sh
./scripts/healthcheck.sh
```

---

### Cleanup complet

```bash
#!/bin/bash
echo "⚠️  ATTENTION : Suppression complète (PERTE DE DONNÉES)"
read -p "Continuer? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Annulé."
  exit 1
fi

cd docker

# Arrêter tous services
docker-compose down

# Supprimer volumes (DONNÉES PERDUES)
docker volume rm docker_pgvector docker_qdrant_data docker_fastapi_data

# Supprimer images
docker-compose down --rmi all

# Nettoyer Docker
docker system prune -af --volumes

echo "✓ Cleanup terminé. Recréer avec: docker-compose up -d"
```

**⚠️ ATTENTION** : Cette commande supprime TOUTES les données (users, projets, PDFs, vecteurs).

---

### Reset service spécifique

```bash
# Reset FastAPI uniquement
docker-compose stop fastapi
docker-compose rm -f fastapi
docker-compose build --no-cache fastapi
docker-compose up -d fastapi

# Reset PostgreSQL (PERTE DONNÉES)
docker-compose stop fastapi pgvector postgres-exporter
docker volume rm docker_pgvector
docker-compose up -d pgvector
# Attendre 10s
sleep 10
docker-compose up -d postgres-exporter fastapi

# Reset Qdrant (PERTE VECTEURS)
docker-compose stop qdrant
docker volume rm docker_qdrant_data
docker-compose up -d qdrant
```

---

### Backup & Restore

**Backup PostgreSQL** :
```bash
# Backup complet
docker exec -it pgvector pg_dump -U postgres minirag > backup_$(date +%Y%m%d).sql

# Backup table spécifique
docker exec -it pgvector pg_dump -U postgres -t users minirag > backup_users.sql
```

**Restore PostgreSQL** :
```bash
# Restore complet
cat backup_20251204.sql | docker exec -i pgvector psql -U postgres minirag

# Restore table spécifique
cat backup_users.sql | docker exec -i pgvector psql -U postgres minirag
```

**Backup Qdrant** :
```bash
# Via API (snapshot)
curl -X POST http://localhost:6333/collections/project_1/snapshots

# Copier snapshot depuis volume
docker cp qdrant:/qdrant/storage/snapshots ./qdrant_backup/
```

**Backup Assets (PDFs)** :
```bash
# Copier depuis volume Docker
docker run --rm -v docker_fastapi_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/fastapi_data_$(date +%Y%m%d).tar.gz /data
```

---

## 📞 Support

### Logs utiles

```bash
# Tous les services
docker-compose logs --tail=100 -f

# Service spécifique
docker logs -f fastapi
docker logs -f pgvector
docker logs -f ollama

# Rechercher erreurs
docker-compose logs | grep -i "error\|exception\|fail"
```

---

### Informations système

```bash
# Version Docker
docker --version
docker-compose --version

# Espace disque
df -h

# RAM disponible
free -h

# Volumes Docker
docker volume ls
docker system df
```

---

### Contacts et Ressources

- **Documentation principale** : `DOCUMENTATION.md`
- **API Reference** : `docs/API_REFERENCE.md`
- **Deployment Guide** : `docs/DEPLOYMENT_GUIDE.md`
- **GitHub Issues** : [Créer une issue si problème non documenté]

---

## ✅ Checklist Problèmes Résolus

Avant de contacter le support, vérifier :

- [ ] Tous services Docker running (`docker-compose ps`)
- [ ] Logs vérifiés (pas d'erreurs critiques)
- [ ] Healthcheck complet exécuté
- [ ] Variables d'environnement correctes
- [ ] Volumes persistants non corrompus
- [ ] Mémoire système > 8GB libre
- [ ] Disque > 20GB libre

---

**Dernière mise à jour** : Décembre 2025
**Version** : 1.0
**Statut** : ✅ **Documentation complète**
