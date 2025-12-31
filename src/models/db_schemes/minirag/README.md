## Exécuter les migrations Alembic

### Configuration

```bash
cp alembic.ini.example alembic.ini
```

- Mettre à jour `alembic.ini` avec vos identifiants de base de données (`sqlalchemy.url`)

### (Optionnel) Créer une nouvelle migration

```bash
alembic revision --autogenerate -m "Add ..."
```

### Mettre à jour la base de données

```bash
alembic upgrade head
```

## Exécuter les migrations avec Docker

Lorsque vous utilisez Docker, exécutez les migrations depuis le conteneur FastAPI pour éviter les problèmes de résolution DNS (`pgvector`):

### Créer une nouvelle migration

```bash
docker exec fastapi bash -c "cd models/db_schemes/minirag && alembic revision -m 'description_de_la_migration'"
```

### Appliquer les migrations

```bash
docker exec fastapi bash -c "cd models/db_schemes/minirag && alembic upgrade head"
```

### Vérifier la version actuelle

```bash
docker exec fastapi bash -c "cd models/db_schemes/minirag && alembic current"
```