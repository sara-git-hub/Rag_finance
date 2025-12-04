#!/usr/bin/env python3
"""
Manual Backfill Script for Exchange Rates
Allows manual data retrieval for specific date ranges

Usage:
    python manual_backfill.py --start-date 2024-01-01 --end-date 2024-03-31
    python manual_backfill.py --start-date 2023-06-01 --end-date 2023-12-31 --delay 30
"""

import asyncio
import argparse
import logging
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
import os
import sys

# Add src to path (parent directory)
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from exchange_rates.services.bam_api_client import BankAlMaghribAPI
from exchange_rates.models.ExchangeRateModel import ExchangeRateModel
from models.db_schemes import CurrencyPair, RateType
from helpers.config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def manual_backfill(
    start_date: date,
    end_date: date,
    api_keys: dict,
    db_client,
    delay: int = 30
):
    """
    Récupère manuellement les données pour une période spécifique

    Args:
        start_date: Date de début (incluse)
        end_date: Date de fin (incluse)
        api_keys: Dictionnaire avec les clés API BAM
        db_client: Database client
        delay: Délai en secondes entre chaque requête (défaut: 30)
    """
    # Validation des dates
    if start_date > end_date:
        logger.error("Start date must be before end date")
        return None

    if end_date > date.today():
        logger.warning(f"End date {end_date} is in the future, adjusting to today")
        end_date = date.today() - timedelta(days=1)

    total_days = (end_date - start_date).days + 1

    logger.info("=" * 70)
    logger.info("MANUAL BACKFILL STARTING")
    logger.info("=" * 70)
    logger.info(f"Date range: {start_date} to {end_date}")
    logger.info(f"Total days to fetch: {total_days}")
    logger.info(f"Delay between requests: {delay} seconds")
    logger.info(f"Estimated duration: {(total_days * delay) / 60:.1f} minutes")
    logger.info("=" * 70)

    # Initialiser le client API et le modèle
    bam_client = BankAlMaghribAPI(api_keys)
    model = await ExchangeRateModel.create_instance(db_client)

    success_count = 0
    error_count = 0
    skip_count = 0
    current_date = start_date

    while current_date <= end_date:
        try:
            # Vérifier si les données existent déjà
            existing_eur_list = await model.get_rates_by_date_range(
                currency_pair=CurrencyPair.MAD_EUR,
                start_date=current_date,
                end_date=current_date,
                rate_type=RateType.ACTUAL
            )
            existing_eur = existing_eur_list[0] if existing_eur_list else None

            existing_usd_list = await model.get_rates_by_date_range(
                currency_pair=CurrencyPair.MAD_USD,
                start_date=current_date,
                end_date=current_date,
                rate_type=RateType.ACTUAL
            )
            existing_usd = existing_usd_list[0] if existing_usd_list else None

            if existing_eur and existing_usd:
                logger.info(f"⊘ {current_date} - Data already exists, skipping")
                skip_count += 1
                current_date += timedelta(days=1)
                continue

            # Récupérer les taux pour cette date
            logger.info(f"→ Fetching {current_date}...")
            rates = bam_client.get_both_rates(current_date)

            # Sauvegarder MAD/EUR
            if rates['MAD/EUR'] and not existing_eur:
                await model.insert_rate(
                    currency_pair=CurrencyPair.MAD_EUR,
                    date=current_date,
                    achat=rates['MAD/EUR']['achat'],
                    vente=rates['MAD/EUR']['vente'],
                    rate_type=RateType.ACTUAL,
                    source='Bank Al-Maghrib (Manual Backfill)'
                )
                logger.info(f"  ✓ MAD/EUR saved")

            # Sauvegarder MAD/USD
            if rates['MAD/USD'] and not existing_usd:
                await model.insert_rate(
                    currency_pair=CurrencyPair.MAD_USD,
                    date=current_date,
                    achat=rates['MAD/USD']['achat'],
                    vente=rates['MAD/USD']['vente'],
                    rate_type=RateType.ACTUAL,
                    source='Bank Al-Maghrib (Manual Backfill)'
                )
                logger.info(f"  ✓ MAD/USD saved")

            if rates['MAD/EUR'] or rates['MAD/USD']:
                success_count += 1
            else:
                error_count += 1
                logger.warning(f"  ✗ No data available from API")

            # Afficher progression tous les 10 jours
            if (current_date - start_date).days % 10 == 0 and current_date != start_date:
                progress = ((current_date - start_date).days / total_days) * 100
                logger.info("")
                logger.info(f"📊 Progress: {progress:.1f}% | Success: {success_count} | Errors: {error_count} | Skipped: {skip_count}")
                logger.info("")

            # Délai entre les requêtes
            await asyncio.sleep(delay)

        except Exception as e:
            error_count += 1
            error_msg = str(e)

            # Gestion des erreurs 429 (rate limit) avec 2 retries maximum
            if "429" in error_msg or "Too Many Requests" in error_msg:
                logger.error(f"⚠ RATE LIMIT ERROR (429) for {current_date}")
                logger.error(f"⚠ API BAM has blocked the request - Too many requests")

                retry_success = False
                max_retries = 2

                for retry_attempt in range(1, max_retries + 1):
                    logger.error(f"⚠ Waiting 60 seconds before retry {retry_attempt}/{max_retries}...")
                    await asyncio.sleep(60)

                    try:
                        logger.info(f"↻ Retry {retry_attempt}/{max_retries} for {current_date} after 60s wait...")
                        rates = bam_client.get_both_rates(current_date)

                        if rates['MAD/EUR'] and not existing_eur:
                            await model.insert_rate(
                                currency_pair=CurrencyPair.MAD_EUR,
                                date=current_date,
                                achat=rates['MAD/EUR']['achat'],
                                vente=rates['MAD/EUR']['vente'],
                                rate_type=RateType.ACTUAL,
                                source='Bank Al-Maghrib (Manual Backfill)'
                            )
                            logger.info(f"  ✓ MAD/EUR saved (after retry {retry_attempt})")

                        if rates['MAD/USD'] and not existing_usd:
                            await model.insert_rate(
                                currency_pair=CurrencyPair.MAD_USD,
                                date=current_date,
                                achat=rates['MAD/USD']['achat'],
                                vente=rates['MAD/USD']['vente'],
                                rate_type=RateType.ACTUAL,
                                source='Bank Al-Maghrib (Manual Backfill)'
                            )
                            logger.info(f"  ✓ MAD/USD saved (after retry {retry_attempt})")

                        if rates['MAD/EUR'] or rates['MAD/USD']:
                            success_count += 1
                            error_count -= 1
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

    # Résumé final
    logger.info("")
    logger.info("=" * 70)
    logger.info("MANUAL BACKFILL COMPLETED")
    logger.info("=" * 70)
    logger.info(f"Total days processed: {total_days}")
    logger.info(f"Successfully retrieved: {success_count} days")
    logger.info(f"Errors: {error_count} days")
    logger.info(f"Skipped (already exists): {skip_count} days")
    logger.info(f"Success rate: {(success_count/total_days)*100:.1f}%")
    logger.info("=" * 70)

    return {
        'success_count': success_count,
        'error_count': error_count,
        'skip_count': skip_count,
        'total_days': total_days,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }


