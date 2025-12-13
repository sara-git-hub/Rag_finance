# Tests - Fil Rouge

Suite de tests complète pour le projet Fil Rouge.

## 📁 Structure

```
tests/
├── unit/                      # Tests unitaires (238 tests)
│   ├── services/             # Tests services LangChain
│   │   ├── test_document_service.py        (20 tests - 100% coverage)
│   │   ├── test_embeddings_service.py      (35 tests - 100% coverage)
│   │   ├── test_prompt_service.py          (30 tests - 100% coverage)
│   │   ├── test_rag_service.py             (23 tests - 46% coverage)
│   │   └── test_vectorstore_service.py     (20 tests - 68% coverage)
│   ├── controllers/          # Tests controllers (58 tests)
│   │   ├── test_base_controller.py         (17 tests - 100% coverage)
│   │   ├── test_data_controller.py         (20 tests - 100% coverage)
│   │   ├── test_nlp_controller.py          (11 tests - 33% coverage)
│   │   ├── test_process_controller.py      (14 tests - 100% coverage)
│   │   └── test_project_controller.py      (6 tests - 100% coverage)
│   ├── helpers/              # Tests helpers/utils (16 tests)
│   │   └── test_auth.py                    (16 tests - 100% coverage)
│   └── models/               # Tests modèles DB (19 tests)
│       ├── test_asset_model.py             (7 tests - 100% coverage)
│       ├── test_chunk_model.py             (6 tests - 100% coverage)
│       └── test_project_model.py           (6 tests - 100% coverage)
├── integration/              # Tests d'intégration (à créer)
│   └── test_routes.py        # Tests API endpoints (à créer)
├── ml/                       # Tests Machine Learning (à créer)
│   └── test_lstm_model.py    # Tests LSTM (à créer)
├── conftest.py               # Fixtures globales
├── pytest.ini                # Configuration pytest
├── ANALYSE_TESTS_ACTUELS.md  # Rapport d'analyse
└── README.md                 # Ce fichier
```

## 🚀 Lancer les tests

### Tous les tests
```bash
cd tests
pytest
```

### Tests unitaires seulement
```bash
pytest unit/
```

### Tests services LangChain
```bash
pytest unit/services/
```

### Tests par marker
```bash
# Tests unitaires
pytest -m unit

# Tests d'intégration
pytest -m integration

# Tests ML
pytest -m ml

# Tests rapides (exclure les lents)
pytest -m "not slow"
```

### Tests avec couverture
```bash
# Rapport dans le terminal
pytest --cov

# Rapport HTML
pytest --cov --cov-report=html
# Ouvrir: htmlcov/index.html
```

### Tests spécifiques
```bash
# Un fichier
pytest unit/services/test_rag_service.py

# Une classe
pytest unit/services/test_rag_service.py::TestRAGService

# Un test
pytest unit/services/test_rag_service.py::TestRAGService::test_answer_with_sources
```

## 📊 Couverture Actuelle

| Catégorie | Fichiers | Couverture | Tests | Cible |
|-----------|----------|------------|-------|-------|
| **Services (LangChain)** | 5/5 | **82%** | 128 | 80% ✅ |
| - DocumentService | 1/1 | 100% ✅ | 20 | - |
| - EmbeddingsService | 1/1 | 100% ✅ | 35 | - |
| - PromptService | 1/1 | 100% ✅ | 30 | - |
| - RAGService | 1/1 | 46% | 23 | - |
| - VectorStoreService | 1/1 | 68% | 20 | - |
| **Controllers** | 5/5 | **87%** | 58 | 70% ✅ |
| - BaseController | 1/1 | 100% ✅ | 17 | - |
| - DataController | 1/1 | 100% ✅ | 20 | - |
| - ProcessController | 1/1 | 100% ✅ | 14 | - |
| - ProjectController | 1/1 | 100% ✅ | 6 | - |
| - NLPController | 1/1 | 33% | 11 | - |
| **Helpers** | 1/1 | **100%** ✅ | 16 | 80% ✅ |
| - auth.py | 1/1 | 100% ✅ | 16 | - |
| **Modèles DB** | 3/4 | **100%** ✅ | 19 | 70% ✅ |
| - Asset | 1/1 | 100% ✅ | 7 | - |
| - Chunk | 1/1 | 100% ✅ | 6 | - |
| - Project | 1/1 | 100% ✅ | 6 | - |
| - User | 0/1 | 0% | 0 | - |
| **Routes/Endpoints** | 0/6 | **0%** | 0 | 75% |
| **ML (LSTM)** | 0/1 | **0%** | 0 | 60% |
| **TOTAL** | **15/23** | **~21%** | **221** | **75%** |

