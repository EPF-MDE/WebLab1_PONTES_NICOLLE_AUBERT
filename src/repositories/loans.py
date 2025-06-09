import logging
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

from .base import BaseRepository
from ..models.loans import Loan
from ..models.books import Book
from ..models.users import User
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

class LoanRepository(BaseRepository[Loan, None, None]):
    def get_active_loans(self) -> List[Loan]:
        """
        Récupère les emprunts actifs (non retournés).
        """
        logger.info("Fetching active loans (not returned)")
        try:
            return self.db.query(Loan).filter(Loan.return_date == None).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emprunts actifs : {e}")
            raise CustomException("Erreur lors de la récupération des emprunts actifs", status_code=500)
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Récupère les emprunts en retard.
        """
        now = datetime.utcnow()
        logger.info("Fetching overdue loans at %s", now)
        try:
            return self.db.query(Loan).filter(
                Loan.return_date == None,
                Loan.due_date < now
            ).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emprunts en retard : {e}")
            raise CustomException("Erreur lors de la récupération des emprunts en retard", status_code=500)
    
    def get_loans_by_user(self, *, user_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un utilisateur.
        """
        logger.info("Fetching loans for user_id=%d", user_id)
        try:
            return self.db.query(Loan).filter(Loan.user_id == user_id).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emprunts pour l'utilisateur {user_id} : {e}")
            raise CustomException("Erreur lors de la récupération des emprunts de l'utilisateur", status_code=500)
    
    def get_loans_by_book(self, *, book_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un livre.
        """
        logger.info("Fetching loans for book_id=%d", book_id)
        try:
            return self.db.query(Loan).filter(Loan.book_id == book_id).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des emprunts pour le livre {book_id} : {e}")
            raise CustomException("Erreur lors de la récupération des emprunts du livre", status_code=500)
    
    def get_with_details(self, *, id: int) -> Optional[Loan]:
        """
        Récupère un emprunt avec les détails du livre et de l'utilisateur.
        """
        logger.info("Fetching loan with details for id=%d", id)
        try:
            return self.db.query(Loan).options(
                joinedload(Loan.user),
                joinedload(Loan.book)
            ).filter(Loan.id == id).first()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'emprunt avec détails (id={id}) : {e}")
            raise CustomException("Erreur lors de la récupération de l'emprunt avec détails", status_code=500)
    
    def get_multi_with_details(self, *, skip: int = 0, limit: int = 100) -> List[Loan]:
        """
        Récupère plusieurs emprunts avec les détails des livres et des utilisateurs.
        """
        logger.info("Fetching multiple loans with details (skip=%d, limit=%d)", skip, limit)
        try:
            return self.db.query(Loan).options(
                joinedload(Loan.user),
                joinedload(Loan.book)
            ).offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de plusieurs emprunts avec détails : {e}")
            raise CustomException("Erreur lors de la récupération de plusieurs emprunts avec détails", status_code=500)
    
    def get_loans_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques sur les emprunts.
        """
        now = datetime.utcnow()
        logger.info("Fetching loan statistics at %s", now)
        try:
            total_loans = self.db.query(func.count(Loan.id)).scalar() or 0
            active_loans = self.db.query(func.count(Loan.id)).filter(Loan.return_date == None).scalar() or 0
            overdue_loans = self.db.query(func.count(Loan.id)).filter(
                Loan.return_date == None,
                Loan.due_date < now
            ).scalar() or 0
            
            # Emprunts par mois (12 derniers mois)
            start_date = now - timedelta(days=365)
            loans_by_month = self.db.query(
                func.strftime("%Y-%m", Loan.loan_date).label("month"),
                func.count(Loan.id).label("count")
            ).filter(
                Loan.loan_date >= start_date
            ).group_by(
                func.strftime("%Y-%m", Loan.loan_date)
            ).all()
            
            loans_by_month_dict = {month: count for month, count in loans_by_month}
            
            logger.debug("Loan stats: total=%d, active=%d, overdue=%d", total_loans, active_loans, overdue_loans)
            return {
                "total_loans": total_loans,
                "active_loans": active_loans,
                "overdue_loans": overdue_loans,
                "loans_by_month": loans_by_month_dict
            }
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques sur les emprunts : {e}")
            raise CustomException("Erreur lors de la récupération des statistiques sur les emprunts", status_code=500)