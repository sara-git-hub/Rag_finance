"""
Fetch Exchange Rates Job
Job quotidien pour récupérer les taux de change EUR/MAD et USD/MAD
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Optional
from exchange_rates.services.bam_api_client import BankAlMaghribAPI
from exchange_rates.models.ExchangeRateModel import ExchangeRateModel
from models.db_schemes import CurrencyPair, RateType

logger = logging.getLogger(__name__)


class FetchExchangeRatesJob:
    """Job pour récupérer les taux de change quotidiens"""

    def __init__(self, db_client, api_keys: Dict[str, str]):
        """
        Initialize job

        Args:
            db_client: Database client
            api_keys: BAM API keys dictionary
        """
        self.db_client = db_client
        self.bam_client = BankAlMaghribAPI(api_keys)

    async def fetch_and_store_today(self) -> Dict[str, bool]:
        """
        Récupérer et stocker les taux de change d'aujourd'hui

        Returns:
            Dict indiquant le succès pour chaque paire
        """
        today = datetime.now().date()
        return await self.fetch_and_store_for_date(today)

    async def fetch_and_store_for_date(self, target_date: date) -> Dict[str, bool]:
        """
        Récupérer et stocker les taux pour une date spécifique

        Args:
            target_date: Date pour laquelle récupérer les taux

        Returns:
            {"EUR/MAD": bool, "USD/MAD": bool}
        """
        logger.info(f"Fetching exchange rates for {target_date}")

        model = await ExchangeRateModel.create_instance(self.db_client)
        results = {"EUR/MAD": False, "USD/MAD": False}

        # Récupérer les deux taux
        rates_data = self.bam_client.get_both_rates(target_date)

        for currency_pair_str, rate_data in rates_data.items():
            if rate_data is None:
                logger.warning(f"Failed to fetch {currency_pair_str} for {target_date}")
                continue

            try:
                # Convertir string en enum
                currency_pair = CurrencyPair(currency_pair_str)

                # Vérifier si le taux existe déjà
                exists = await model.rate_exists(
                    currency_pair=currency_pair,
                    date=target_date,
                    rate_type=RateType.ACTUAL
                )

                if exists:
                    logger.info(f"{currency_pair_str} rate for {target_date} already exists, skipping")
                    results[currency_pair_str] = True
                    continue

                # Insérer le nouveau taux
                await model.insert_rate(
                    currency_pair=currency_pair,
                    date=target_date,
                    achat=rate_data["achat"],
                    vente=rate_data["vente"],
                    rate_type=RateType.ACTUAL,
                    source="BAM API"
                )

                logger.info(
                    f"Stored {currency_pair_str}: "
                    f"achat={rate_data['achat']}, vente={rate_data['vente']}"
                )
                results[currency_pair_str] = True

            except Exception as e:
                logger.error(f"Error storing {currency_pair_str}: {e}")
                results[currency_pair_str] = False

        return results

    async def backfill_missing_data(self, days: int = 365) -> Dict[str, int]:
        """
        Remplir les données manquantes pour les N derniers jours

        Args:
            days: Nombre de jours à vérifier (par défaut 365 pour 1 an)

        Returns:
            {"EUR/MAD": count, "USD/MAD": count} nombre de jours ajoutés
        """
        logger.info(f"Backfilling exchange rates for last {days} days")

        model = await ExchangeRateModel.create_instance(self.db_client)
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        counts = {"EUR/MAD": 0, "USD/MAD": 0}

        # Parcourir chaque jour
        current_date = start_date
        while current_date <= end_date:
            # Ignorer les week-ends (marchés fermés)
            if current_date.weekday() >= 5:  # 5=samedi, 6=dimanche
                current_date += timedelta(days=1)
                continue

            results = await self.fetch_and_store_for_date(current_date)

            for pair, success in results.items():
                if success:
                    # Vérifier si c'était une nouvelle insertion (pas un "already exists")
                    exists_before = await model.rate_exists(
                        currency_pair=CurrencyPair(pair),
                        date=current_date,
                        rate_type=RateType.ACTUAL
                    )
                    if not exists_before:
                        counts[pair] += 1

            current_date += timedelta(days=1)

            # Petit délai pour ne pas surcharger l'API
            import asyncio
            await asyncio.sleep(0.5)

        logger.info(f"Backfill complete: {counts}")
        return counts

    async def run(self):
        """
        Point d'entrée principal du job
        Appelé quotidiennement par le scheduler
        """
        try:
            logger.info("=== Exchange Rates Job Started ===")

            # Récupérer les taux d'aujourd'hui
            results = await self.fetch_and_store_today()

            success_count = sum(1 for v in results.values() if v)
            total_count = len(results)

            logger.info(
                f"=== Exchange Rates Job Completed: "
                f"{success_count}/{total_count} successful ==="
            )

            return results

        except Exception as e:
            logger.error(f"Exchange Rates Job failed: {e}", exc_info=True)
            raise


async def fetch_rates_task(db_client, api_keys: Dict[str, str]):
    """
    Fonction wrapper pour le scheduler

    Args:
        db_client: Database client
        api_keys: BAM API keys
    """
    job = FetchExchangeRatesJob(db_client, api_keys)
    return await job.run()
