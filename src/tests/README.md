# 🧪 Tests LangChain Migration

Tests automatisés pour la migration vers LangChain.

## 📋 Structure

```
tests/
├── __init__.py
├── conftest.py                    # Fixtures partagées
├── test_document_service.py       # Tests DocumentService
├── test_embeddings_service.py     # Tests EmbeddingsService
├── test_prompt_service.py         # Tests PromptService
├── test_vectorstore_service.py    # Tests VectorStoreService
└── test_rag_service.py            # Tests RAGService
```

## 🚀 Installation

```bash
cd src
pip install -r requirements.txt
```

## ▶️ Exécution des Tests

### Tous les tests
```bash
pytest
```

### Tests spécifiques
```bash
# Un fichier de test
pytest tests/test_document_service.py

# Une classe de test
pytest tests/test_embeddings_service.py::TestEmbeddingsServiceLocal

# Un test spécifique
pytest tests/test_embeddings_service.py::TestEmbeddingsServiceLocal::test_embed_query_local
```

### Tests par catégorie
```bash
# Tests unitaires rapides (sans API)
pytest -m unit

# Tests d'intégration
pytest -m integration

# Tests nécessitant des clés API
pytest -m requires_api
```

### Avec couverture de code
```bash
pytest --cov=services --cov-report=html
```

Le rapport HTML sera dans `htmlcov/index.html`

### Mode verbose
```bash
pytest -v
pytest -vv  # Très verbose
```

### Arrêter au premier échec
```bash
pytest -x
```

### Exécuter seulement les tests qui ont échoué
```bash
pytest --lf  # last-failed
```

## 🔑 Tests avec API Keys

Certains tests nécessitent des clés API. Définissez-les avant de lancer les tests :

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-..."
export COHERE_API_KEY="..."

# Windows PowerShell
$env:OPENAI_API_KEY="sk-..."
$env:COHERE_API_KEY="..."

# Windows CMD
set OPENAI_API_KEY=sk-...
set COHERE_API_KEY=...
```

Les tests nécessitant des clés API seront automatiquement **skippés** si la clé n'est pas présente.

## 📊 Organisation des Tests

### test_document_service.py
- ✅ Chunking avec RecursiveCharacterTextSplitter
- ✅ Préservation des métadonnées
- ✅ Statistiques des chunks
- ✅ Overlap entre chunks

### test_embeddings_service.py
- ✅ Embeddings locaux (HuggingFace) - **GRATUIT**
- ✅ Embeddings OpenAI (nécessite API key)
- ✅ Embeddings Cohere (nécessite API key)
- ✅ Multilingual support (FR/EN/AR)
- ✅ Cohérence des embeddings

### test_prompt_service.py
- ✅ Prompts multilingues (EN/FR/AR)
- ✅ ChatPromptTemplate
- ✅ Formatage de documents
- ✅ Changement de langue dynamique

### test_vectorstore_service.py
- ✅ Qdrant vector store
- ✅ Ajout de documents
- ✅ Recherche par similarité
- ✅ Retriever interfaces (similarity, MMR)
- ✅ Statistiques

### test_rag_service.py
- ✅ Pipeline RAG complète
- ✅ Génération de réponses (nécessite API key)
- ✅ Réponses avec sources
- ✅ Streaming
- ✅ Batch processing

## 🎯 Fixtures Disponibles

Définies dans `conftest.py` :

- `test_data_dir` : Dossier temporaire pour données de test
- `test_database_dir` : Dossier temporaire pour base vectorielle
- `sample_documents` : Documents d'exemple
- `sample_long_text` : Texte long pour tests de chunking
- `openai_api_key` : Clé API OpenAI (skip si absent)
- `cohere_api_key` : Clé API Cohere (skip si absent)
- `test_project_id` : ID de projet de test
- `test_collection_name` : Nom de collection de test

## 📈 Exemple de Sortie

```bash
$ pytest -v

tests/test_document_service.py::TestDocumentService::test_init_default_params PASSED
tests/test_document_service.py::TestDocumentService::test_chunk_documents_basic PASSED
tests/test_embeddings_service.py::TestEmbeddingsServiceLocal::test_init_local_default PASSED
tests/test_embeddings_service.py::TestEmbeddingsServiceLocal::test_embed_query_local PASSED
tests/test_embeddings_service.py::TestEmbeddingsServiceOpenAI::test_init_openai SKIPPED (OPENAI_API_KEY not set)
tests/test_prompt_service.py::TestPromptService::test_init_default_language PASSED
tests/test_vectorstore_service.py::TestVectorStoreServiceQdrant::test_add_documents PASSED
tests/test_rag_service.py::TestRAGServiceStructure::test_init PASSED
tests/test_rag_service.py::TestRAGServiceWithLLM::test_answer SKIPPED (OPENAI_API_KEY not set)

========================== 30 passed, 6 skipped in 15.23s ==========================
```

## 🐛 Debugging

### Voir les print() dans les tests
```bash
pytest -s
```

### Voir les logs complets
```bash
pytest --log-cli-level=DEBUG
```

### Débugger avec pdb
```bash
pytest --pdb  # Entre en mode debug au premier échec
```

## 📝 Écrire de Nouveaux Tests

Exemple de structure :

```python
import pytest
from services import MonService

class TestMonService:
    """Description de la suite de tests"""

    @pytest.fixture
    def mon_service(self):
        """Fixture pour créer le service"""
        return MonService()

    def test_ma_fonctionnalite(self, mon_service):
        """Test une fonctionnalité spécifique"""
        result = mon_service.ma_methode()

        assert result is not None
        assert result == "valeur_attendue"
```

## ⚙️ Configuration CI/CD

Pour intégrer dans GitHub Actions :

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        cd src
        pip install -r requirements.txt

    - name: Run tests
      run: |
        cd src
        pytest --cov=services --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## 🔗 Ressources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/example/markers.html)
