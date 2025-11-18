# 🐳 Guide de Déploiement Docker - RAG avec LangChain

Guide complet pour déployer votre application RAG avec **embeddings locaux HuggingFace** sur Docker.

## 📋 Table des Matières

1. [Prérequis](#prérequis)
2. [Configuration](#configuration)
3. [Build et Déploiement](#build-et-déploiement)
4. [Vérification](#vérification)
5. [Ressources Système](#ressources-système)
6. [Troubleshooting](#troubleshooting)
7. [Production](#production)

---

## 🔧 Prérequis

### Logiciels Requis
- **Docker** ≥ 20.10
- **Docker Compose** ≥ 2.0
- **8 GB RAM minimum** (recommandé : 16 GB)
- **10 GB d'espace disque** (pour images + données)

### Vérifier l'Installation
```bash
docker --version
docker compose version
```

---

## ⚙️ Configuration

### 1. Copier les Fichiers de Configuration

```bash
cd docker/env

# Copier l'exemple
cp .env.example.app .env.app

# Copier les autres configs si nécessaire
cp .env.example.postgres .env.postgres
cp .env.example.grafana .env.grafana
cp .env.example.postgres-exporter .env.postgres-exporter
```

### 2. Configurer .env.app

Éditer `docker/env/.env.app` :

```bash
nano docker/env/.env.app
```

**Configuration Minimale** (Embeddings Locaux) :

```bash
#APP
APP_NAME=rag_finance
APP_VERSION=1.0.0
SECRET_KEY=CHANGEZ_CETTE_CLE_EN_PRODUCTION_MINIMUM_32_CHARS

#POSTGRES
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE
POSTGRES_HOST=pgvector
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE=minirag

# LLM Config
GENERATION_BACKEND=openai
GENERATION_MODEL_ID=gpt-3.5-turbo-0125
OPENAI_API_KEY=sk-votre-cle-openai-ici

# 🆓 Embeddings LOCAUX (Gratuit!)
EMBEDDING_BACKEND=local
EMBEDDING_MODEL_ID=multilingual
EMBEDDING_MODEL_SIZE=768
EMBEDDING_DEVICE=cpu

# Vector DB
VECTOR_DB_BACKEND=PGVECTOR
VECTOR_DB_DISTANCE_METHOD=cosine

# Langue
PRIMARY_LANG=fr
DEFAULT_LANG=en
```

### 3. Configurer PostgreSQL

Éditer `docker/env/.env.postgres` :

```bash
POSTGRES_USER=postgres
POSTGRES_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE
POSTGRES_DB=minirag
```

⚠️ **Important** : Utilisez le **même mot de passe** dans `.env.app` et `.env.postgres`

---

## 🚀 Build et Déploiement

### Option 1 : Déploiement Complet (Recommandé)

```bash
cd docker

# Build et démarrage de tous les services
docker compose up -d --build
```

**Services démarrés** :
- ✅ FastAPI (port 8000) - avec embeddings HuggingFace
- ✅ Frontend React (port 3001)
- ✅ PostgreSQL + PGVector (port 5432)
- ✅ Qdrant (ports 6333, 6334)
- ✅ Nginx (port 80)
- ✅ Prometheus (port 9090)
- ✅ Grafana (port 3000)

### Option 2 : Services Minimaux (Dev/Test)

```bash
# Démarrer uniquement FastAPI + PostgreSQL + Qdrant
docker compose up -d --build fastapi pgvector qdrant
```

### Suivre les Logs

```bash
# Tous les services
docker compose logs -f

# FastAPI uniquement
docker compose logs -f fastapi

# Voir le téléchargement du modèle HuggingFace
docker compose logs -f fastapi | grep -i "downloading\|model"
```

---

## ✅ Vérification

### 1. Vérifier que les Conteneurs Fonctionnent

```bash
docker compose ps
```

Vous devriez voir :

```
NAME                IMAGE                      STATUS
fastapi             fil_rouge-fastapi          Up (healthy)
pgvector            pgvector/pgvector:0.8.1    Up (healthy)
qdrant              qdrant/qdrant:v1.13.6      Up
frontend            fil_rouge-frontend         Up
nginx               nginx:stable-alpine        Up
...
```

### 2. Tester l'API

```bash
# Health check
curl http://localhost:8000/api/v1/

# Devrait retourner: {"message": "Welcome to RAG Finance API"}
```

### 3. Vérifier les Embeddings Locaux

```bash
# Tester que HuggingFace est bien chargé
docker exec fastapi python3 -c "
from services import EmbeddingsService
emb = EmbeddingsService(provider='local', model_name='multilingual')
print(f'✅ Embeddings dimension: {emb.get_embedding_dimension()}')
print(f'✅ Provider: {emb.get_provider_info()}')
"
```

**Résultat attendu** :
```
✅ Embeddings dimension: 768
✅ Provider: {'provider': 'local', 'dimension': 768, 'device': 'cpu'}
```

### 4. Tester le Frontend

Ouvrir dans le navigateur :
- **Frontend** : http://localhost:3001
- **API Swagger** : http://localhost:8000/docs
- **Grafana** : http://localhost:3000 (admin/admin)
- **Prometheus** : http://localhost:9090

---

## 💾 Ressources Système

### Utilisation RAM par Service

| Service | RAM Minimale | RAM Recommandée |
|---------|--------------|-----------------|
| **FastAPI (avec HuggingFace)** | 2 GB | 3 GB |
| PostgreSQL | 256 MB | 512 MB |
| Qdrant | 128 MB | 256 MB |
| Frontend | 64 MB | 128 MB |
| Nginx | 32 MB | 64 MB |
| Prometheus | 256 MB | 512 MB |
| Grafana | 128 MB | 256 MB |
| **TOTAL** | **~3 GB** | **~5 GB** |

### Configuration Docker Desktop

**Windows/Mac** :
1. Docker Desktop → Settings → Resources
2. **Memory** : 8 GB minimum (16 GB recommandé)
3. **CPUs** : 4 minimum
4. **Disk** : 20 GB minimum

### Monitorer l'Utilisation

```bash
# Voir l'utilisation en temps réel
docker stats

# Stats du service FastAPI
docker stats fastapi
```

---

## 🐛 Troubleshooting

### Problème : Build Échoue sur HuggingFace

**Symptôme** :
```
ERROR: Failed to download model
```

**Solution** :
```bash
# Build avec plus de logs
docker compose build --progress=plain fastapi

# Augmenter le timeout
docker compose build --build-arg BUILDKIT_STEP_LOG_MAX_SIZE=-1 fastapi
```

### Problème : Container FastAPI Redémarre en Boucle

**Diagnostic** :
```bash
docker compose logs fastapi
```

**Causes fréquentes** :
1. **Pas assez de RAM**
   ```bash
   # Vérifier
   docker stats fastapi

   # Solution : Augmenter RAM dans docker-compose.yml
   # ou utiliser modèle plus léger
   EMBEDDING_MODEL_ID=multilingual-mini  # 384 dims au lieu de 768
   ```

2. **PostgreSQL pas prêt**
   ```bash
   # Vérifier que PG est healthy
   docker compose ps pgvector

   # Redémarrer
   docker compose restart fastapi
   ```

3. **Variable d'environnement manquante**
   ```bash
   # Vérifier .env.app
   cat docker/env/.env.app
   ```

### Problème : Modèle HuggingFace Téléchargé à Chaque Redémarrage

**Cause** : Volume pas persistant

**Solution** :
```bash
# Vérifier que le volume existe
docker volume ls | grep huggingface

# Si absent, recréer
docker compose down
docker compose up -d --build
```

### Problème : Connexion PostgreSQL Échoue

**Vérifier** :
```bash
# Logs PostgreSQL
docker compose logs pgvector

# Tester connexion
docker exec pgvector psql -U postgres -d minirag -c "SELECT version();"
```

**Solution** :
- Vérifier que mots de passe correspondent dans `.env.app` et `.env.postgres`
- Vérifier `POSTGRES_HOST=pgvector` (nom du service Docker)

### Problème : API Lente au Démarrage

**Normal** : Première requête prend 5-10s
- HuggingFace charge le modèle en mémoire à la première utilisation
- Ensuite : < 100ms par requête

---

## 🌍 Déploiement Production (VPS)

### 1. Prérequis VPS

**Spécifications Minimales** :
- **CPU** : 4 vCPU
- **RAM** : 8 GB
- **Disque** : 40 GB SSD
- **OS** : Ubuntu 22.04 LTS

**Providers recommandés** :
- Hetzner Cloud (~€13/mois)
- DigitalOcean (~$40/mois)
- Contabo (~€10/mois)

### 2. Installation sur VPS

```bash
# 1. Se connecter au VPS
ssh root@votre-vps-ip

# 2. Installer Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Cloner le projet
git clone https://github.com/votre-repo/fil_rouge.git
cd fil_rouge/docker

# 4. Configurer
cp env/.env.example.app env/.env.app
nano env/.env.app  # Éditer la configuration

# 5. Démarrer
docker compose up -d --build

# 6. Vérifier
docker compose ps
docker compose logs -f fastapi
```

### 3. Configuration HTTPS (Production)

Ajouter Certbot pour SSL :

```yaml
# docker-compose.yml
services:
  certbot:
    image: certbot/certbot
    volumes:
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

**Obtenir certificat** :
```bash
docker compose run --rm certbot certonly --webroot \
  --webroot-path=/var/www/certbot \
  -d votre-domaine.com
```

### 4. Sécurité Production

**Checklist** :
- ✅ Changer `SECRET_KEY` (32+ caractères aléatoires)
- ✅ Changer tous les mots de passe par défaut
- ✅ Activer firewall (ufw)
  ```bash
  sudo ufw allow 80/tcp
  sudo ufw allow 443/tcp
  sudo ufw allow 22/tcp
  sudo ufw enable
  ```
- ✅ Configurer backup automatique (bases de données)
- ✅ Configurer monitoring (Grafana alertes)

### 5. Backup Automatique

```bash
# Script backup
#!/bin/bash
# /opt/backup-rag.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"

# Backup PostgreSQL
docker exec pgvector pg_dump -U postgres minirag > $BACKUP_DIR/minirag_$DATE.sql

# Backup volumes
docker run --rm -v fil_rouge_fastapi_data:/data -v $BACKUP_DIR:/backup \
  ubuntu tar czf /backup/fastapi_data_$DATE.tar.gz -C /data .

# Garder 7 derniers jours
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
```

**Cron automatique** :
```bash
crontab -e
# Ajouter : backup tous les jours à 2h
0 2 * * * /opt/backup-rag.sh
```

---

## 📊 Monitoring Production

### Grafana Dashboards

**Accès** : http://votre-vps-ip:3000

**Dashboards recommandés** :
1. **FastAPI Metrics** (déjà configuré)
   - Request rate
   - Response time
   - Error rate

2. **PostgreSQL Metrics**
   - Connections actives
   - Query duration
   - Cache hit rate

3. **System Metrics** (Node Exporter)
   - CPU, RAM, Disk
   - Network I/O

### Alertes

Configurer dans Grafana :
- RAM > 90% → Alerte email
- Disk > 85% → Alerte
- API error rate > 5% → Alerte

---

## 🔄 Maintenance

### Mettre à Jour l'Application

```bash
cd fil_rouge

# Pull dernières modifications
git pull origin main

# Rebuild et redémarrer
cd docker
docker compose down
docker compose up -d --build
```

### Nettoyer Docker

```bash
# Supprimer images inutilisées
docker system prune -a

# Libérer espace (attention : supprime volumes non utilisés)
docker system prune --volumes
```

### Logs Rotation

```bash
# Limiter taille des logs Docker
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Redémarrer Docker
sudo systemctl restart docker
```

---

## 📈 Performances

### Optimisations

**1. Utiliser modèle embeddings plus léger** (si perf insuffisantes) :
```bash
# .env.app
EMBEDDING_MODEL_ID=multilingual-mini  # 384 dims, 2x plus rapide
```

**2. Augmenter workers FastAPI** (si CPU disponible) :
```yaml
# docker-compose.yml
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**3. Activer cache PostgreSQL** :
```sql
-- Augmenter shared_buffers
ALTER SYSTEM SET shared_buffers = '512MB';
```

### Benchmarks Attendus

| Opération | Latence | Throughput |
|-----------|---------|------------|
| Embedding (1 doc) | 20-50ms | ~50 req/s |
| RAG Query | 200-500ms | ~10 req/s |
| Document Upload | 100-200ms | ~20 req/s |

---

## 📝 Résumé Commandes Rapides

```bash
# Build et démarrer
docker compose up -d --build

# Voir les logs
docker compose logs -f fastapi

# Redémarrer un service
docker compose restart fastapi

# Arrêter tout
docker compose down

# Supprimer volumes (ATTENTION: perte de données)
docker compose down -v

# Stats en temps réel
docker stats

# Shell dans container
docker exec -it fastapi bash

# Tests dans container
docker exec fastapi pytest
```

---

## 🎉 Conclusion

Vous avez maintenant :
- ✅ Application RAG complète en Docker
- ✅ Embeddings locaux (gratuit, privacy)
- ✅ Stack de monitoring (Prometheus + Grafana)
- ✅ Prêt pour production VPS

**Besoin d'aide ?** Consultez :
- MIGRATION_LANGCHAIN.md (guide migration)
- src/tests/README.md (tests)
- Issues GitHub du projet

---

**Dernière mise à jour** : 2025-01-18
**Version** : 1.0.0 (LangChain Migration)
