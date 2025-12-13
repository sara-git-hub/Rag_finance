## 🚀 Installation

### Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt
venv\Scripts\activate  # Windows
```

### Installer les dépendances

```bash
# Option 1: Si vous avez une erreur avec pip, utilisez cette commande (recommandée):
.\venv\Scripts\python.exe -m pip install --only-binary=:all: -r requirements.txt

# Option 2: Si la première option ne fonctionne pas, essayez:
pip install -r requirements.txt
```
pip freeze > requirements.txt

### Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## 🧪 Tests

### Lancer les tests unitaires

```bash
# Lancer tous les tests unitaires
cd tests
pytest unit/ -v

# Lancer les tests avec la couverture
pytest unit/ -v --cov=../src --cov-report=term-missing

# Lancer les tests avec rapport XML (pour CI/CD)
pytest unit/ -v --cov=../src --cov-report=xml
```

### Structure des tests

```
tests/
├── unit/
│   ├── controllers/    # Tests des contrôleurs
│   ├── helpers/        # Tests des helpers (auth, etc.)
│   ├── models/         # Tests des modèles de base de données
│   └── services/       # Tests des services (RAG, embeddings, etc.)
├── conftest.py         # Configuration pytest et fixtures
└── pytest.ini          # Configuration pytest
```

## 🔄 CI/CD

Ce projet utilise GitHub Actions pour l'intégration continue.

### Workflow Tests Unitaires

Le workflow `.github/workflows/unit-tests.yml` s'exécute automatiquement:
- À chaque push sur les branches `main` et `develop`
- À chaque pull request vers ces branches

**Ce qu'il fait:**
1. Configure Python 3.12
2. Installe les dépendances depuis `requirements.txt`
3. Exécute les tests unitaires avec pytest
4. Génère un rapport de couverture
5. Upload les résultats vers Codecov (optionnel)
6. Ajoute un commentaire sur les PR avec le pourcentage de couverture

### Configuration Codecov (optionnel)

Pour activer l'upload vers Codecov:
1. Créez un compte sur [codecov.io](https://codecov.io)
2. Ajoutez votre repository
3. Ajoutez le secret `CODECOV_TOKEN` dans les settings GitHub de votre repo:
   - Allez dans Settings > Secrets and variables > Actions
   - Créez un nouveau secret nommé `CODECOV_TOKEN`
   - Collez le token fourni par Codecov

### Voir les résultats

- Les résultats des tests sont visibles dans l'onglet **Actions** de votre repository GitHub
- Les pull requests affichent automatiquement le statut des tests
- Le pourcentage de couverture est commenté sur chaque PR