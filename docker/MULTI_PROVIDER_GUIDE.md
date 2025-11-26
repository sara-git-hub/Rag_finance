# 🎯 Guide Multi-Providers - OpenAI, Cohere, Ollama, Groq

Guide pour utiliser votre application RAG avec 4 providers LLM différents.

---

## ✅ Ce qui a été configuré

### 1. **Fichier .env Multi-Providers**
- Location : `docker/env/.env.app`
- Contient les configurations pour les 4 providers
- Permet de changer facilement entre providers

### 2. **Code Modifié**
- `requirements.txt` : Dépendances pour Ollama et Groq ajoutées
- `rag_service.py` : Support des 4 providers intégré
- `docker-compose.yml` : Service Ollama ajouté

### 3. **Services Docker**
- ✅ Ollama : Running (port 11434)
- ✅ FastAPI : Running (port 8000)
- ✅ PostgreSQL : Running (port 5432)
- ✅ Frontend : Running (port 3001)

---

## 🔄 Comment Changer de Provider

### Méthode Simple : Modifier `.env.app`

Éditez le fichier `docker/env/.env.app` et changez ces deux lignes :

```bash
# Pour OpenAI (PAYANT)
GENERATION_BACKEND=openai
GENERATION_MODEL_ID=gpt-3.5-turbo-0125
OPENAI_API_KEY=sk-votre-cle-ici

# Pour Cohere (GRATUIT - nécessite clé API de génération)
GENERATION_BACKEND=cohere
GENERATION_MODEL_ID=command-r
COHERE_API_KEY=votre-cle-ici

# Pour Ollama (100% GRATUIT & LOCAL)
GENERATION_BACKEND=ollama
GENERATION_MODEL_ID=mistral
# Pas besoin de clé API !

# Pour Groq (GRATUIT & RAPIDE)
GENERATION_BACKEND=groq
GENERATION_MODEL_ID=llama-3.1-70b-versatile
GROQ_API_KEY=votre-cle-gratuite-ici
```

Après modification, redémarrez FastAPI :
```bash
cd docker
docker compose restart fastapi
```

---

## 📋 Comparaison des Providers

| Provider | Coût | Vitesse | Privacy | Installation | Quota Gratuit |
|----------|------|---------|---------|--------------|---------------|
| **OpenAI** | 💰 Payant | ⚡⚡ | ❌ Cloud | Aucune | Payant |
| **Cohere** | 💰 Payant | ⚡⚡ | ❌ Cloud | Aucune | Trial limité |
| **Groq** | 🆓 Gratuit | ⚡⚡⚡⚡ | ❌ Cloud | Aucune | 14,400 req/jour |
| **Ollama** | 🆓 Gratuit | ⚡⚡⚡ | ✅ Local | Docker (~6GB) | Illimité |

---

## 🦙 Utiliser Ollama (Local - Recommandé pour Dev)

### Avantages
- ✅ **100% Gratuit** - Pas de limite, pas de clé API
- ✅ **Privacy** - Données restent en local
- ✅ **Offline** - Fonctionne sans internet
- ✅ **Pas de quota** - Utilisez autant que vous voulez

### 1. Vérifier qu'Ollama est démarré

```bash
docker compose ps ollama
```

Devrait afficher : `STATUS: Up`

### 2. Télécharger un modèle

```bash
# Mistral 7B (4GB - Recommandé)
docker exec ollama ollama pull mistral

# Llama 3.1 8B (4.7GB - Très bon)
docker exec ollama ollama pull llama3.1

# Gemma 2 9B (5.4GB - Performant)
docker exec ollama ollama pull gemma2:9b

# Phi 3 (2.3GB - Rapide et léger)
docker exec ollama ollama pull phi3
```

### 3. Lister les modèles disponibles

```bash
docker exec ollama ollama list
```

### 4. Tester directement

```bash
docker exec ollama ollama run mistral "Bonjour, qui es-tu ?"
```

### 5. Utiliser dans votre application

Éditez `.env.app` :
```bash
GENERATION_BACKEND=ollama
GENERATION_MODEL_ID=mistral  # ou llama3.1, gemma2:9b, phi3
```

Redémarrez :
```bash
docker compose restart fastapi
```

---

## ⚡ Utiliser Groq (Rapide - Gratuit)

### Avantages
- ✅ **Gratuit** - 14,400 requêtes/jour
- ✅ **Très rapide** - Inférence ultra-optimisée
- ✅ **Pas d'installation** - Juste une clé API

### 1. Obtenir une clé API gratuite

1. Aller sur https://console.groq.com/keys
2. Créer un compte (gratuit)
3. Générer une clé API

