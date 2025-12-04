"""
APScheduler Configuration
Configuration du planificateur pour les jobs quotidiens
"""

import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from typing import Dict, Callable
from datetime import datetime

logger = logging.getLogger(__name__)


class ExchangeRatesScheduler:
    """Gestionnaire de tâches planifiées pour les taux de change"""

    def __init__(self):
        """Initialize scheduler"""
        self.scheduler = AsyncIOScheduler(
            timezone="Africa/Casablanca",  # Timezone du Maroc
            job_defaults={
                'coalesce': True,  # Combiner les exécutions manquées
                'max_instances': 1,  # Une seule instance à la fois
                'misfire_grace_time': 3600  # 1h de tolérance pour exécutions manquées
            }
        )

        # Ajouter des listeners pour logging
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    def _job_listener(self, event):
        """
        Listener pour logger l'exécution des jobs

        Args:
            event: Event object from APScheduler
        """
        if event.exception:
            logger.error(
                f"Job {event.job_id} failed with exception: {event.exception}",
                exc_info=True
            )
        else:
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
            func: Fonction à exécuter
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

        self.scheduler.add_job(
            func,
            trigger=trigger,
            id=job_id,
            name=f"Daily job at {hour:02d}:{minute:02d}",
            replace_existing=True,
            kwargs=kwargs
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
        jobs = self.scheduler.get_jobs()
        if not jobs:
            logger.info("No scheduled jobs")
            return []

        job_info = []
        for job in jobs:
            info = {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
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

        return {
            "status": "scheduled",
            "id": job.id,
            "name": job.name,
            "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
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


def get_scheduler() -> ExchangeRatesScheduler:
    """
    Récupérer l'instance globale du scheduler (singleton)

    Returns:
        ExchangeRatesScheduler instance
    """
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = ExchangeRatesScheduler()
    return _scheduler_instance
