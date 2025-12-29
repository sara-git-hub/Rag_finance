# Tests - Fil Rouge

Suite de tests complète pour le projet Fil Rouge.

## 🎉 Dernière Exécution

✅ **286 tests passés** en 5min 52s | **Couverture: 32%** | **11 modules à 100%**

**Récentes améliorations**:
- 🔄 Migration OpenAI → Groq pour tests LLM (économies + vitesse)
- 🔒 Isolation Qdrant via `tmp_path` (plus de verrouillage fichiers)
- 🔒 Isolation PostgreSQL (`minirag_test` séparée de production)
- 📁 Centralisation tests dans `tests/` (`src/tests/` supprimé)
- 🧹 Cleanup automatique avec `vectorstore.close()`

## 📁 Structure

```
tests/
├── unit/                      # Tests unitaires (286 tests)
│   ├── services/             # Tests services LangChain (87% coverage)
│   │   ├── test_document_service.py        (100% coverage ✅)
│   │   ├── test_embeddings_service.py      (100% coverage ✅)
│   │   ├── test_prompt_service.py          (100% coverage ✅)
│   │   ├── test_rag_service.py             (68% coverage 🟡)
│   │   └── test_vectorstore_service.py     (69% coverage 🟡)
│   ├── controllers/          # Tests controllers (87% coverage)
│   │   ├── test_base_controller.py         (100% coverage ✅)
│   │   ├── test_data_controller.py         (100% coverage ✅)
│   │   ├── test_nlp_controller.py          (33% coverage 🔴)
│   │   ├── test_process_controller.py      (100% coverage ✅)
│   │   └── test_project_controller.py      (100% coverage ✅)
│   ├── helpers/              # Tests helpers (100% coverage ✅)
│   │   └── test_auth.py                    (100% coverage ✅)
│   └── models/               # Tests modèles DB (100% coverage ✅)
│       ├── test_asset_model.py             (100% coverage ✅)
│       ├── test_datachunk_model.py         (100% coverage ✅)
│       ├── test_project_model.py           (100% coverage ✅)
│       └── test_user_model.py              (100% coverage ✅)
├── integration/              # Tests d'intégration (1 test - 93% coverage)
│   ├── conftest.py           # DB test séparée (minirag_test)
│   └── test_routes_auth.py   # Tests auth endpoints (93% coverage ✅)
├── ml/                       # Tests Machine Learning (95% coverage ✅)
│   └── test_lstm_model.py    # Tests LSTM (95% coverage ✅)
├── conftest.py               # Fixtures globales (tmp_path, groq_api_key, etc.)
├── pytest.ini                # Configuration pytest
├── ANALYSE_TESTS_ACTUELS.md  # Rapport d'analyse
└── README.md                 # Ce fichier
```

## 🚀 Lancer les tests

⚠️ **Important** : Tous les tests sont maintenant centralisés dans `tests/` (le dossier `src/tests` a été supprimé)

### Tous les tests
```bash
# Depuis la racine du projet
pytest tests/

# Ou depuis le dossier tests
cd tests
pytest
```

### Tests unitaires seulement
```bash
# Depuis la racine
pytest tests/unit/

# Depuis tests/
cd tests
pytest unit/
```

### Tests services LangChain
```bash
# Depuis la racine
pytest tests/unit/services/

# Depuis tests/
cd tests
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
pytest tests/unit/services/test_rag_service.py

# Une classe
pytest tests/unit/services/test_rag_service.py::TestRAGServiceWithLLM

# Un test
pytest tests/unit/services/test_rag_service.py::TestRAGServiceWithLLM::test_answer_with_sources
```

### Tests nécessitant une clé API

Certains tests RAG nécessitent une clé API Groq :

```bash
# Définir la clé API Groq
export GROQ_API_KEY="votre_clé_groq"

# Les tests seront skipped si GROQ_API_KEY n'est pas définie
pytest tests/unit/services/test_rag_service.py::TestRAGServiceWithLLM
```

## 📊 Couverture Actuelle

**Dernière exécution**: 286 tests passés en 5min 52s ✅