async def main():
    """Main function to run manual backfill"""
    parser = argparse.ArgumentParser(
        description='Manual backfill for exchange rates',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Récupérer les 3 premiers mois de 2024
  python manual_backfill.py --start-date 2024-01-01 --end-date 2024-03-31

  # Récupérer toute l'année 2023 avec un délai de 45 secondes
  python manual_backfill.py --start-date 2023-01-01 --end-date 2023-12-31 --delay 45

  # Récupérer le dernier mois
  python manual_backfill.py --start-date 2024-10-01 --end-date 2024-10-31
        """
    )

    parser.add_argument(
        '--start-date',
        required=True,
        type=str,
        help='Date de début (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--end-date',
        required=True,
        type=str,
        help='Date de fin (format: YYYY-MM-DD)'
    )

    parser.add_argument(
        '--delay',
        type=int,
        default=30,
        help='Délai en secondes entre chaque requête (défaut: 30)'
    )

    args = parser.parse_args()

    # Parse dates
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    except ValueError as e:
        logger.error(f"Invalid date format: {e}")
        logger.error("Please use YYYY-MM-DD format (e.g., 2024-01-15)")
        sys.exit(1)

    # Load environment variables
    load_dotenv()

    # Get settings
    settings = get_settings()

    # Prepare API keys
    api_keys = {
        "changes": settings.CLE_API_CHANGES,
        "changes_2": settings.CLE_API_CHANGES_2
    }

    if not api_keys["changes"]:
        logger.error("CLE_API_CHANGES not found in environment variables")
        sys.exit(1)

    # Database connection
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    engine = create_async_engine(postgres_conn)
    db_client = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        # Run manual backfill
        result = await manual_backfill(
            start_date=start_date,
            end_date=end_date,
            api_keys=api_keys,
            db_client=db_client,
            delay=args.delay
        )

        if result:
            logger.info("")
            logger.info("✓ Manual backfill completed successfully!")
            sys.exit(0)
        else:
            logger.error("✗ Manual backfill failed")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
