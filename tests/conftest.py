"""
Pytest Configuration and Shared Fixtures
"""

import pytest
import os
import shutil
from pathlib import Path
from langchain_core.documents import Document


@pytest.fixture(scope="session")
def test_data_dir():
    """Create temporary test data directory"""
    test_dir = Path("tests/test_data")
    test_dir.mkdir(parents=True, exist_ok=True)
    yield test_dir
    # Cleanup after all tests
    if test_dir.exists():
        shutil.rmtree(test_dir)


@pytest.fixture
def test_database_dir(tmp_path):
    """Create unique temporary test database directory for each test"""
    # tmp_path is a pytest fixture that provides a unique temporary directory per test
    db_dir = tmp_path / "test_database"
    db_dir.mkdir(parents=True, exist_ok=True)
    yield db_dir
    # Cleanup is automatic with tmp_path


@pytest.fixture
def sample_documents():
    """Sample documents for testing"""
    return [
        Document(
            page_content="La finance est un domaine important de l'économie. Elle concerne la gestion de l'argent.",
            metadata={"source": "doc1.pdf", "page": 1}
        ),
        Document(
            page_content="Les marchés financiers permettent l'échange d'actifs. Ils sont essentiels pour l'économie.",
            metadata={"source": "doc1.pdf", "page": 2}
        ),
        Document(
            page_content="Python est un langage de programmation très populaire. Il est utilisé dans de nombreux domaines.",
            metadata={"source": "doc2.pdf", "page": 1}
        ),
    ]


@pytest.fixture
def sample_long_text():
    """Long text for chunking tests"""
    return """
    LangChain est un framework pour développer des applications basées sur des modèles de langage.
    Il fournit des composants modulaires pour construire des pipelines complexes.

    Les principales fonctionnalités incluent:
    - Gestion des prompts
    - Chaînes de traitement (chains)
    - Agents intelligents
    - Intégration avec des bases de données vectorielles

    LangChain supporte de nombreux fournisseurs de LLM comme OpenAI, Anthropic, Cohere, et d'autres.
    Il permet également d'utiliser des modèles locaux via HuggingFace.

    Le framework est écrit en Python et dispose d'une large communauté de développeurs.
    """ * 5  # Repeat to make it longer


@pytest.fixture
def openai_api_key():
    """Get OpenAI API key from environment"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        pytest.skip("OPENAI_API_KEY not set - skipping test requiring API")
    return api_key


@pytest.fixture
def cohere_api_key():
    """Get Cohere API key from environment"""
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key:
        pytest.skip("COHERE_API_KEY not set - skipping test requiring API")
    return api_key


@pytest.fixture
def groq_api_key():
    """Get Groq API key from environment"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY not set - skipping test requiring API")
    return api_key


@pytest.fixture
def test_project_id():
    """Test project ID"""
    return "test_project_123"


@pytest.fixture
def test_collection_name():
    """Test collection name for vector stores"""
    return "test_collection"
