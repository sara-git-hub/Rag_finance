# 🔧 Troubleshooting

> Guide de résolution des problèmes courants
> Dernière mise à jour : Décembre 2025

---

## 📋 Problèmes courants

### Services Docker

#### Ollama ne démarre pas
```bash
# Vérifier logs
docker logs ollama

# Vérifier mémoire
docker stats

# Solution : Réduire limite mémoire dans docker-compose.yml
```

#### FastAPI ne se connecte pas à PostgreSQL
```bash
# Vérifier healthcheck
docker-compose ps

# Tester connexion
docker exec -it pgvector psql -U postgres -d minirag
```

### Application

#### Erreur 401 (Non autorisé)
- Vérifier token JWT dans localStorage
- Vérifier SECRET_KEY dans .env.app
- Se reconnecter

#### Vector search ne retourne rien
- Vérifier l'indexation (/index)
- Vérifier Qdrant collections
- Vérifier chunks en DB

---

## 🚧 EN COURS DE RÉDACTION

Plus de solutions seront ajoutées lors des phases suivantes.
