"""
Configuration pytest pour les tests unitaires
Réutilise les fixtures de database du conftest d'intégration
"""

import pytest
import sys
import os

# Add integration conftest to path to reuse database fixtures
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../integration')))

# Import database fixtures from integration conftest
from conftest import test_db_engine, test_db_session  # noqa: F401, E402