**Légende**: ✅ = Objectif atteint | 🟡 = En cours | ❌ = Non commencé

## 🎯 Priorités

### ✅ Phase 1 - Complétée (128 tests)
- ✅ Tests services LangChain (128 tests, 82% couverture)
  - DocumentService: 20 tests, 100% ✅
  - EmbeddingsService: 35 tests, 100% ✅
  - PromptService: 30 tests, 100% ✅
  - RAGService: 23 tests, 46%
  - VectorStoreService: 20 tests, 68%
- ✅ Fixtures de base (conftest.py)

### ✅ Phase 2 - Complétée (93 tests)
- ✅ Tests Controllers (58 tests, 87% couverture)
  - BaseController: 17 tests, 100% ✅
  - DataController: 20 tests, 100% ✅
  - ProcessController: 14 tests, 100% ✅
  - ProjectController: 6 tests, 100% ✅
  - NLPController: 11 tests, 33%
- ✅ Tests Helpers (16 tests, 100% couverture)
  - auth.py: 16 tests, 100% ✅
- ✅ Tests Modèles DB (19 tests, 100% couverture)
  - Asset: 7 tests, 100% ✅
  - Chunk: 6 tests, 100% ✅
  - Project: 6 tests, 100% ✅

### 🔴 Phase 3 - PRIORITAIRE
1. **Tests Endpoints API** (integration/) - 0% couverture
   - Authentification (login, register, JWT)
   - Upload et traitement fichiers
   - RAG Q&A
   - Admin CRUD
   - Gestion projets

2. **Tests Machine Learning** (ml/) - 0% couverture
   - LSTM Exchange Rates
   - Prédictions
   - Entraînement modèle

### 🟡 Phase 4 - Amélioration Continue
- Améliorer RAGService (46% → 80%)
- Améliorer VectorStoreService (68% → 80%)
- Améliorer NLPController (33% → 70%)
- Ajouter tests User model

## 🔄 CI/CD - Intégration Continue

### ✅ GitHub Actions Configuré

Le projet utilise GitHub Actions pour l'exécution automatique des tests:

**Workflow**: `.github/workflows/unit-tests.yml`

**Déclenchement**:
- Push sur `main` ou `develop`
- Pull Requests vers `main` ou `develop`

**Exécution**:
1. Configuration Python 3.12
2. Installation des dépendances (`requirements.txt`)
3. Exécution des tests unitaires avec pytest
4. Génération du rapport de couverture (XML)
5. Upload vers Codecov (optionnel, nécessite `CODECOV_TOKEN`)
6. Commentaire automatique sur les PR avec le % de couverture

**Voir les résultats**:
- Onglet **Actions** sur GitHub
- Badge de statut sur les PR
- Rapport de couverture commenté sur chaque PR

**Commandes exécutées**:
```bash
cd tests
pytest unit/ -v --cov=../src --cov-report=xml --cov-report=term-missing
```

### Configuration Locale

Pour tester le workflow localement avant de push:

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer les tests comme le CI/CD
cd tests
pytest unit/ -v --cov=../src --cov-report=xml --cov-report=term-missing

# Vérifier le fichier coverage.xml généré
ls -lh coverage.xml
```

## 🔧 Fixtures Disponibles

### Fixtures globales (conftest.py)

```python
@pytest.fixture(scope="session")
def test_data_dir():
    """Répertoire temporaire pour tests"""

@pytest.fixture
def sample_documents():
    """Documents de test LangChain"""

