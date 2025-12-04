# 🦙 Guide Ollama - LLM Gratuit et Local

Guide complet pour utiliser **Ollama** (100% gratuit) avec votre application RAG au lieu d'OpenAI.

---

## 🎯 Avantages d'Ollama

✅ **100% Gratuit** - Pas de clé API, pas de limite
✅ **Privacy** - Données restent locales
✅ **Offline** - Fonctionne sans internet
✅ **Pas de quota** - Utilisez autant que vous voulez
✅ **Multi-modèles** - Llama, Mistral, Gemma, etc.

---

## 🚀 Démarrage Rapide (3 étapes)

### Étape 1 : Utiliser le fichier .env pour Ollama

```bash
cd docker/env

# Remplacer .env.app par la version Ollama
cp .env.app.ollama .env.app
```

### Étape 2 : Démarrer les services Docker

```bash
cd docker

# Démarrer tous les services (y compris Ollama)
docker compose up -d --build
```

**Services démarrés** :
- ✅ Ollama (port 11434)
- ✅ FastAPI (port 8000)
- ✅ PostgreSQL + PGVector (port 5432)
- ✅ Frontend (port 3001)

### Étape 3 : Télécharger un modèle

**Option A : Avec le script automatique** (recommandé)
```bash
# Rendre le script exécutable
chmod +x docker/init-ollama.sh

# Lancer le téléchargement
./docker/init-ollama.sh
```

**Option B : Manuellement**
```bash
# Télécharger Mistral (recommandé, 4GB)
docker exec ollama ollama pull mistral

# Vérifier que c'est installé
docker exec ollama ollama list
```

---

## ✅ Vérification

### 1. Vérifier qu'Ollama fonctionne

```bash
# Tester Ollama directement
docker exec ollama ollama run mistral "Bonjour, qui es-tu?"
```

**Résultat attendu** :
```
Bonjour! Je suis Mistral, un assistant IA...
```

### 2. Tester l'API FastAPI

```bash
# Health check
curl http://localhost:8000/api/v1/

# Test de génération (via votre API)
curl -X POST "http://localhost:8000/api/v1/rag/question" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test",
    "question": "Teste Ollama"
  }'
```

### 3. Vérifier les logs

```bash
# Voir les logs Ollama
docker compose logs -f ollama

# Voir les logs FastAPI
docker compose logs -f fastapi
```

---

## 🤖 Modèles Disponibles

| Modèle | Taille | Langues | RAM | Vitesse | Recommandation |
|--------|--------|---------|-----|---------|----------------|
| **mistral** | 7B (4GB) | FR/EN/ES/IT | 8GB | ⚡⚡⚡ | **✅ Recommandé** |
| **llama3.1** | 8B (4.7GB) | Multi | 10GB | ⚡⚡ | Très bon |
| **gemma2:9b** | 9B (5.4GB) | Multi | 12GB | ⚡⚡ | Performant |
| **qwen2.5** | 7B (4.5GB) | Multi | 8GB | ⚡⚡⚡ | Très rapide |
| **phi3** | 3.8B (2.3GB) | EN | 6GB | ⚡⚡⚡⚡ | Ultra rapide |

### Changer de modèle

**1. Télécharger le nouveau modèle**
```bash
docker exec ollama ollama pull llama3.1
```

**2. Modifier `.env.app`**
```bash
# Éditer docker/env/.env.app
GENERATION_MODEL_ID=llama3.1
```

**3. Redémarrer FastAPI**
```bash
docker compose restart fastapi
```

---

## 📊 Performances

### Temps de Réponse Typiques

| Opération | Latence | Notes |
|-----------|---------|-------|
| Première question | 5-10s | Chargement du modèle en mémoire |
| Questions suivantes | 1-3s | Dépend de la taille du contexte |
| Embeddings (local) | 50-100ms | HuggingFace |

### Optimiser les Performances

**1. Utiliser un modèle plus petit**
```bash
# Phi3 est 2x plus rapide que Mistral
GENERATION_MODEL_ID=phi3
```

**2. Réduire la longueur des réponses**
```bash
# .env.app
GENERATION_DEFAULT_MAX_TOKENS=500  # au lieu de 1000
```

**3. Augmenter la RAM Docker**
```yaml
# docker-compose.yml → service ollama
deploy:
  resources:
    limits:
      memory: 12G  # Si vous avez la RAM disponible
```

---

## 🐛 Troubleshooting

### Problème : "Ollama connection refused"

**Cause** : Ollama pas encore démarré

**Solution** :
```bash
# Vérifier le status
docker compose ps ollama

# Redémarrer
docker compose restart ollama

# Vérifier les logs
docker compose logs ollama
```

### Problème : "Model not found"

**Cause** : Modèle pas téléchargé

**Solution** :
```bash
# Lister les modèles disponibles
docker exec ollama ollama list

# Si vide, télécharger
docker exec ollama ollama pull mistral
```

### Problème : Container Ollama arrêté (OOMKilled)

**Cause** : Pas assez de RAM

**Solutions** :
1. **Utiliser un modèle plus petit**
   ```bash
   docker exec ollama ollama pull phi3
   GENERATION_MODEL_ID=phi3
   ```

2. **Augmenter RAM Docker**
   - Docker Desktop → Settings → Resources
   - Memory: 12 GB minimum (16 GB recommandé)

