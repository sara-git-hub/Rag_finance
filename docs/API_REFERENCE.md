# 🔌 API Reference

> Référence complète des endpoints de l'API FastAPI
> Dernière mise à jour : Décembre 2025

---

## 📋 Table des matières

1. [Base](#base)
2. [Authentication](#authentication)
3. [Data Management](#data-management)
4. [NLP / RAG](#nlp--rag)
5. [Conversations](#conversations)
6. [Exchange Rates](#exchange-rates)
7. [Admin](#admin)

---

## 🚧 EN COURS DE DOCUMENTATION

Cette section sera complétée lors de la **Phase 2 : Analyse Backend**.

Pour l'instant, voici une liste sommaire des endpoints disponibles :

### Base
- `GET /health` - Health check

### Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/auth/users` (admin)

### Data Management
- `POST /api/v1/data/upload/{project_id}` (admin)
- `POST /api/v1/data/process/{project_id}` (admin)
- `GET /api/v1/data/project/{project_id}/language`
- `PUT /api/v1/data/project/{project_id}/language` (admin)

### NLP / RAG
- `POST /api/v1/nlp/index/push/{project_id}` (admin)
- `GET /api/v1/nlp/index/info/{project_id}` (admin)
- `POST /api/v1/nlp/index/search/{project_id}`
- `POST /api/v1/nlp/index/answer/{project_id}`

### Conversations
- `POST /api/v1/conversations/create`
- `GET /api/v1/conversations/project/{project_id}`
- `GET /api/v1/conversations/{conv_id}/messages`
- `DELETE /api/v1/conversations/{conv_id}`

### Exchange Rates
- `GET /api/v1/exchange-rates/latest`
- `GET /api/v1/exchange-rates/predictions`
- `GET /api/v1/exchange-rates/history`
- `POST /api/v1/exchange-rates/admin/train-model` (admin)
- `POST /api/v1/exchange-rates/admin/generate-predictions` (admin)

### Admin
- `GET /api/v1/admin/projects`
- `DELETE /api/v1/admin/projects/{id}`
- `GET /api/v1/admin/assets`
- `DELETE /api/v1/admin/assets/{id}`
- (+ chunks, conversations, messages, vectors, exchange-rates)

---

**Documentation détaillée à venir** lors de la Phase 2.