| Catégorie | Fichiers | Couverture | Status | Cible |
|-----------|----------|------------|--------|-------|
| **Services (LangChain)** | 5/5 | **87%** | 🟢 | 80% ✅ |
| - DocumentService | 1/1 | 100% ✅ | 🟢 | - |
| - EmbeddingsService | 1/1 | 100% ✅ | 🟢 | - |
| - PromptService | 1/1 | 100% ✅ | 🟢 | - |
| - RAGService | 1/1 | 68% | 🟡 | - |
| - VectorStoreService | 1/1 | 69% | 🟡 | - |
| **Controllers** | 5/5 | **87%** | 🟢 | 70% ✅ |
| - BaseController | 1/1 | 100% ✅ | 🟢 | - |
| - DataController | 1/1 | 100% ✅ | 🟢 | - |
| - ProcessController | 1/1 | 100% ✅ | 🟢 | - |
| - ProjectController | 1/1 | 100% ✅ | 🟢 | - |
| - NLPController | 1/1 | 33% | 🔴 | - |
| **Helpers** | 2/2 | **100%** | 🟢 | 80% ✅ |
| - auth.py | 1/1 | 100% ✅ | 🟢 | - |
| - config.py | 1/1 | 100% ✅ | 🟢 | - |
| **Modèles DB Schemes** | 7/7 | **100%** | 🟢 | 70% ✅ |
| - asset.py | 1/1 | 100% ✅ | 🟢 | - |
| - datachunk.py | 1/1 | 100% ✅ | 🟢 | - |
| - project.py | 1/1 | 100% ✅ | 🟢 | - |
| - user.py | 1/1 | 100% ✅ | 🟢 | - |
| - conversation.py | 1/1 | 100% ✅ | 🟢 | - |
| - exchange_rate.py | 1/1 | 100% ✅ | 🟢 | - |
| - minirag_base.py | 1/1 | 100% ✅ | 🟢 | - |
| **Routes/Endpoints** | 1/6 | **15%** | 🔴 | 75% |
| - auth.py | 1/1 | 93% ✅ | 🟢 | - |
| - admin.py, conversation.py, data.py, nlp.py, base.py | 0/5 | 0% | 🔴 | - |
| **ML (LSTM)** | 1/1 | **95%** | 🟢 | 60% ✅ |
| - lstm_model.py | 1/1 | 95% ✅ | 🟢 | - |
| **Exchange Rates** | 0/7 | **0%** | 🔴 | 60% |
| - jobs, models, routes, services | 0/7 | 0% | 🔴 | - |
| **Models (Legacy)** | 1/6 | **7%** | 🔴 | 70% |
| - UserModel.py | 1/1 | 41% | 🔴 | - |
| - Asset, Chunk, Conversation, Project, Base | 0/5 | 0% | 🔴 | - |
| **TOTAL** | **22/34** | **32%** | 🟡 | **75%** |

**Légende**: 🟢 = Excellent (≥80%) | 🟡 = Moyen (40-79%) | 🔴 = Faible (<40%)

## 🎯 Priorités

### ✅ Phase 1 - Complétée (286 tests)
**Services LangChain** (87% couverture) ✅
- DocumentService: 100% ✅
- EmbeddingsService: 100% ✅
- PromptService: 100% ✅
- RAGService: 68% 🟡
- VectorStoreService: 69% 🟡

**Controllers** (87% couverture) ✅
- BaseController: 100% ✅
- DataController: 100% ✅
- ProcessController: 100% ✅
- ProjectController: 100% ✅
- NLPController: 33% 🔴

**Helpers** (100% couverture) ✅
- auth.py: 100% ✅
- config.py: 100% ✅

**Modèles DB Schemes** (100% couverture) ✅
- Tous les schemes: 100% ✅

**ML** (95% couverture) ✅
- lstm_model.py: 95% ✅

**Routes** (15% couverture partielle)
- auth.py: 93% ✅
- Autres routes: 0% 🔴

### 🔴 Phase 2 - PRIORITAIRE (Prochaines étapes)

**1. Tests Routes/Endpoints API** - 0% couverture
- admin.py (247 lignes non testées)
- conversation.py (111 lignes)
- data.py (104 lignes)
- nlp.py (91 lignes)
- base.py (8 lignes)
- Target: ~100 tests, 75% couverture

