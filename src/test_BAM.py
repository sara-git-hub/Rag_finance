from BAM import BankAlMaghribAPI
from dotenv import load_dotenv
import os
import logging

# Configurer le logging pour voir les détails
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

# Charger les variables d'environnement
load_dotenv()

print("=" * 60)
print("Testing Bank Al-Maghrib API")
print("=" * 60)

# Vérifier les clés API
api_key_1 = os.getenv("CLE_API_CHANGES")
api_key_2 = os.getenv("CLE_API_CHANGES_2")

print(f"API Key 1: {api_key_1[:10]}...{api_key_1[-5:] if api_key_1 else 'NOT SET'}")
print(f"API Key 2: {api_key_2[:10]}...{api_key_2[-5:] if api_key_2 else 'NOT SET'}")
print()

bam = BankAlMaghribAPI({
    "changes": api_key_1,
    "changes_2": api_key_2,
})

# Test 1: Récupérer les taux pour une date passée (format ISO 8601)
print("Test 1: Get exchange rates for 2024-12-01")
print("-" * 60)
data_fx = bam.get_cours_virement(libDevise="EUR", date="2025-12-01T00:00:00.000Z")
print(f"Result: {data_fx}")
print()

# Test 2: Récupérer tous les taux (EUR et USD)
print("Test 2: Get both MAD/EUR and MAD/USD rates")
print("-" * 60)
from datetime import date, timedelta
test_date = date.today() - timedelta(days=7)  # Date d'il y a 7 jours
both_rates = bam.get_both_rates(test_date)
print(f"Date: {test_date}")
print(f"MAD/EUR: {both_rates['MAD/EUR']}")
print(f"MAD/USD: {both_rates['MAD/USD']}")
print()

print("=" * 60)

