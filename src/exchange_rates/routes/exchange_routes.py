"""
Exchange Rates API Routes
Routes pour accéder aux taux de change et prédictions
"""

from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime, date, timedelta

from helpers.auth import get_current_user, require_admin
from exchange_rates.services.prediction_service import PredictionService
from exchange_rates.models.ExchangeRateModel import ExchangeRateModel
from models.db_schemes import CurrencyPair, RateType
import logging

logger = logging.getLogger(__name__)

exchange_router = APIRouter(
    prefix="/api/v1/exchange-rates",
    tags=["exchange_rates"],
)


# ==================== Routes Publiques (Users) ====================

@exchange_router.get("/latest")
async def get_latest_rates(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer les derniers taux de change EUR/MAD et USD/MAD
    Accessible à tous les utilisateurs authentifiés
    """
    try:
        model = await ExchangeRateModel.create_instance(request.app.db_client)

        eur_mad = await model.get_latest_rate(CurrencyPair.EUR_MAD, RateType.ACTUAL)
        usd_mad = await model.get_latest_rate(CurrencyPair.USD_MAD, RateType.ACTUAL)

        return JSONResponse(content={
            "signal": "LATEST_RATES_RETRIEVED",
            "data": {
                "EUR/MAD": {
                    "date": eur_mad.date.isoformat() if eur_mad else None,
                    "achat": eur_mad.achat if eur_mad else None,
                    "vente": eur_mad.vente if eur_mad else None,
                    "moyenne": eur_mad.moyenne if eur_mad else None
                } if eur_mad else None,
                "USD/MAD": {
                    "date": usd_mad.date.isoformat() if usd_mad else None,
                    "achat": usd_mad.achat if usd_mad else None,
                    "vente": usd_mad.vente if usd_mad else None,
                    "moyenne": usd_mad.moyenne if usd_mad else None
                } if usd_mad else None
            }
        })

    except Exception as e:
        logger.error(f"Error fetching latest rates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching latest rates"
        )


@exchange_router.get("/predictions")
async def get_predictions(
    request: Request,
    currency_pair: str = Query(..., description="EUR/MAD or USD/MAD"),
    days_history: int = Query(30, ge=7, le=365),
    days_ahead: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique et les prédictions pour une paire de devises
    Accessible à tous les utilisateurs authentifiés

    Args:
        currency_pair: "EUR/MAD" ou "USD/MAD" (query parameter)
        days_history: Nombre de jours d'historique (défaut: 30)
        days_ahead: Nombre de jours de prédictions (défaut: 7)
    """
    try:
        # Valider la paire de devises
        try:
            pair = CurrencyPair(currency_pair)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency pair. Must be 'EUR/MAD' or 'USD/MAD'"
            )

        # Récupérer les prédictions
        prediction_service = PredictionService(
            db_client=request.app.db_client,
            models_dir="/app/assets/models/exchange_rates"
        )

        data = await prediction_service.get_predictions_with_history(
            currency_pair=pair,
            history_days=days_history,
            prediction_days=days_ahead
        )

        return JSONResponse(content={
            "signal": "PREDICTIONS_RETRIEVED",
            "data": data
        })

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@exchange_router.get("/history")
async def get_history(
    request: Request,
    currency_pair: str = Query(..., description="EUR/MAD or USD/MAD"),
    days: int = Query(365, ge=1, le=730),
    current_user: dict = Depends(get_current_user)
):
    """
    Récupérer l'historique des taux de change
    Accessible à tous les utilisateurs authentifiés

    Args:
        currency_pair: "EUR/MAD" ou "USD/MAD" (query parameter)
        days: Nombre de jours d'historique (défaut: 365 = 1 an)
    """
    try:
        # Valider la paire de devises
        try:
            pair = CurrencyPair(currency_pair)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency pair. Must be 'EUR/MAD' or 'USD/MAD'"
            )

        model = await ExchangeRateModel.create_instance(request.app.db_client)

        historical = await model.get_historical_data(
            currency_pair=pair,
            days=days,
            rate_type=RateType.ACTUAL
        )

        return JSONResponse(content={
            "signal": "HISTORY_RETRIEVED",
            "currency_pair": currency_pair,
            "data": [
                {
                    "date": rate.date.isoformat(),
                    "achat": rate.achat,
                    "vente": rate.vente,
                    "moyenne": rate.moyenne
                }
                for rate in historical
            ]
        })

    except Exception as e:
        logger.error(f"Error fetching history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== Routes Admin ====================

@exchange_router.post("/admin/train-model")
async def train_model(
    request: Request,
    currency_pair: str = Query(..., description="EUR/MAD or USD/MAD"),
    days_history: int = Query(175, ge=60, le=730),
    current_user: dict = Depends(require_admin)
):
    """
    Entraîner le modèle LSTM pour une paire de devises
    Réservé aux administrateurs
    """
    try:
        # Log pour debug
        logger.info(f"Training model - currency_pair received: '{currency_pair}'")

        # Valider la paire
        try:
            pair = CurrencyPair(currency_pair)
        except ValueError as ve:
            logger.error(f"Invalid currency pair '{currency_pair}': {ve}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency pair: '{currency_pair}'. Expected: EUR/MAD or USD/MAD"
            )

        prediction_service = PredictionService(
            db_client=request.app.db_client,
            models_dir="/app/assets/models/exchange_rates"
        )

        result = await prediction_service.train_model(
            currency_pair=pair,
            days_history=days_history,
            force_retrain=True
        )

        return JSONResponse(content={
            "signal": "MODEL_TRAINED",
            "data": result
        })

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error training model: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@exchange_router.post("/admin/generate-predictions")
async def generate_predictions(
    request: Request,
    currency_pair: str = Query(..., description="EUR/MAD or USD/MAD"),
    days_ahead: int = Query(7, ge=1, le=30),
    current_user: dict = Depends(require_admin)
):
    """
    Générer et sauvegarder les prédictions en base de données
    Réservé aux administrateurs
    """
    try:
        # Valider la paire
        try:
            pair = CurrencyPair(currency_pair)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid currency pair"
            )

        prediction_service = PredictionService(
            db_client=request.app.db_client,
            models_dir="/app/assets/models/exchange_rates"
        )

        count = await prediction_service.save_predictions_to_db(
            currency_pair=pair,
            days_ahead=days_ahead
        )

        return JSONResponse(content={
            "signal": "PREDICTIONS_GENERATED",
            "currency_pair": currency_pair,
            "predictions_saved": count
        })

    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating predictions: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@exchange_router.post("/admin/fetch-rates-now")