**2. Tests Exchange Rates** - 0% couverture
- jobs/ (fetch_rates_job, initial_backfill, scheduler)
- models/ExchangeRateModel.py
- routes/exchange_routes.py
- services/ (bam_api_client, prediction_service)
- Target: ~60 tests, 60% couverture

**3. Tests Models (Legacy)** - 7% couverture
- AssetModel, ChunkModel, ConversationModel, ProjectModel
- Améliorer UserModel (41% → 80%)
- Target: ~30 tests, 70% couverture

### 🟡 Phase 3 - Amélioration Continue
- RAGService: 68% → 80% (+12%)
- VectorStoreService: 69% → 80% (+11%)
- NLPController: 33% → 70% (+37%)
- auth.py: 93% → 100% (+7%)

## 🔄 CI/CD - Intégration Continue

### ✅ GitHub Actions Configuré

Le projet utilise GitHub Actions pour l'exécution automatique des tests:

**Workflow**: `.github/workflows/unit-tests.yml`

**Déclenchement**:
- Push sur `main` ou `develop`
- Pull Requests vers `main` ou `develop`

**Exécution**:
1. Configuration Python 3.12
2. Installation des dépendances lightweight (`src/requirements-test.txt`)
3. Création d'un fichier `.env` de test avec valeurs mock
4. Exécution des tests unitaires compatibles CI/CD (131 tests)
5. Génération du rapport de couverture (XML)
6. Commentaire automatique sur les PR avec le % de couverture

**Tests CI/CD vs Tests Locaux**:

| Environnement | Tests | Durée | Packages |
|---------------|-------|-------|----------|
| **CI/CD (GitHub Actions)** | 131 tests | ~11s | Lightweight (requirements-test.txt) |
| **Local (Docker)** | 286 tests | ~6min | Complets (requirements.txt) |

**Tests exclus du CI/CD** (contraintes espace disque 14GB):
- ❌ Tests PostgreSQL: `integration/`, `unit/models/`
- ❌ Tests ML: `unit/services/test_embeddings_service.py`, `unit/services/test_rag_service.py`, `unit/services/test_vectorstore_service.py`
- ❌ Packages lourds: torch (~3GB), tensorflow (~500MB), sentence-transformers

**Tests inclus dans CI/CD**:
- ✅ `unit/services/test_document_service.py`
- ✅ `unit/services/test_prompt_service.py`
- ✅ `unit/controllers/` (tous)
- ✅ `unit/helpers/` (tous)

**Commandes exécutées**:
```bash
cd tests
pytest unit/services/test_document_service.py unit/services/test_prompt_service.py unit/controllers/ unit/helpers/ -v --cov=../src --cov-report=xml --cov-report=term-missing
```

**Voir les résultats**:
- Onglet **Actions** sur GitHub
- Badge de statut sur les PR (vert ✅ si 131 tests passent)
- Rapport de couverture commenté sur chaque PR

### Configuration Locale

Pour tester le workflow CI/CD localement avant de push:

```bash
# Installer les dépendances lightweight
pip install -r src/requirements-test.txt

# Créer le fichier .env de test (voir .github/workflows/unit-tests.yml pour les variables)
cat > src/.env << 'EOF'
APP_NAME=TestApp
APP_VERSION=1.0.0
SECRET_KEY=test-secret-key
# ... (voir workflow pour la liste complète)
EOF

# Lancer les tests comme le CI/CD
cd tests
pytest unit/services/test_document_service.py unit/services/test_prompt_service.py unit/controllers/ unit/helpers/ -v --cov=../src --cov-report=xml --cov-report=term-missing

# Vérifier le fichier coverage.xml généré
ls -lh coverage.xml
```

**Pour lancer TOUS les tests (286) localement avec Docker**:
```bash
# Depuis la machine hôte
docker exec fastapi bash -c "cd ../tests && pytest -v --cov=../src --cov-report=term-missing"
```

## 🛡️ Isolation des Bases de Données

Les tests sont complètement isolés de la production :

### Qdrant (Vector Store)
- ✅ **Isolation complète** : Chaque test utilise `tmp_path` (répertoire temporaire unique)
- ✅ **Pas de conflit** : Aucun verrouillage de fichiers entre tests
- ✅ **Cleanup automatique** : `vectorstore.close()` appelé dans tous les fixtures
- ✅ **Production protégée** : Aucune connexion à `http://localhost:6333`

