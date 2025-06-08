from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from src.models.loans import Loan
from src.api.schemas.loans import LoanCreate, LoanUpdate
from .base import BaseRepository


class LoanRepository(BaseRepository[Loan, LoanCreate, LoanUpdate]):
    def get_active_loans(self) -> List[Loan]:
        """
        Récupère les emprunts actifs (non retournés).
        """
        return self.db.query(Loan).filter(Loan.return_date == None).all()

    def get_overdue_loans(self) -> List[Loan]:
        """
        Récupère les emprunts en retard.
        """
        return self.db.query(self.model).filter(
            self.model.due_date < datetime.utcnow(),
            self.model.return_date == None
        ).all()

    def get_loans_by_user(self, *, user_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un utilisateur.
        """
        return self.db.query(Loan).filter(Loan.user_id == user_id).all()

    def get_loans_by_book(self, *, book_id: int) -> List[Loan]:
        """
        Récupère les emprunts d'un livre.
        """
        return self.db.query(Loan).filter(Loan.book_id == book_id).all()