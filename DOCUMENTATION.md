# 📚 DOCUMENTATION PROJET FIL ROUGE

> **Documentation complète du système RAG Finance**
> Version 1.0 | Dernière mise à jour : Décembre 2025

---

## 📖 Table des matières

### Vue d'ensemble
- [Introduction](#introduction)
- [Technologies utilisées](#technologies-utilisées)
- [Démarrage rapide](#démarrage-rapide)

### Documentation détaillée par phase
- [Phase 1 : Architecture Globale](#phase-1--architecture-globale) ✅ **Complétée**
- [Phase 2 : Analyse Backend](#phase-2--analyse-backend) 🚧 **À compléter**
- [Phase 3 : Analyse Frontend](#phase-3--analyse-frontend) 🚧 **À compléter**
- [Phase 4 : Code Mort & Nettoyage](#phase-4--code-mort--nettoyage) 🚧 **À compléter**
- [Phase 5 : Flux de Données](#phase-5--flux-de-données) 🚧 **À compléter**
- [Phase 6 : Recommandations](#phase-6--recommandations) 🚧 **À compléter**

### Guides pratiques
- [Guide de déploiement](#guide-de-déploiement)
- [Référence API](#référence-api)
- [Troubleshooting](#troubleshooting)
- [Commandes Docker utiles](#commandes-docker-utiles)

---

## 📋 Introduction

### Qu'est-ce que Fil Rouge ?

**Fil Rouge** est une application de **Retrieval-Augmented Generation (RAG)** spécialisée dans l'analyse de documents financiers, avec des fonctionnalités avancées de prédiction de taux de change.

### Fonctionnalités principales

✅ **RAG Multi-langue** (FR/EN/AR)
✅ **Upload & Processing de PDFs**
✅ **Recherche sémantique vectorielle**
✅ **Q&A conversationnel avec historique**
✅ **Prédiction ML de taux de change** (MAD/EUR, MAD/USD)
✅ **Multi-provider LLM** (Ollama [GRATUIT], OpenAI, Cohere, Groq)
✅ **Dual Vector DB** (Qdrant + PGVector)
✅ **Monitoring complet** (Prometheus + Grafana)

### Architecture

- **Type** : Microservices (11 conteneurs Docker)
- **Backend** : FastAPI (Python 3.10)
- **Frontend** : React 18 + Vite
- **Database** : PostgreSQL 17 + PGVector
- **Vector DB** : Qdrant v1.13.6
- **LLM** : Ollama (local, gratuit)
- **Orchestration** : Docker Compose

---

## 🛠️ Technologies utilisées

### Backend
- **Framework** : FastAPI 0.110.2
- **ORM** : SQLAlchemy 2.0.36 (async)
- **LangChain** : 0.3.17+ (RAG pipeline)
- **Embeddings** : Sentence Transformers 2.7.0 (multilingual)
- **ML** : TensorFlow 2.16+ (LSTM)
- **Auth** : JWT (python-jose)
- **Monitoring** : Prometheus + Grafana

### Frontend
- **Framework** : React 18.2.0
- **Build Tool** : Vite 5.0.11
- **Routing** : React Router 6.21.0
- **HTTP** : Axios 1.6.5
- **Charts** : Recharts 3.5.0
- **Styling** : Tailwind CSS 3.4.1

### Infrastructure
- **Conteneurisation** : Docker + Docker Compose
- **Reverse Proxy** : Nginx
- **Database** : PostgreSQL 17 + PGVector 0.8.1
- **Vector DB** : Qdrant v1.13.6
- **LLM** : Ollama (Mistral, Llama 3.1)

---

## 🚀 Démarrage rapide

### Prérequis

- Docker + Docker Compose
- 16GB RAM minimum (24GB recommandé)
- 20GB d'espace disque

### Installation

```bash
# 1. Cloner le projet
cd C:\Users\lenovo\Documents\fil_rouge

# 2. Configurer les variables d'environnement
cd docker/env
cp .env.app.example .env.app
cp .env.postgres.example .env.postgres
# Éditer les fichiers .env avec vos clés API

# 3. Lancer tous les services
cd ..
docker-compose up -d

# 4. Vérifier que tous les conteneurs sont démarrés
docker-compose ps

# 5. Accéder à l'application
# Frontend : http://localhost (port 80)
# API : http://localhost:8000
# Grafana : http://localhost:3000
# Qdrant Dashboard : http://localhost:6333/dashboard
```

### Premier utilisateur (Admin)

Le premier utilisateur créé devient automatiquement **admin**.

```bash
# Créer un compte via l'interface : http://localhost/register
# Username: admin
# Email: admin@example.com
# Password: votre_mot_de_passe
```

---

## Phase 1 : Architecture Globale

> ✅ **Phase complétée** | Durée : 2h
> 📄 Documentation détaillée : [`docs/phases/01_ARCHITECTURE_GLOBALE.md`](docs/phases/01_ARCHITECTURE_GLOBALE.md)

### Vue d'ensemble

Le projet utilise une **architecture microservices** avec **11 conteneurs Docker** interconnectés via un réseau bridge.

### Services Docker (11 conteneurs)

| # | Service | Port | Rôle |
|---|---------|------|------|
| 1 | **nginx** | 80 | Reverse Proxy (point d'entrée unique) |
| 2 | **frontend** | 3001 | Interface React (SPA) |
| 3 | **fastapi** | 8000 | API Backend REST |
| 4 | **pgvector** | 5432 | PostgreSQL + extension vectors |
| 5 | **qdrant** | 6333 | Vector Database (similarité) |
| 6 | **ollama** | 11434 | LLM local (Mistral, Llama) |
| 7 | **prometheus** | 9090 | Collecte métriques |
| 8 | **grafana** | 3000 | Dashboards monitoring |
| 9 | **node-exporter** | 9100 | Métriques système |
| 10 | **postgres-exporter** | 9187 | Métriques PostgreSQL |

### Architecture en couches

```
┌─────────────────────────────────────────────────────┐
│              COUCHE PRÉSENTATION                    │
│  React 18 + Vite (18 routes, AuthContext)          │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────┐
│            COUCHE REVERSE PROXY                     │
│  Nginx (Routing /api → FastAPI, / → Frontend)      │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│           COUCHE APPLICATIVE                        │
│  FastAPI (7 routers, 40+ endpoints)                │
│  - Routes, Controllers, Services, Models            │
│  - LangChain (RAG, Embeddings, VectorStore)        │
│  - Exchange Rates Module (ML + Scheduler)          │
└──────┬──────────────┬──────────────┬───────────────┘
       │              │              │
       ▼              ▼              ▼
┌───────────┐  ┌──────────┐  ┌─────────────┐
│PostgreSQL │  │  Qdrant  │  │   Ollama    │
│+ PGVector │  │(Vectors) │  │   (LLM)     │
└───────────┘  └──────────┘  └─────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────┐
│         COUCHE OBSERVABILITÉ                        │
│  Prometheus → Grafana (Dashboards)                  │
└─────────────────────────────────────────────────────┘
```

### Points d'entrée

#### Backend : `src/main.py`
- Initialise FastAPI avec lifespan management
- Configure database (PostgreSQL async)
- Initialise LangChain services (Embeddings, Prompts)
- Démarre Exchange Rates Scheduler (job quotidien 9h)
- Ajoute Prometheus middleware
- Inclut 7 routers (40+ endpoints)

#### Frontend : `frontend/src/App.jsx`
- Router principal React (18 routes)
- AuthProvider (gestion JWT globale)
- ProtectedRoute (auth + rôle admin)

### Routes principales

**Routes publiques :**
- `/login` - Authentification
- `/register` - Inscription

**Routes utilisateur (auth requis) :**
- `/dashboard` - Page d'accueil
- `/search` - Recherche vectorielle
- `/qa` - Q&A conversationnel RAG
- `/exchange-rates` - Graphiques taux de change

**Routes admin uniquement :**
- `/upload` - Upload PDFs
- `/process` - Processing documents
- `/index` - Indexation vectorielle
- `/users` - Gestion utilisateurs
- `/admin/*` - CRUD (projects, assets, chunks, conversations, messages, vectors)

### Volumes persistants

| Volume | Service | Taille | Contenu |
|--------|---------|--------|---------|
| `ollama_models` | ollama | ~5-10GB | Modèles LLM |
| `fastapi_data` | fastapi | ~100MB-1GB | PDFs uploadés |
| `huggingface_cache` | fastapi | ~420MB | Modèle embeddings |
| `pgvector` | pgvector | ~500MB-5GB | PostgreSQL + vecteurs |
| `qdrant_data` | qdrant | ~200MB-2GB | Collections vecteurs |
| `prometheus_data` | prometheus | ~100MB | Métriques |
| `grafana_data` | grafana | ~50MB | Dashboards |

**Total** : ~6-20GB (selon usage)

### Ressources mémoire

- **RAM minimum** : 16GB
- **RAM recommandé** : 20-24GB
- **Ollama** : 8GB max, 4GB réservé
- **FastAPI** : 4GB max, 2GB réservé

---

## Phase 2 : Analyse Backend

> 🚧 **Phase à compléter**
> 📄 Documentation détaillée : [`docs/phases/02_BACKEND_ANALYSIS.md`](docs/phases/02_BACKEND_ANALYSIS.md)

### Aperçu

Analyse approfondie du backend FastAPI :
- **7 routers** avec 40+ endpoints
- **4 contrôleurs** (NLP, Data, Process, Project)
- **5 services LangChain** (RAG, Embeddings, VectorStore, Prompt, Document)
- **7 modèles** (User, Project, Asset, Chunk, Conversation, Message, ExchangeRate)
- **Module Exchange Rates** (Jobs, ML, Services)

*Détails à venir lors de l'analyse de la Phase 2.*

---

## Phase 3 : Analyse Frontend

> 🚧 **Phase à compléter**
> 📄 Documentation détaillée : [`docs/phases/03_FRONTEND_ANALYSIS.md`](docs/phases/03_FRONTEND_ANALYSIS.md)

### Aperçu

Analyse approfondie du frontend React :
- **18 routes** (2 publiques, 4 user, 12 admin)
- **Context API** (AuthContext)
- **Custom hooks** (useConversation)
- **Services API** (api.js avec Axios interceptors)
- **Composants** (Navbar, ProtectedRoute, Admin components)

*Détails à venir lors de l'analyse de la Phase 3.*

---

## Phase 4 : Code Mort & Nettoyage

> 🚧 **Phase à compléter**
> 📄 Documentation détaillée : [`docs/phases/04_CODE_CLEANUP.md`](docs/phases/04_CODE_CLEANUP.md)

### Aperçu

Identification et nettoyage du code inutilisé :
- Imports non utilisés (backend + frontend)
- Fonctions mortes
- Packages npm obsolètes
- Fichiers corrompus/backups
- Dépendances inutiles

*Détails à venir lors de l'analyse de la Phase 4.*

---

## Phase 5 : Flux de Données

> 🚧 **Phase à compléter**
> 📄 Documentation détaillée : [`docs/phases/05_DATA_FLOWS.md`](docs/phases/05_DATA_FLOWS.md)

### Aperçu

Documentation des flux de données complets :
- Flux RAG (Upload → Process → Index → Query → Answer)
- Flux Authentication (Register/Login → JWT → Axios)
- Flux Exchange Rates (Scheduler → BAM API → DB → ML → Frontend)
- Flux Admin (CRUD operations)

*Détails à venir lors de l'analyse de la Phase 5.*

---

## Phase 6 : Recommandations

> 🚧 **Phase à compléter**
> 📄 Documentation détaillée : [`docs/phases/06_RECOMMENDATIONS.md`](docs/phases/06_RECOMMENDATIONS.md)

### Aperçu

Plan d'amélioration du projet :
- Tests à ajouter (unitaires, intégration, E2E)
- Sécurité à renforcer (CORS, rate limiting, secrets)
- Performance à optimiser (caching, pooling)
- Features à développer
- Architecture à améliorer

*Détails à venir lors de l'analyse de la Phase 6.*

---

## 📚 Guide de déploiement

### Développement local

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f fastapi

# Redémarrer un service
docker-compose restart fastapi

# Arrêter tous les services
docker-compose down

# Arrêter + supprimer volumes (⚠️ perte de données)
docker-compose down -v
```

### Production (VPS)

```bash
# 1. Cloner sur le serveur
git clone <repo> /var/www/fil_rouge
cd /var/www/fil_rouge

# 2. Configurer les .env (production)
cd docker/env
nano .env.app
# - Changer SECRET_KEY
# - Ajouter vraies API keys
# - Configurer domaine

# 3. Lancer en mode production
docker-compose up -d

# 4. Configurer Nginx SSL (Let's Encrypt)
# Voir docs/DEPLOYMENT_GUIDE.md
```

### Variables d'environnement critiques

**`.env.app` (FastAPI)**
```bash
SECRET_KEY=<générer_clé_sécurisée>
POSTGRES_PASSWORD=<mot_de_passe_fort>
CLE_API_CHANGES=<clé_api_bam>

# LLM Configuration
GENERATION_BACKEND=ollama  # ou openai, cohere, groq
GENERATION_MODEL_ID=mistral

# Embeddings
EMBEDDING_BACKEND=local  # ou openai, cohere
EMBEDDING_MODEL_ID=sentence-transformers/paraphrase-multilingual-mpnet-base-v2

# Vector DB
VECTOR_DB_BACKEND=qdrant  # ou pgvector
QDRANT_URL=http://qdrant:6333
```

---

## 🔍 Référence API

### Endpoints Backend

**Base**
- `GET /health` - Health check
- `GET /TrhBVe_m5gg2002_E5VVqS` - Prometheus metrics

**Auth**
- `POST /api/v1/auth/register` - Inscription
- `POST /api/v1/auth/login` - Connexion
- `GET /api/v1/auth/me` - User actuel
- `GET /api/v1/auth/users` - Liste users (admin)

**Data**
- `POST /api/v1/data/upload/{project_id}` - Upload PDFs (admin)
- `POST /api/v1/data/process/{project_id}` - Process documents (admin)
- `GET /api/v1/data/project/{project_id}/language` - Langue projet
- `PUT /api/v1/data/project/{project_id}/language` - Modifier langue (admin)

**NLP/RAG**
- `POST /api/v1/nlp/index/push/{project_id}` - Indexer vecteurs (admin)
- `GET /api/v1/nlp/index/info/{project_id}` - Stats index (admin)
- `POST /api/v1/nlp/index/search/{project_id}` - Recherche vectorielle
- `POST /api/v1/nlp/index/answer/{project_id}` - Q&A RAG

**Conversations**
- `POST /api/v1/conversations/create` - Créer conversation
- `GET /api/v1/conversations/project/{project_id}` - Liste conversations
- `GET /api/v1/conversations/{conv_id}/messages` - Messages
- `DELETE /api/v1/conversations/{conv_id}` - Supprimer

**Exchange Rates (Public)**
- `GET /api/v1/exchange-rates/latest` - Derniers taux
- `GET /api/v1/exchange-rates/predictions` - Historique + prédictions
- `GET /api/v1/exchange-rates/history` - Historique

**Exchange Rates (Admin)**
- `POST /api/v1/exchange-rates/admin/train-model` - Entraîner LSTM
- `POST /api/v1/exchange-rates/admin/generate-predictions` - Générer prédictions
- `POST /api/v1/exchange-rates/admin/fetch-rates-now` - Fetch manuel
- `GET /api/v1/exchange-rates/admin/scheduler/status` - Statut scheduler

**Admin**
- `GET /api/v1/admin/projects` - Liste projets
- `DELETE /api/v1/admin/projects/{id}` - Supprimer projet
- `GET /api/v1/admin/assets` - Liste assets
- `DELETE /api/v1/admin/assets/{id}` - Supprimer asset
- `GET /api/v1/admin/chunks` - Liste chunks
- `DELETE /api/v1/admin/chunks/{id}` - Supprimer chunk
- *(+ conversations, messages, vectors)*

---

## 🐛 Troubleshooting

### Problème : Ollama ne démarre pas

```bash
# Vérifier les logs
docker logs ollama

# Vérifier la mémoire disponible
docker stats

# Redémarrer Ollama
docker-compose restart ollama

# Si échec, réduire la limite mémoire dans docker-compose.yml
# memory: 6G au lieu de 8G
```

### Problème : FastAPI ne se connecte pas à PostgreSQL

```bash
# Vérifier que pgvector est healthy
docker-compose ps

# Tester la connexion
docker exec -it pgvector psql -U postgres -d minirag

# Vérifier les credentials dans .env.app
cat docker/env/.env.app | grep POSTGRES
```

### Problème : Frontend ne charge pas

```bash
# Vérifier nginx
docker logs nginx

# Vérifier frontend
docker logs frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

### Problème : Erreur 401 (Non autorisé)

```bash
# Vérifier le token JWT dans localStorage
# Console navigateur : localStorage.getItem('token')

# Vérifier SECRET_KEY dans .env.app
# Doit être identique entre redémarrages

# Se reconnecter
```

### Problème : Vector search ne retourne rien

```bash
# Vérifier que l'indexation est faite
# Aller sur /index et indexer le projet

# Vérifier Qdrant
curl http://localhost:6333/collections

# Vérifier les chunks en DB
docker exec -it pgvector psql -U postgres -d minirag
SELECT COUNT(*) FROM datachunks;
```

---

## 🔧 Commandes Docker utiles

### Gestion des conteneurs

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f fastapi

# Redémarrer un service
docker-compose restart fastapi

# Arrêter tous les services
docker-compose down

# Rebuild un service
docker-compose up -d --build fastapi
```

### Gestion des volumes

```bash
# Lister les volumes
docker volume ls

# Inspecter un volume
docker volume inspect fil_rouge_pgvector

# Sauvegarder la base de données
docker exec pgvector pg_dump -U postgres minirag > backup.sql

# Restaurer la base de données
cat backup.sql | docker exec -i pgvector psql -U postgres minirag

# ⚠️ Supprimer tous les volumes (perte de données)
docker-compose down -v
```

### Accès aux conteneurs

```bash
# Shell dans FastAPI
docker exec -it fastapi bash

# Shell dans PostgreSQL
docker exec -it pgvector psql -U postgres -d minirag

# Shell dans Ollama
docker exec -it ollama bash

# Télécharger un modèle Ollama
docker exec -it ollama ollama pull mistral
docker exec -it ollama ollama pull llama3.1
```

### Monitoring

```bash
# Stats CPU/RAM en temps réel
docker stats

# Espace disque des volumes
docker system df -v

# Nettoyer images inutilisées
docker system prune -a

# Voir les processus dans un conteneur
docker top fastapi
```

### Debugging

```bash
# Vérifier la santé des services
docker-compose ps

# Inspecter un conteneur
docker inspect fastapi

# Voir les variables d'environnement
docker exec fastapi env

# Tester la connectivité réseau
docker exec fastapi ping pgvector
docker exec fastapi ping qdrant
```

---

## 📝 Notes importantes

### Sécurité

⚠️ **En production** :
- Changer `SECRET_KEY` dans `.env.app`
- Utiliser des mots de passe forts
- Configurer HTTPS (Let's Encrypt)
- Limiter les ports exposés (seulement 80/443)
- Activer le firewall
- Configurer CORS correctement

### Performance

💡 **Optimisations** :
- Utiliser un VPS avec au moins 16GB RAM
- Activer Redis pour le caching (futur)
- Configurer un CDN pour les assets statiques
- Utiliser PostgreSQL connection pooling
- Monitorer avec Grafana et ajuster les ressources

### Backup

💾 **Sauvegardes régulières** :
- Base de données PostgreSQL (quotidien)
- Volumes Qdrant (hebdomadaire)
- Fichiers uploadés dans `fastapi_data` (quotidien)
- Configuration `.env` (versionné hors Git)

---

## 🤝 Contribution

Pour contribuer au projet :

1. Lire la documentation complète dans `docs/`
2. Suivre les conventions de code (PEP 8 pour Python, ESLint pour JavaScript)
3. Ajouter des tests pour les nouvelles fonctionnalités
4. Mettre à jour la documentation si nécessaire

---

## 📄 License

*À définir*

---

## 📞 Support

Pour toute question ou problème :
- Consulter la section [Troubleshooting](#troubleshooting)
- Lire la documentation détaillée dans `docs/`
- Vérifier les logs : `docker-compose logs -f`

---

**Dernière mise à jour** : Décembre 2025
**Version** : 1.0
**Statut** : En développement actif
