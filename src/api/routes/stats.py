import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ...db.session import get_db
from ...services.stats import StatsService
from ..dependencies import get_current_admin_user
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/general", response_model=Dict[str, Any])
def get_general_stats(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère des statistiques générales sur la bibliothèque.
    """
    logger.info("Fetching general stats by user: %s", getattr(current_user, "id", None))
    service = StatsService(db)
    try:
        result = service.get_general_stats()
        logger.debug("General stats result: %s", result)
        return result
    except CustomException as e:
        logger.error(f"Error fetching general stats: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching general stats: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des statistiques générales")


@router.get("/most-borrowed-books", response_model=List[Dict[str, Any]])
def get_most_borrowed_books(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les livres les plus empruntés.
    """
    logger.info("Fetching most borrowed books (limit=%d) by user: %s", limit, getattr(current_user, "id", None))
    service = StatsService(db)
    try:
        result = service.get_most_borrowed_books(limit=limit)
        logger.debug("Most borrowed books result: %s", result)
        return result
    except CustomException as e:
        logger.error(f"Error fetching most borrowed books: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching most borrowed books: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des livres les plus empruntés")


@router.get("/most-active-users", response_model=List[Dict[str, Any]])
def get_most_active_users(
    db: Session = Depends(get_db),
    limit: int = 10,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère les utilisateurs les plus actifs.
    """
    logger.info("Fetching most active users (limit=%d) by user: %s", limit, getattr(current_user, "id", None))
    service = StatsService(db)
    try:
        result = service.get_most_active_users(limit=limit)
        logger.debug("Most active users result: %s", result)
        return result
    except CustomException as e:
        logger.error(f"Error fetching most active users: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching most active users: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des utilisateurs les plus actifs")


@router.get("/monthly-loans", response_model=List[Dict[str, Any]])
def get_monthly_loans(
    db: Session = Depends(get_db),
    months: int = 12,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère le nombre d'emprunts par mois pour les derniers mois.
    """
    logger.info("Fetching monthly loans (months=%d) by user: %s", months, getattr(current_user, "id", None))
    service = StatsService(db)
    try:
        result = service.get_monthly_loans(months=months)
        logger.debug("Monthly loans result: %s", result)
        return result
    except CustomException as e:
        logger.error(f"Error fetching monthly loans: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching monthly loans: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des emprunts mensuels")