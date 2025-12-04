# Exchange Rates Backfill - Guide d'utilisation

## Vue d'ensemble

Le système de backfill permet de récupérer les données historiques de taux de change depuis l'API Bank Al-Maghrib (BAM).

## Backfill automatique

Le backfill automatique s'exécute au démarrage de l'application si moins de 30 jours de données sont disponibles.

**Configuration actuelle:**
- **Période**: 90 jours (3 mois)
- **Délai entre requêtes**: 30 secondes
- **Gestion des erreurs 429**: Attente de 60 secondes + 1 retry
- **Durée estimée**: ~45-90 minutes pour 90 jours

**Fichier**: `src/exchange_rates/jobs/initial_backfill.py`

## Backfill manuel

Pour récupérer des données pour des périodes spécifiques, utilisez le script manuel.

### Prérequis

- Environnement Python configuré
- Variables d'environnement définies (`.env` file)
- Accès à la base de données PostgreSQL

### Installation

```bash
cd src
pip install -r requirements.txt
```

### Utilisation de base

```bash
# Récupérer 3 mois de données
python manual_backfill.py --start-date 2024-01-01 --end-date 2024-03-31

# Récupérer l'année 2023
python manual_backfill.py --start-date 2023-01-01 --end-date 2023-12-31

# Récupérer avec délai personnalisé (45 secondes)
python manual_backfill.py --start-date 2024-06-01 --end-date 2024-08-31 --delay 45
```

### Paramètres

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `--start-date` | String | Oui | Date de début (format: YYYY-MM-DD) |
| `--end-date` | String | Oui | Date de fin (format: YYYY-MM-DD) |
| `--delay` | Integer | Non | Délai en secondes entre requêtes (défaut: 30) |

### Exemples d'utilisation

#### 1. Récupérer le premier trimestre 2024

```bash
python manual_backfill.py --start-date 2024-01-01 --end-date 2024-03-31
```

**Durée estimée**: ~45 minutes (90 jours × 30 secondes / 60)

#### 2. Récupérer une année complète avec délai augmenté

```bash
python manual_backfill.py --start-date 2023-01-01 --end-date 2023-12-31 --delay 45
```

**Durée estimée**: ~4.5 heures (365 jours × 45 secondes / 3600)

#### 3. Récupérer juste un mois

```bash
python manual_backfill.py --start-date 2024-10-01 --end-date 2024-10-31
```

**Durée estimée**: ~15 minutes (30 jours × 30 secondes / 60)

### Comportement

1. **Vérification des doublons**: Le script vérifie si les données existent déjà et les saute
2. **Gestion des erreurs 429**:
   - Log explicite de l'erreur
   - Attente de 60 secondes
   - Une tentative de retry
3. **Progression**: Affichage tous les 10 jours
4. **Résumé final**: Statistiques complètes à la fin

### Logs

Le script affiche des logs détaillés:

```
→ Fetching 2024-01-15...
  ✓ MAD/EUR saved
  ✓ MAD/USD saved

⊘ 2024-01-20 - Data already exists, skipping

⚠ RATE LIMIT ERROR (429) for 2024-01-25
⚠ API BAM has blocked the request - Too many requests
⚠ Waiting 60 seconds before retrying...
↻ Retrying 2024-01-25 after 60s wait...
  ✓ MAD/EUR saved (after retry)

📊 Progress: 33.3% | Success: 25 | Errors: 3 | Skipped: 2
```

## Limitations de l'API BAM

### Rate Limits

L'API Bank Al-Maghrib applique des limites strictes:

- **Limite estimée**: ~100-150 requêtes par heure
- **Réponse**: HTTP 429 (Too Many Requests)
- **Impact**: Avec 2 requêtes/jour (EUR + USD), on peut récupérer ~50-75 jours/heure max

### Recommandations

1. **Pour <100 jours**: Utiliser le backfill automatique (30s de délai)
2. **Pour 100-365 jours**: Utiliser le script manuel avec délai 45s
3. **Pour >365 jours**: Diviser en plusieurs sessions sur plusieurs jours

### Jours sans données

L'API ne retourne pas de données pour:
- Weekends (samedi, dimanche)
- Jours fériés marocains
- Jours où la BAM n'a pas publié de taux

**Solution**: Le modèle LSTM remplit automatiquement les trous par interpolation linéaire.

## Modèle LSTM et données manquantes

Le modèle LSTM a été modifié pour gérer les données manquantes:

### Interpolation automatique

Quand des jours manquent (weekends, jours fériés), le modèle:

1. Crée un index de dates complet (tous les jours calendaires)
2. Interpole linéairement les valeurs manquantes
3. Utilise forward/backward fill pour les extrémités

### Exigences minimales

- **Pour l'entraînement**: 40+ jours de données disponibles (même non consécutifs)
- **Pour la prédiction**: 30+ jours de données disponibles

Le système convertit automatiquement les jours disponibles en séquence continue.

## Exemples de scénarios

### Scénario 1: Première installation

```bash
# Au démarrage, le backfill automatique récupère 90 jours
# Puis utilisez le manuel pour compléter l'année

python manual_backfill.py --start-date 2024-01-01 --end-date 2024-08-26
```

### Scénario 2: Mise à jour après une panne

```bash
# Récupérer les jours manqués pendant la panne
python manual_backfill.py --start-date 2024-11-01 --end-date 2024-11-15
```

### Scénario 3: Construction d'un historique complet

```bash
# Année 2023
python manual_backfill.py --start-date 2023-01-01 --end-date 2023-12-31 --delay 45

# Année 2022
python manual_backfill.py --start-date 2022-01-01 --end-date 2022-12-31 --delay 45
```

## Résolution de problèmes

### Erreur: "CLE_API_CHANGES not found"

**Solution**: Vérifier le fichier `.env` contient:
```
CLE_API_CHANGES=votre_clé_api
CLE_API_CHANGES_2=votre_clé_secours
```

### Erreur: "Role fil_rouge_user does not exist"

**Solution**: Vérifier la configuration PostgreSQL dans `.env.postgres`

### Trop d'erreurs 429

**Solution**: Augmenter le délai
```bash
python manual_backfill.py --start-date ... --end-date ... --delay 60
```

### Script s'arrête après quelques jours

**Cause**: Probablement rate limit API
**Solution**: Relancer le script, il sautera les jours déjà récupérés

## Maintenance quotidienne

Le scheduler automatique récupère les nouveaux taux chaque jour à 9h du matin:

- **Fichier**: `src/exchange_rates/jobs/fetch_rates_job.py`
- **Fréquence**: Quotidienne à 9h00
- **Action**: Récupère les taux MAD/EUR et MAD/USD du jour

## Attribution

Conformément aux conditions d'utilisation de la BAM, les données affichées doivent mentionner:

```
Source: Bank Al-Maghrib (www.bkam.ma)
```

Cette attribution est automatiquement incluse dans le champ `source` de chaque enregistrement.
