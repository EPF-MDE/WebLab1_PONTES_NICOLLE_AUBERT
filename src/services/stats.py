import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.books import Book
from ..models.users import User
from ..models.loans import Loan
from src.exceptions import CustomException

logger = logging.getLogger(__name__)

class StatsService:
    """
    Service pour les statistiques de la bibliothèque.
    """
    def __init__(self, db: Session):
        self.db = db
        logger.debug("StatsService initialized with db session %s", db)
    
    def get_general_stats(self) -> Dict[str, Any]:
        """
        Récupère des statistiques générales sur la bibliothèque.
        """
        logger.info("Fetching general library statistics")
        try:
            total_books = self.db.query(func.sum(Book.quantity)).scalar() or 0
            unique_books = self.db.query(func.count(Book.id)).scalar() or 0
            total_users = self.db.query(func.count(User.id)).scalar() or 0
            active_users = self.db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
            total_loans = self.db.query(func.count(Loan.id)).scalar() or 0
            active_loans = self.db.query(func.count(Loan.id)).filter(Loan.return_date == None).scalar() or 0
            overdue_loans = self.db.query(func.count(Loan.id)).filter(
                Loan.return_date == None,
                Loan.due_date < datetime.utcnow()
            ).scalar() or 0
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération des statistiques générales : {e}")
            raise CustomException("Erreur lors de la récupération des statistiques générales", status_code=500)
        
        stats = {
            "total_books": total_books,
            "unique_books": unique_books,
            "total_users": total_users,
            "active_users": active_users,
            "total_loans": total_loans,
            "active_loans": active_loans,
            "overdue_loans": overdue_loans
        }
        logger.debug("General stats: %s", stats)
        return stats
    
    def get_most_borrowed_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les livres les plus empruntés.
        """
        logger.info("Fetching top %d most borrowed books", limit)
        try:
            result = self.db.query(
                Book.id,
                Book.title,
                Book.author,
                func.count(Loan.id).label("loan_count")
            ).join(Loan).group_by(Book.id).order_by(func.count(Loan.id).desc()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération des livres les plus empruntés : {e}")
            raise CustomException("Erreur lors de la récupération des livres les plus empruntés", status_code=500)
        
        books = [
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "loan_count": book.loan_count
            }
            for book in result
        ]
        logger.debug("Most borrowed books: %s", books)
        return books
    
    def get_most_active_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Récupère les utilisateurs les plus actifs.
        """
        logger.info("Fetching top %d most active users", limit)
        try:
            result = self.db.query(
                User.id,
                User.full_name,
                User.email,
                func.count(Loan.id).label("loan_count")
            ).join(Loan).group_by(User.id).order_by(func.count(Loan.id).desc()).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération des utilisateurs les plus actifs : {e}")
            raise CustomException("Erreur lors de la récupération des utilisateurs les plus actifs", status_code=500)
        
        users = [
            {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "loan_count": user.loan_count
            }
            for user in result
        ]
        logger.debug("Most active users: %s", users)
        return users
    
    def get_monthly_loans(self, months: int = 12) -> List[Dict[str, Any]]:
        """
        Récupère le nombre d'emprunts par mois pour les derniers mois.
        """
        logger.info("Fetching monthly loans for the last %d months", months)
        start_date = datetime.utcnow() - timedelta(days=30 * months)
        try:
            result = self.db.query(
                func.strftime("%Y-%m", Loan.loan_date).label("month"),
                func.count(Loan.id).label("loan_count")
            ).filter(
                Loan.loan_date >= start_date
            ).group_by(
                func.strftime("%Y-%m", Loan.loan_date)
            ).order_by(
                func.strftime("%Y-%m", Loan.loan_date)
            ).all()
        except SQLAlchemyError as e:
            logger.error(f"Erreur lors de la récupération des emprunts mensuels : {e}")
            raise CustomException("Erreur lors de la récupération des emprunts mensuels", status_code=500)
        
        monthly_loans = [
            {
                "month": month,
                "loan_count": loan_count
            }
            for month, loan_count in result
        ]
        logger.debug("Monthly loans: %s", monthly_loans)
        return monthly_loans