### PostgreSQL
- ✅ **Base de test séparée** : `minirag_test` (production : `minirag`)
- ✅ **Isolation totale** : Les tests n'accèdent jamais à la base de production
- ✅ **Cleanup automatique** : Tables créées et supprimées par test

### LLM Provider
- ✅ **Tests avec Groq** : API Groq gratuite pour tests LLM (llama-3.3-70b-versatile)
- ✅ **Tests mockés** : OpenAI et Cohere testés avec mocks (pas de vraie API)
- ✅ **Embeddings locaux** : HuggingFace uniquement (aucune API externe)

## 🔧 Fixtures Disponibles

### Fixtures globales (conftest.py)

```python
@pytest.fixture(scope="session")
def test_data_dir():
    """Répertoire temporaire pour tests"""

@pytest.fixture
def test_database_dir(tmp_path):
    """Répertoire unique par test pour Qdrant (isolation complète)"""

@pytest.fixture
def sample_documents():
    """Documents de test LangChain"""

@pytest.fixture
def groq_api_key():
    """Clé API Groq pour tests LLM (skip si absente)"""

@pytest.fixture
def openai_api_key():
    """Clé API OpenAI (utilisée uniquement dans tests mockés)"""

@pytest.fixture
def cohere_api_key():
    """Clé API Cohere (utilisée uniquement dans tests mockés)"""

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

### ✅ Tests Créés: 286 tests au total

**Couverture Globale**: 32% (22/34 modules testés)

**Modules 100% couverts** (11 modules):
- ✅ Services: DocumentService, EmbeddingsService, PromptService
- ✅ Controllers: Base, Data, Process, Project
- ✅ Helpers: auth.py, config.py
- ✅ DB Schemes: Tous les 7 schemes (asset, datachunk, project, user, conversation, exchange_rate, minirag_base)

**Modules excellents ≥90%** (2 modules):
- ✅ ML: lstm_model (95%)
- ✅ Routes: auth (93%)

**Modules moyens 60-89%** (2 modules):
- 🟡 RAGService: 68%
- 🟡 VectorStoreService: 69%

**Améliorations réalisées**:
- 🎯 Migration OpenAI → Groq pour tests LLM
- 🎯 Isolation Qdrant avec tmp_path (fini verrouillage fichiers)
- 🎯 Isolation PostgreSQL (minirag_test séparée de production)
- 🎯 Centralisation tests dans `tests/` (suppression `src/tests/`)
- 🎯 Cleanup automatique avec `vectorstore.close()`

**Infrastructure**:
- ✅ GitHub Actions workflow configuré
- ✅ Tests automatiques sur push/PR
- ✅ Rapports de couverture automatiques
- ✅ Documentation complète et à jour

### 🎯 Prochaines Étapes (pour atteindre 75%)

**Phase 2 - Routes & Exchange Rates** (~160 tests):
1. Routes API (admin, conversation, data, nlp, base)
   - Target: ~100 tests, 75% couverture
2. Exchange Rates (jobs, models, routes, services)
   - Target: ~60 tests, 60% couverture

**Phase 3 - Models Legacy** (~30 tests):
- AssetModel, ChunkModel, ConversationModel, ProjectModel
- Améliorer UserModel: 41% → 80%
- Target: 70% couverture

**Phase 4 - Amélioration Continue**:
- RAGService: 68% → 80%
- VectorStoreService: 69% → 80%
- NLPController: 33% → 70%
- auth.py: 93% → 100%

**Objectif Final**: 75% de couverture globale (~476 tests)

---

**Dernière mise à jour**: 2025-12-15
**Total Tests**: 286 tests passés (tous isolés de la production) ✅
**Temps d'exécution**: 5min 52s
**LLM Provider**: Groq (llama-3.3-70b-versatile) pour tests réels
**Embeddings**: Local HuggingFace uniquement
**Couverture Globale**: 32% (22/34 modules) | 100% sur 11 modules critiques ✅
**Isolation**: ✅ Qdrant (tmp_path) | ✅ PostgreSQL (minirag_test)
**Structure**: ✅ Tous les tests centralisés dans `tests/` (src/tests supprimé)