async def fetch_rates_now(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Déclencher manuellement la récupération des taux de change
    Réservé aux administrateurs
    """
    try:
        from exchange_rates.jobs.fetch_rates_job import FetchExchangeRatesJob

        # Préparer les clés API
        from helpers.config import get_settings
        settings = get_settings()

        bam_api_keys = {
            "changes": settings.CLE_API_CHANGES,
            "changes_2": settings.CLE_API_CHANGES_2
        }

        job = FetchExchangeRatesJob(request.app.db_client, bam_api_keys)
        results = await job.run()

        return JSONResponse(content={
            "signal": "RATES_FETCHED",
            "results": results
        })

    except Exception as e:
        logger.error(f"Error fetching rates: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@exchange_router.get("/admin/scheduler/status")
async def get_scheduler_status(
    request: Request,
    current_user: dict = Depends(require_admin)
):
    """
    Récupérer le statut du scheduler
    Réservé aux administrateurs
    """
    try:
        if not hasattr(request.app, 'exchange_scheduler'):
            return JSONResponse(content={
                "signal": "SCHEDULER_NOT_INITIALIZED",
                "status": "not_running"
            })

        jobs = request.app.exchange_scheduler.list_jobs()

        return JSONResponse(content={
            "signal": "SCHEDULER_STATUS_RETRIEVED",
            "status": "running" if request.app.exchange_scheduler.scheduler.running else "stopped",
            "jobs": jobs
        })

    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
