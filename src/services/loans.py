import logging
from typing import List, Optional, Any, Dict, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..repositories.loans import LoanRepository
from ..repositories.books import BookRepository
from ..repositories.users import UserRepository
from ..models.loans import Loan
from ..models.books import Book
from ..models.users import User
from ..api.schemas.loans import LoanCreate, LoanUpdate
from .base import BaseService
from src.exceptions import CustomException

logger = logging.getLogger(__name__)

class LoanService(BaseService[Loan, LoanCreate, LoanUpdate]):
    """
    Service pour la gestion des emprunts.
    """
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_repository: BookRepository,
        user_repository: UserRepository
    ):
        super().__init__(loan_repository)
        self.loan_repository = loan_repository
        self.book_repository = book_repository
        self.user_repository = user_repository
    
    def get_active_loans(self) -> List[Loan]:
        logger.info("Récupération des emprunts actifs")
        return self.loan_repository.get_active_loans()
    
    def get_overdue_loans(self) -> List[Loan]:
        logger.info("Récupération des emprunts en retard")
        return self.loan_repository.get_overdue_loans()
    
    def get_loans_by_user(self, *, user_id: int) -> List[Loan]:
        logger.info(f"Récupération des emprunts pour l'utilisateur {user_id}")
        return self.loan_repository.get_loans_by_user(user_id=user_id)
    
    def get_loans_by_book(self, *, book_id: int) -> List[Loan]:
        logger.info(f"Récupération des emprunts pour le livre {book_id}")
        return self.loan_repository.get_loans_by_book(book_id=book_id)
    
    def create_loan(
        self,
        *,
        user_id: int,
        book_id: int,
        loan_period_days: int = 14
    ) -> Loan:
        logger.info(f"Tentative de création d'un emprunt pour user_id={user_id}, book_id={book_id}")
        user = self.user_repository.get(id=user_id)
        if not user:
            logger.error(f"Utilisateur avec l'ID {user_id} non trouvé")
            raise CustomException(f"Utilisateur avec l'ID {user_id} non trouvé", status_code=404)
        
        if not user.is_active:
            logger.warning(f"L'utilisateur {user_id} est inactif et ne peut pas emprunter de livres")
            raise CustomException("L'utilisateur est inactif et ne peut pas emprunter de livres", status_code=403)
        
        book = self.book_repository.get(id=book_id)
        if not book:
            logger.error(f"Livre avec l'ID {book_id} non trouvé")
            raise CustomException(f"Livre avec l'ID {book_id} non trouvé", status_code=404)
        
        if book.quantity <= 0:
            logger.warning(f"Le livre {book_id} n'est pas disponible pour l'emprunt")
            raise CustomException("Le livre n'est pas disponible pour l'emprunt", status_code=409)
        
        active_loans = self.loan_repository.get_active_loans()
        for loan in active_loans:
            if loan.user_id == user_id and loan.book_id == book_id:
                logger.warning(f"L'utilisateur {user_id} a déjà emprunté le livre {book_id} et ne l'a pas encore rendu")
                raise CustomException("L'utilisateur a déjà emprunté ce livre et ne l'a pas encore rendu", status_code=409)
        
        user_active_loans = [loan for loan in active_loans if loan.user_id == user_id]
        if len(user_active_loans) >= 5:
            logger.warning(f"L'utilisateur {user_id} a atteint la limite d'emprunts simultanés (5)")
            raise CustomException("L'utilisateur a atteint la limite d'emprunts simultanés (5)", status_code=403)
        
        loan_data = {
            "user_id": user_id,
            "book_id": book_id,
            "loan_date": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=loan_period_days),
            "return_date": None
        }
        
        loan = self.loan_repository.create(obj_in=loan_data)
        logger.info(f"Emprunt créé avec succès pour user_id={user_id}, book_id={book_id}, loan_id={loan.id}")
        
        book.quantity -= 1
        self.book_repository.update(db_obj=book, obj_in={"quantity": book.quantity})
        logger.info(f"Quantité du livre {book_id} mise à jour à {book.quantity}")
        
        return loan
    
    def return_loan(self, *, loan_id: int) -> Loan:
        logger.info(f"Tentative de retour de l'emprunt {loan_id}")
        loan = self.loan_repository.get(id=loan_id)
        if not loan:
            logger.error(f"Emprunt avec l'ID {loan_id} non trouvé")
            raise CustomException(f"Emprunt avec l'ID {loan_id} non trouvé", status_code=404)
        
        if loan.return_date:
            logger.warning(f"L'emprunt {loan_id} a déjà été retourné")
            raise CustomException("L'emprunt a déjà été retourné", status_code=409)
        
        loan_data = {"return_date": datetime.utcnow()}
        loan = self.loan_repository.update(db_obj=loan, obj_in=loan_data)
        logger.info(f"Emprunt {loan_id} marqué comme retourné")
        
        book = self.book_repository.get(id=loan.book_id)
        if book:
            book.quantity += 1
            self.book_repository.update(db_obj=book, obj_in={"quantity": book.quantity})
            logger.info(f"Quantité du livre {book.id} mise à jour à {book.quantity}")
        
        return loan
    
    def extend_loan(self, *, loan_id: int, extension_days: int = 7) -> Loan:
        logger.info(f"Tentative de prolongation de l'emprunt {loan_id}")
        loan = self.loan_repository.get(id=loan_id)
        if not loan:
            logger.error(f"Emprunt avec l'ID {loan_id} non trouvé")
            raise CustomException(f"Emprunt avec l'ID {loan_id} non trouvé", status_code=404)
        
        if loan.return_date:
            logger.warning(f"L'emprunt {loan_id} a déjà été retourné")
            raise CustomException("L'emprunt a déjà été retourné", status_code=409)
        
        if loan.due_date < datetime.utcnow():
            logger.warning(f"L'emprunt {loan_id} est en retard et ne peut pas être prolongé")
            raise CustomException("L'emprunt est en retard et ne peut pas être prolongé", status_code=409)
        
        if loan.due_date > loan.loan_date + timedelta(days=14):
            logger.warning(f"L'emprunt {loan_id} a déjà été prolongé")
            raise CustomException("L'emprunt a déjà été prolongé", status_code=409)
        
        new_due_date = loan.due_date + timedelta(days=extension_days)
        loan_data = {"due_date": new_due_date}
        logger.info(f"Nouvelle date d'échéance pour l'emprunt {loan_id}: {new_due_date}")
        
        return self.loan_repository.update(db_obj=loan, obj_in=loan_data)