### 2. Configurer

Éditez `.env.app` :
```bash
GENERATION_BACKEND=groq
GENERATION_MODEL_ID=llama-3.1-70b-versatile
GROQ_API_KEY=gsk_votre_cle_ici
```

### 3. Modèles disponibles

| Modèle | Taille | Vitesse | Qualité |
|--------|--------|---------|---------|
| `llama-3.1-70b-versatile` | 70B | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| `llama-3.1-8b-instant` | 8B | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |
| `mixtral-8x7b-32768` | 46B | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| `gemma2-9b-it` | 9B | ⚡⚡⚡⚡ | ⭐⭐⭐⭐ |

### 4. Redémarrer

```bash
docker compose restart fastapi
```

---

## 🔑 Utiliser OpenAI

### 1. Obtenir une clé API

1. Créer un compte sur https://platform.openai.com/
2. Ajouter un moyen de paiement
3. Générer une clé API

### 2. Configurer

Éditez `.env.app` :
```bash
GENERATION_BACKEND=openai
GENERATION_MODEL_ID=gpt-3.5-turbo-0125  # ou gpt-4o-mini, gpt-4o
OPENAI_API_KEY=sk-votre-cle-ici
```

### 3. Modèles disponibles

| Modèle | Prix | Qualité |
|--------|------|---------|
| `gpt-3.5-turbo-0125` | $0.0005/1K tokens | ⭐⭐⭐ |
| `gpt-4o-mini` | $0.00015/1K tokens | ⭐⭐⭐⭐ |
| `gpt-4o` | $0.0025/1K tokens | ⭐⭐⭐⭐⭐ |

---

## 🧪 Tester l'Application

### 1. Vérifier que l'API fonctionne

```bash
curl http://localhost:8000/api/v1/
```

### 2. Voir les logs

```bash
# Logs FastAPI
docker compose logs -f fastapi

# Logs Ollama
docker compose logs -f ollama
```

### 3. Tester une question RAG

Via l'interface Web : http://localhost:3001

Ou via API :
```bash
curl -X POST "http://localhost:8000/api/v1/rag/question" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test",
    "question": "Teste le provider actuel"
  }'
```

---

## 🔧 Troubleshooting

### Ollama : "Model not found"

```bash
# Lister les modèles
docker exec ollama ollama list

# Si vide, télécharger un modèle
docker exec ollama ollama pull mistral
```

### FastAPI : "Connection refused to Ollama"

```bash
# Vérifier qu'Ollama tourne
docker compose ps ollama

# Redémarrer si nécessaire
docker compose restart ollama
docker compose restart fastapi
```

### Groq/OpenAI : "Authentication error"

- Vérifier que la clé API est correcte dans `.env.app`
- S'assurer qu'elle commence par `gsk_` (Groq) ou `sk-` (OpenAI)
- Redémarrer FastAPI après modification

### Changer de provider ne fonctionne pas

1. Vérifier que `.env.app` est bien modifié
2. **Redémarrer FastAPI** :
   ```bash
   docker compose restart fastapi
   ```
3. Vérifier les logs :
   ```bash
   docker compose logs fastapi
   ```

---

## 💡 Conseils d'Utilisation

### Pour le Développement
✅ **Recommandé : Ollama** (Mistral ou Llama 3.1)
- Gratuit, illimité
- Bonne qualité
- Pas de dépendance internet

### Pour le Production (Budget limité)
✅ **Recommandé : Groq** (Llama 3.1 70B)
- Gratuit avec quota généreux
- Très rapide
- Bonne qualité

### Pour la Production (Budget)
✅ **Recommandé : OpenAI** (GPT-4o-mini)
- Meilleure qualité
- Fiable et stable
- Support officiel

---

## 📚 Ressources

- **Ollama** : https://ollama.com
  - Liste modèles : https://ollama.com/library

- **Groq** : https://console.groq.com
  - Documentation : https://console.groq.com/docs

- **OpenAI** : https://platform.openai.com
  - Pricing : https://openai.com/pricing

---

## ✅ Checklist de Configuration

- [ ] Service Ollama démarré (`docker compose ps ollama`)
- [ ] Au moins un modèle Ollama téléchargé (`ollama list`)
- [ ] `.env.app` configuré avec le provider choisi
- [ ] FastAPI redémarré (`docker compose restart fastapi`)
- [ ] API testée (`curl http://localhost:8000/api/v1/`)
- [ ] Question RAG testée via l'interface ou API

---

**Date de création** : 2025-01-19
**Providers supportés** : OpenAI, Cohere, Ollama, Groq
**Status** : ✅ Production Ready