3. **Libérer de la RAM**
   ```bash
   # Arrêter services non essentiels
   docker compose stop prometheus grafana
   ```

### Problème : Réponses très lentes

**Diagnostic** :
```bash
# Voir l'utilisation ressources
docker stats ollama
```

**Solutions** :
- Modèle plus léger (phi3)
- Réduire `GENERATION_DEFAULT_MAX_TOKENS`
- Allouer plus de CPU à Docker

---

## 🔄 Comparaison avec OpenAI

| Critère | Ollama (Mistral) | OpenAI (GPT-4) |
|---------|------------------|----------------|
| **Prix** | 🆓 Gratuit | 💰 $0.03/1K tokens |
| **Latence** | 2-3s | 1-2s |
| **Qualité** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Privacy** | ✅ Local | ❌ Cloud |
| **Offline** | ✅ Oui | ❌ Non |
| **Limite** | ∞ | Quota payant |

**Verdict** : Ollama parfait pour développement et petit-medium usage !

---

## 🌐 Utiliser Ollama en Production (VPS)

### Prérequis VPS

- **CPU** : 4+ vCPU
- **RAM** : 12 GB minimum (16 GB recommandé)
- **Disque** : 50 GB SSD
- **OS** : Ubuntu 22.04 LTS

### Déploiement

```bash
# 1. Se connecter au VPS
ssh root@votre-vps-ip

# 2. Cloner le projet
git clone https://github.com/votre-repo/fil_rouge.git
cd fil_rouge/docker

# 3. Configurer
cp env/.env.app.ollama env/.env.app

# 4. Démarrer
docker compose up -d --build

# 5. Télécharger modèle
docker exec ollama ollama pull mistral

# 6. Tester
curl http://localhost:8000/api/v1/
```

### Providers VPS Recommandés

| Provider | Config | Prix/mois |
|----------|--------|-----------|
| **Hetzner** | CPX41 (8 vCPU, 16GB) | ~€20 |
| **Contabo** | Cloud VPS L (10 vCPU, 30GB) | ~€25 |
| **DigitalOcean** | Premium 16GB | ~$60 |

---

## 📝 Commandes Utiles

```bash
# ========== Gestion des modèles ==========
# Lister modèles installés
docker exec ollama ollama list

# Télécharger un modèle
docker exec ollama ollama pull <nom-modele>

# Supprimer un modèle
docker exec ollama ollama rm <nom-modele>

# ========== Tests ==========
# Tester un modèle directement
docker exec -it ollama ollama run mistral "Bonjour!"

# Tester via curl
curl http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Bonjour, qui es-tu?",
  "stream": false
}'

# ========== Monitoring ==========
# Voir utilisation ressources Ollama
docker stats ollama

# Logs Ollama
docker compose logs -f ollama

# Taille des modèles
docker exec ollama du -sh /root/.ollama/models

# ========== Maintenance ==========
# Redémarrer Ollama
docker compose restart ollama

# Reconstruire avec nouvelle version
docker compose pull ollama
docker compose up -d ollama
```

---

## 🎓 Exemples d'Utilisation

### Exemple 1 : Question RAG Simple

```python
# Dans votre code Python ou via API
from services import create_rag_service, VectorStoreService, EmbeddingsService

# Embeddings locaux
embeddings = EmbeddingsService(provider="local")

# Vector store
vectorstore = VectorStoreService(
    embeddings=embeddings.embeddings,
    provider="qdrant",
    collection_name="test"
)

# RAG avec Ollama
rag = create_rag_service(
    vectorstore_service=vectorstore,
    llm_provider="ollama",
    model_name="mistral",
    language="fr"
)

# Poser une question
result = rag.answer("Qu'est-ce que le RAG?")
print(result["answer"])
```

### Exemple 2 : Via API REST

```bash
# Upload d'un document
curl -X POST "http://localhost:8000/api/v1/projects/test/documents" \
  -F "file=@document.pdf"

# Poser une question
curl -X POST "http://localhost:8000/api/v1/rag/question" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test",
    "question": "Résume le document"
  }'
```

---

## 📚 Ressources

- **Ollama** : https://ollama.com
- **Liste modèles** : https://ollama.com/library
- **LangChain Ollama** : https://python.langchain.com/docs/integrations/chat/ollama
- **Docker Hub** : https://hub.docker.com/r/ollama/ollama

---

## ✅ Checklist de Configuration

- [ ] Service Ollama ajouté à `docker-compose.yml`
- [ ] `langchain-ollama` dans `requirements.txt`
- [ ] `rag_service.py` modifié pour supporter Ollama
- [ ] `.env.app` configuré avec `GENERATION_BACKEND=ollama`
- [ ] Services Docker démarrés (`docker compose up -d`)
- [ ] Modèle téléchargé (`ollama pull mistral`)
- [ ] API testée avec succès

---

**Dernière mise à jour** : 2025-01-19
**Version** : 1.0.0 (Ollama Integration)

---

## 🎉 Conclusion

Vous avez maintenant :
- ✅ LLM gratuit et illimité (Ollama)
- ✅ Embeddings gratuits (HuggingFace)
- ✅ Privacy totale (100% local)
- ✅ Aucun coût d'API

**Prêt à tester votre application RAG gratuitement ! 🚀**
