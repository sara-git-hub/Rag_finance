"""
APScheduler Configuration
Configuration du planificateur pour les jobs quotidiens
"""

import logging
import time
import asyncio
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from typing import Dict, Callable, Optional
from datetime import datetime
from functools import wraps
import inspect

from exchange_rates.metrics import (
    SCHEDULER_JOB_SUCCESS,
    SCHEDULER_JOB_ERROR,
    SCHEDULER_JOB_DURATION
)

logger = logging.getLogger(__name__)


class ExchangeRatesScheduler:
    """Gestionnaire de tâches planifiées pour les taux de change"""

    def __init__(self, event_loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        Initialize scheduler

        Args:
            event_loop: Event loop à utiliser pour les tâches async (optionnel)
        """
        # Stocker l'event loop pour les tâches async
        self.event_loop = event_loop or asyncio.get_event_loop()

        # Utiliser BackgroundScheduler au lieu de AsyncIOScheduler
        # BackgroundScheduler fonctionne dans un thread séparé mais permet
        # d'exécuter des coroutines dans l'event loop de FastAPI
        self.scheduler = BackgroundScheduler(
            timezone="Africa/Casablanca",  # Timezone du Maroc
            job_defaults={
                'coalesce': True,  # Combiner les exécutions manquées
                'max_instances': 1,  # Une seule instance à la fois
                'misfire_grace_time': 3600  # 1h de tolérance pour exécutions manquées
            }
        )

        # Ajouter des listeners pour logging
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def _wrap_async_job(self, async_func: Callable, **kwargs):
        """
        Wrapper pour exécuter une fonction async dans l'event loop de FastAPI

        Args:
            async_func: Fonction async à exécuter
            **kwargs: Arguments à passer à la fonction

        Returns:
            Fonction synchrone qui exécute la coroutine
        """
        def sync_wrapper():
            # Créer la coroutine
            coro = async_func(**kwargs)

            # Exécuter la coroutine dans l'event loop de FastAPI
            # Utiliser run_coroutine_threadsafe car on est dans un thread différent
            future = asyncio.run_coroutine_threadsafe(coro, self.event_loop)

            # Attendre le résultat (avec timeout de 5 minutes)
            try:
                result = future.result(timeout=300)
                return result
            except TimeoutError:
                logger.error(f"Job {async_func.__name__} timed out after 5 minutes")
                raise
            except Exception as e:
                logger.error(f"Job {async_func.__name__} failed: {e}", exc_info=True)
                raise

        return sync_wrapper

    def _job_listener(self, event):
        """
        Listener pour logger l'exécution des jobs et enregistrer les métriques

        Args:
            event: Event object from APScheduler
        """
        # Calculer la durée d'exécution si disponible
        if hasattr(event, 'retval') and hasattr(event, 'scheduled_run_time'):
            duration = (datetime.now() - event.scheduled_run_time).total_seconds()
            if duration > 0:
                SCHEDULER_JOB_DURATION.labels(job_name=event.job_id).observe(duration)

        if event.exception:
            # Enregistrer l'erreur dans les métriques
            error_type = type(event.exception).__name__
            SCHEDULER_JOB_ERROR.labels(
                job_name=event.job_id,
                error_type=error_type
            ).inc()

            logger.error(
                f"Job {event.job_id} failed: {event.exception}",
                exc_info=True
            )
        else:
            # Enregistrer le succès dans les métriques
            SCHEDULER_JOB_SUCCESS.labels(job_name=event.job_id).inc()
            logger.info(f"Job {event.job_id} executed successfully")

    def add_daily_job(
        self,
        func: Callable,
        hour: int = 9,
        minute: int = 0,
        job_id: str = "fetch_exchange_rates",
        **kwargs
    ):
        """
        Ajouter un job quotidien

        Args:
            func: Fonction à exécuter (peut être sync ou async)
            hour: Heure d'exécution (0-23)
            minute: Minute d'exécution (0-59)
            job_id: ID unique du job
            **kwargs: Arguments à passer à la fonction
        """
        trigger = CronTrigger(
            hour=hour,
            minute=minute,
            timezone="Africa/Casablanca"
        )

        is_async = inspect.iscoroutinefunction(func)

        # Si la fonction est async, la wrapper pour l'exécuter dans l'event loop
        if is_async:
            job_func = self._wrap_async_job(func, **kwargs)
            # Ne pas passer kwargs à add_job car déjà passés au wrapper
            job_kwargs = {}
        else:
            job_func = func
            job_kwargs = kwargs

        self.scheduler.add_job(
            job_func,
            trigger=trigger,
            id=job_id,
            name=f"Daily job at {hour:02d}:{minute:02d}",
            replace_existing=True,
            kwargs=job_kwargs
        )

        logger.info(f"Scheduled job '{job_id}' to run daily at {hour:02d}:{minute:02d} (Casablanca time)")

    def start(self):
        """Démarrer le scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✓ Scheduler started successfully")
        else:
            logger.warning("Scheduler is already running")

    def shutdown(self, wait: bool = True):
        """
        Arrêter le scheduler

        Args:
            wait: Attendre la fin des jobs en cours
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("✓ Scheduler shut down")
        else:
            logger.warning("Scheduler is not running")

    def list_jobs(self):
        """Liste tous les jobs planifiés"""
        from datetime import timezone

        jobs = self.scheduler.get_jobs()
        if not jobs:
            logger.info("No scheduled jobs")
            return []

        job_info = []
        # Utiliser l'heure actuelle avec timezone UTC pour comparaison
        now = datetime.now(timezone.utc)

        for job in jobs:
            # Récupérer next_run_time de façon sûre
            next_run = getattr(job, 'next_run_time', None)

            # Si next_run est dans le passé, forcer le recalcul
            if next_run and next_run < now:
                logger.warning(f"Job {job.id} next_run_time is in the past ({next_run}), recalculating...")
                # Recalculer la prochaine exécution en fonction du trigger
                try:
                    next_run_calculated = job.trigger.get_next_fire_time(None, now)
                    # Mettre à jour le job avec la nouvelle heure
                    if next_run_calculated:
                        job.modify(next_run_time=next_run_calculated)
                        next_run = next_run_calculated
                        logger.info(f"Job {job.id} next_run_time updated to {next_run}")
                except Exception as e:
                    logger.error(f"Could not recalculate next_run for {job.id}: {e}")

            info = {
                "id": job.id,
                "name": job.name,
                "next_run": next_run.isoformat() if next_run else None,
                "trigger": str(job.trigger)
            }
            job_info.append(info)
            logger.info(f"Job: {info}")

        return job_info

    def get_job_status(self, job_id: str) -> Dict:
        """
        Récupérer le statut d'un job

        Args:
            job_id: ID du job

        Returns:
            Dictionnaire avec les infos du job
        """
        job = self.scheduler.get_job(job_id)

        if not job:
            return {"status": "not_found"}

        next_run = getattr(job, 'next_run_time', None)

        return {
            "status": "scheduled",
            "id": job.id,
            "name": job.name,
            "next_run": next_run.isoformat() if next_run else None,
            "trigger": str(job.trigger)
        }

    def pause_job(self, job_id: str):
        """Mettre un job en pause"""
        self.scheduler.pause_job(job_id)
        logger.info(f"Job '{job_id}' paused")

    def resume_job(self, job_id: str):
        """Reprendre un job en pause"""
        self.scheduler.resume_job(job_id)
        logger.info(f"Job '{job_id}' resumed")

    def run_job_now(self, job_id: str):
        """
        Exécuter un job immédiatement (manuel)

        Args:
            job_id: ID du job à exécuter
        """
        job = self.scheduler.get_job(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Job '{job_id}' scheduled to run immediately")
        else:
            logger.error(f"Job '{job_id}' not found")


# Instance globale du scheduler
_scheduler_instance = None


def get_scheduler(event_loop: Optional[asyncio.AbstractEventLoop] = None) -> ExchangeRatesScheduler:
    """
    Récupérer l'instance globale du scheduler (singleton)

    Args:
        event_loop: Event loop à utiliser pour les tâches async (utilisé uniquement à la première création)

    Returns:
        ExchangeRatesScheduler instance
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ExchangeRatesScheduler(event_loop=event_loop)
    return _scheduler_instance