@pytest.fixture
def openai_api_key():
    """Clé API OpenAI (skip si absente)"""

@pytest.fixture
def test_project_id():
    """ID projet de test"""
```

### À créer

```python
@pytest.fixture
def test_db_session():
    """Session DB de test (SQLite en mémoire)"""

@pytest.fixture
def test_client():
    """Client FastAPI pour tests API"""

@pytest.fixture
def admin_token():
    """Token JWT admin pour tests"""

@pytest.fixture
def test_project():
    """Projet de test complet"""
```

## 📝 Conventions

### Nommage
- Fichiers: `test_*.py`
- Classes: `Test*`
- Fonctions: `test_*`

### Organisation
```python
class TestUserModel:
    """Test suite for User model"""

    def test_create_user(self):
        """Test user creation"""
        # Arrange
        user_data = {"username": "test", ...}

        # Act
        user = create_user(user_data)

        # Assert
        assert user.username == "test"
```

### Markers
```python
@pytest.mark.unit
def test_service():
    """Test unitaire"""

@pytest.mark.integration
@pytest.mark.slow
def test_api_endpoint():
    """Test d'intégration lent"""

@pytest.mark.ml
def test_lstm_prediction():
    """Test ML"""
```

## 🐛 Debug

### Verbose
```bash
pytest -v
pytest -vv  # Extra verbose
```

### Arrêt au premier échec
```bash
pytest -x
```

### Relancer les tests échoués
```bash
pytest --lf  # Last failed
pytest --ff  # Failed first
```

### Afficher print()
```bash
pytest -s
```

### Debug avec breakpoint
```python
def test_something():
    result = complex_function()
    breakpoint()  # Pause ici
    assert result == expected
```

## 📚 Documentation

- [Analyse complète](./ANALYSE_TESTS_ACTUELS.md)
- [Recommandations](../docs/phases/06_RECOMMENDATIONS.md)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)

## ✅ Checklist Nouveau Test

- [ ] Fichier dans le bon dossier
- [ ] Nom commence par `test_`
- [ ] Docstrings claires
- [ ] Markers appropriés
- [ ] Fixtures utilisées
- [ ] Arrange-Act-Assert
- [ ] Edge cases testés
- [ ] Assertions claires
- [ ] Pas de dépendances externes non mockées

---

## 📈 Résumé des Accomplissements

### ✅ Tests Créés: 238 tests au total

**Phase 1** (128 tests - Services):
- DocumentService: 20 tests → 100% couverture ✅
- EmbeddingsService: 35 tests → 100% couverture ✅
- PromptService: 30 tests → 100% couverture ✅
- RAGService: 23 tests → 46% couverture
- VectorStoreService: 20 tests → 68% couverture

**Phase 2** (93 tests - Controllers + Helpers + Models):
- Controllers: 58 tests → 87% couverture ✅
  - BaseController, DataController, ProcessController, ProjectController: 100% ✅
  - NLPController: 33%
- Helpers (auth): 16 tests → 100% couverture ✅
- Models DB: 19 tests → 100% couverture ✅

**CI/CD**:
- ✅ GitHub Actions workflow configuré
- ✅ Tests automatiques sur push/PR
- ✅ Rapports de couverture automatiques
- ✅ Documentation complète (README.md)

### 🎯 Prochaines Étapes

**Phase 3 - Tests d'Intégration**:
1. Tests API endpoints (routes/)
   - Authentification, Upload, RAG, Admin
   - Target: ~50 tests, 75% couverture

2. Tests ML (LSTM)
   - Prédictions, Entraînement
   - Target: ~20 tests, 60% couverture

**Phase 4 - Amélioration**:
- RAGService: 46% → 80%
- VectorStoreService: 68% → 80%
- NLPController: 33% → 70%
- User model tests

**Objectif Final**: 75% de couverture globale

---

**Dernière mise à jour**: 2025-12-13
**Total Tests**: 238 (222 passés, 16 nécessitent clés API)
**Couverture**: ~21% globale | 100% sur 8 modules critiques
