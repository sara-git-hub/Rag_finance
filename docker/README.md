# Configuration Docker pour l'application MiniRAG

Ce répertoire contient la configuration Docker pour l'application RAG FINANCE, incluant tous les services nécessaires pour le développement et le monitoring.

## Services

- **Application FastAPI** : Application principale exécutée sur Uvicorn
- **Nginx** : Serveur web pour servir l'application FastAPI
- **PostgreSQL (pgvector)** : Base de données avec support vectoriel pour stocker les embeddings
- **Postgres-Exporter** : Exporte les métriques PostgreSQL pour Prometheus
- **Qdrant** : Base de données vectorielle pour la recherche de similarité
- **Prometheus** : Collecte de métriques
- **Grafana** : Dashboard de visualisation des métriques
- **Node-Exporter** : Collecte de métriques système

## Instructions de configuration

### 1. Configurer les fichiers d'environnement

Créez vos fichiers d'environnement à partir des exemples :

```bash
# Créer tous les fichiers .env requis depuis les exemples
cd docker/env
cp .env.example.app .env.app
cp .env.example.postgres .env.postgres
cp .env.example.grafana .env.grafana
cp .env.example.postgres-exporter .env.postgres-exporter

# Configurer Alembic pour l'application FastAPI
cd ..
cd docker/minirag
cp alembic.example.ini alembic.ini
```

### 2. Démarrer les services

```bash
cd docker
docker-compose up --build -d
```

Pour démarrer uniquement des services spécifiques :

```bash
docker-compose up -d fastapi nginx pgvector qdrant
```

Si vous rencontrez des problèmes de connexion, vous pouvez démarrer d'abord les services de base de données et les laisser s'initialiser avant de démarrer l'application :

```bash
# Démarrer d'abord les bases de données
docker compose-up -d pgvector qdrant postgres-exporter
# Attendre que les bases de données soient prêtes
sleep 30
# Démarrer les services d'application
docker-compose up fastapi nginx prometheus grafana node-exporter --build -d
```

En cas de nécessité de supprimer tous les conteneurs et volumes, vous pouvez exécuter :

```bash
docker-compose down -v --remove-orphans
```

### 3. Accéder aux services

- Application FastAPI : http://localhost:8000
- Documentation FastAPI : http://localhost:8000/docs
- Nginx (servant FastAPI) : http://localhost
- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000
- Interface Qdrant : http://localhost:6333/dashboard

## Gestion des volumes

### Gérer les volumes Docker

Les volumes Docker sont utilisés pour persister les données générées et utilisées par les conteneurs Docker. Voici quelques commandes pour gérer vos volumes :

1. **Lister tous les volumes** :
   ```bash
   docker volume ls
   ```
2. **Inspecter un volume** :
   ```bash
   docker volume inspect <nom_volume>
   ```

   - Lister les fichiers dans un volume :
   ```bash
   docker run --rm -v <nom_volume>:/data busybox ls -l /data
   ```

3. **Supprimer un volume** :
   ```bash
   docker volume rm <nom_volume>
   ```
4. **Nettoyer les volumes non utilisés** :
   ```bash
    docker volume prune
    ```

5. **Sauvegarder un volume pour migration** :
   ```bash
    docker run --rm -v <nom_volume>:/volume -v $(pwd):/backup alpine tar cvf /backup/backup.tar /volume
    ```

6. **Restaurer un volume depuis une sauvegarde** :
   ```bash
    docker run --rm -v <nom_volume>:/volume -v $(pwd):/backup alpine sh -c "cd /volume && tar xvf /backup/backup.tar --strip 1"
    ```

7. **Supprimer tous les volumes** :
    ```bash
    docker volume rm $(docker volume ls -q)
    ```

**NOTE** : Pour PostgreSQL spécifiquement, vous pouvez envisager d'utiliser les outils intégrés de PostgreSQL comme `pg_dump` et `pg_restore` pour des sauvegardes plus fiables, en particulier pour les bases de données actives.

## Monitoring

### Métriques FastAPI

FastAPI est configuré pour exposer les métriques Prometheus sur l'endpoint `/metrics`. Ces métriques incluent :

- Nombre de requêtes
- Latences des requêtes
- Codes de statut

Prometheus est configuré pour collecter ces métriques automatiquement.

### Visualiser les métriques dans Grafana

1. Connectez-vous à Grafana sur http://localhost:3000 (identifiants par défaut : admin/admin_password)
2. Ajoutez Prometheus comme source de données (URL : http://prometheus:9090)
3. Importez des dashboards pour FastAPI, PostgreSQL et Qdrant

#### URLs des dashboards

https://grafana.com/grafana/dashboards/18739-fastapi-observability/

https://grafana.com/grafana/dashboards/1860-node-exporter-full/

https://grafana.com/grafana/dashboards/23033-qdrant/

https://grafana.com/grafana/dashboards/12485-postgresql-exporter/


## Flux de développement

L'application FastAPI est configurée avec le rechargement automatique. Toute modification du code dans le répertoire `src/` rechargera automatiquement l'application.

## Dépannage

### Erreurs de connexion

Si vous rencontrez des erreurs de connexion au démarrage des services :

1. **Connexion à la base de données refusée** : Cela se produit souvent lorsque l'application FastAPI tente de se connecter aux bases de données avant qu'elles ne soient prêtes.
   ```
   Connection refused: [Errno 111] Connection refused
   ```

   Solutions :
   - Démarrer d'abord les services de base de données, attendre, puis démarrer l'application
   - Vérifier les logs de la base de données : `docker compose logs pgvector`
   - Assurez-vous que vos identifiants de base de données dans `.env.app` correspondent à ceux dans `.env.postgres`

2. **Redémarrer le service FastAPI** après que les bases de données sont en cours d'exécution :
   ```bash
   docker-compose restart fastapi
   ```

3. **Vérifier le statut des services** :
   ```bash
   docker-compose ps
   ```

4. **Voir les logs** pour plus de détails :
   ```bash
   docker-compose logs --tail=100 fastapi
   docker-compose logs --tail=100 pgvector
   ```
