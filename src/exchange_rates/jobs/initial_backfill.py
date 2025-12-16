"""
Initial Backfill Script
Récupère 90 jours (3 mois) de données historiques au premier démarrage
"""

import asyncio
from datetime import date, timedelta
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from exchange_rates.services.bam_api_client import BankAlMaghribAPI
from exchange_rates.models.ExchangeRateModel import ExchangeRateModel
from models.db_schemes import CurrencyPair, RateType

logger = logging.getLogger(__name__)


async def check_if_backfill_needed(db_client) -> bool:
    """
    Vérifie si le backfill est nécessaire
    Retourne True si la base est vide ou a moins de 30 jours de données
    """
    model = await ExchangeRateModel.create_instance(db_client)

    # Vérifier pour MAD/EUR
    eur_data = await model.get_historical_data(
        currency_pair=CurrencyPair.MAD_EUR,
        days=365,
        rate_type=RateType.ACTUAL
    )

    if len(eur_data) < 30:
        logger.info(f"Backfill needed: only {len(eur_data)} days of data found")
        return True

    logger.info(f"Backfill not needed: {len(eur_data)} days of data found")
    return False


async def run_initial_backfill(db_client, api_keys: dict, days: int = 30):
    """
    Récupère les données historiques sur N jours

    Args:
        db_client: Database client
        api_keys: Dictionnaire avec les clés API BAM
        days: Nombre de jours à récupérer (défaut: 30 = 1 mois)
    """
    logger.info(f"Starting initial backfill for {days} days...")

    # Initialiser le client API
    bam_client = BankAlMaghribAPI(api_keys)
    model = await ExchangeRateModel.create_instance(db_client)

    # Date de fin = hier (aujourd'hui pourrait ne pas être disponible encore)
    end_date = date.today() - timedelta(days=1)
    start_date = end_date - timedelta(days=days)

    logger.info(f"Fetching data from {start_date} to {end_date}")

    success_count = 0
    error_count = 0
    total_days = days

    # Récupérer jour par jour
    current_date = start_date

    while current_date <= end_date:
        try:
            # Variables pour suivre si on a sauvegardé des données
            eur_saved = False
            usd_saved = False

            # Récupérer MAD/EUR
            # Vérifier d'abord si le taux existe déjà
            eur_exists = await model.rate_exists(
                currency_pair=CurrencyPair.MAD_EUR,
                date=current_date,
                rate_type=RateType.ACTUAL
            )

            if eur_exists:
                logger.debug(f"⊙ {current_date} MAD/EUR already exists, skipping")
                eur_saved = True  # Compter comme succès
            else:
                rate_eur = bam_client.get_mad_eur_rate(current_date)
                if rate_eur:
                    await model.insert_rate(
                        currency_pair=CurrencyPair.MAD_EUR,
                        date=current_date,
                        achat=rate_eur['achat'],
                        vente=rate_eur['vente'],
                        rate_type=RateType.ACTUAL,
                        source='Bank Al-Maghrib (Backfill)'
                    )
                    logger.debug(f"✓ {current_date} MAD/EUR saved")
                    eur_saved = True

            # Attendre 65 secondes entre les requêtes EUR et USD pour éviter le rate limiting
            await asyncio.sleep(65)

            # Récupérer MAD/USD
            # Vérifier d'abord si le taux existe déjà
            usd_exists = await model.rate_exists(
                currency_pair=CurrencyPair.MAD_USD,
                date=current_date,
                rate_type=RateType.ACTUAL
            )

            if usd_exists:
                logger.debug(f"⊙ {current_date} MAD/USD already exists, skipping")
                usd_saved = True  # Compter comme succès
            else:
                rate_usd = bam_client.get_mad_usd_rate(current_date)
                if rate_usd:
                    await model.insert_rate(
                        currency_pair=CurrencyPair.MAD_USD,
                        date=current_date,
                        achat=rate_usd['achat'],
                        vente=rate_usd['vente'],
                        rate_type=RateType.ACTUAL,
                        source='Bank Al-Maghrib (Backfill)'
                    )
                    logger.debug(f"✓ {current_date} MAD/USD saved")
                    usd_saved = True

            if eur_saved or usd_saved:
                success_count += 1
            else:
                error_count += 1
                logger.warning(f"✗ {current_date} No data available")

            # Afficher progression tous les 30 jours
            if (current_date - start_date).days % 30 == 0:
                progress = ((current_date - start_date).days / total_days) * 100
                logger.info(f"Progress: {progress:.1f}% ({success_count} success, {error_count} errors)")

            # Délai de 65 secondes avant la prochaine date pour respecter les rate limits de l'API BAM
            await asyncio.sleep(65)

        except Exception as e:
            error_count += 1
            error_msg = str(e)

            # Gestion explicite des erreurs 429 (rate limit) avec 2 retries maximum
            if "429" in error_msg or "Too Many Requests" in error_msg:
                logger.error(f"⚠ RATE LIMIT ERROR (429) for {current_date}")
                logger.error(f"⚠ API BAM has blocked the request - Too many requests")

                retry_success = False
                max_retries = 2

                for retry_attempt in range(1, max_retries + 1):
                    logger.error(f"⚠ Waiting 65 seconds before retry {retry_attempt}/{max_retries}...")
                    await asyncio.sleep(65)

                    try:
                        logger.info(f"↻ Retry {retry_attempt}/{max_retries} for {current_date} after 65s wait...")

                        # Variables pour suivre le succès
                        retry_eur_saved = False
                        retry_usd_saved = False

                        # Vérifier et récupérer MAD/EUR
                        eur_exists = await model.rate_exists(
                            currency_pair=CurrencyPair.MAD_EUR,
                            date=current_date,
                            rate_type=RateType.ACTUAL
                        )

                        if eur_exists:
                            logger.info(f"⊙ {current_date} MAD/EUR already exists, skipping (retry {retry_attempt})")
                            retry_eur_saved = True
                        else:
                            rate_eur = bam_client.get_mad_eur_rate(current_date)
                            if rate_eur:
                                await model.insert_rate(
                                    currency_pair=CurrencyPair.MAD_EUR,
                                    date=current_date,
                                    achat=rate_eur['achat'],
                                    vente=rate_eur['vente'],
                                    rate_type=RateType.ACTUAL,
                                    source='Bank Al-Maghrib (Backfill)'
                                )
                                logger.info(f"✓ {current_date} MAD/EUR saved (after retry {retry_attempt})")
                                retry_eur_saved = True

                        # Attendre entre EUR et USD
                        await asyncio.sleep(65)

                        # Vérifier et récupérer MAD/USD
                        usd_exists = await model.rate_exists(
                            currency_pair=CurrencyPair.MAD_USD,
                            date=current_date,
                            rate_type=RateType.ACTUAL
                        )

                        if usd_exists:
                            logger.info(f"⊙ {current_date} MAD/USD already exists, skipping (retry {retry_attempt})")
                            retry_usd_saved = True
                        else:
                            rate_usd = bam_client.get_mad_usd_rate(current_date)
                            if rate_usd:
                                await model.insert_rate(
                                    currency_pair=CurrencyPair.MAD_USD,
                                    date=current_date,
                                    achat=rate_usd['achat'],
                                    vente=rate_usd['vente'],
                                    rate_type=RateType.ACTUAL,
                                    source='Bank Al-Maghrib (Backfill)'
                                )
                                logger.info(f"✓ {current_date} MAD/USD saved (after retry {retry_attempt})")
                                retry_usd_saved = True

                        if retry_eur_saved or retry_usd_saved:
                            success_count += 1
                            error_count -= 1  # Annuler l'erreur comptée plus haut
                            retry_success = True
                            break  # Sortir de la boucle si succès

                    except Exception as retry_error:
                        retry_error_msg = str(retry_error)
                        if "429" in retry_error_msg or "Too Many Requests" in retry_error_msg:
                            logger.error(f"✗ Retry {retry_attempt}/{max_retries} also got 429 for {current_date}")
                            if retry_attempt == max_retries:
                                logger.error(f"✗ All {max_retries} retries exhausted for {current_date}")
                        else:
                            logger.error(f"✗ Retry {retry_attempt} failed for {current_date}: {retry_error}")
                            break  # Sortir si erreur différente de 429
            else:
                logger.error(f"Error fetching data for {current_date}: {e}")

        current_date += timedelta(days=1)

    logger.info(f"Backfill completed: {success_count} days retrieved, {error_count} errors")
    logger.info(f"Success rate: {(success_count/total_days)*100:.1f}%")

    return {
        'success_count': success_count,
        'error_count': error_count,
        'total_days': total_days,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }


async def run_backfill_if_needed(db_client, api_keys: dict, days: int = 30):
    """
    Vérifie si le backfill est nécessaire et l'exécute si besoin
    """
    try:
        needs_backfill = await check_if_backfill_needed(db_client)

        if needs_backfill:
            logger.info("=" * 60)
            logger.info("INITIAL BACKFILL STARTING")
            logger.info("=" * 60)
            result = await run_initial_backfill(db_client, api_keys, days)
            logger.info("=" * 60)
            logger.info("INITIAL BACKFILL COMPLETED")
            logger.info(f"Retrieved {result['success_count']} days of data")
            logger.info("=" * 60)
            return result
        else:
            logger.info("Backfill skipped - sufficient data already exists")
            return None

    except Exception as e:
        logger.error(f"Error during backfill check/execution: {e}", exc_info=True)
        raise
