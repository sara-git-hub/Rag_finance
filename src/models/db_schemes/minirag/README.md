## Run Alembic Migrations

### Configuration

```bash
cp alembic.ini.example alembic.ini
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)
  
### (Optional) Create a new migration

```bash
alembic revision --autogenerate -m "Add ..."
```

### Upgrade the database

```bash
alembic upgrade head
```

## Run Migrations with Docker

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