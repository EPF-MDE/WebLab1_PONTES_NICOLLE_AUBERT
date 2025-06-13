import pytest
from datetime import datetime, timedelta

from src.models.loans import Loan
from src.models.books import Book
from src.models.users import User
from src.repositories.loans import LoanRepository
from src.repositories.books import BookRepository
from src.repositories.users import UserRepository
from src.exceptions import CustomException 

class DummySession:
    def query(self, model):
        class Query:
            def filter(self, *args, **kwargs):
                raise Exception("Erreur DB")
            def all(self):
                raise Exception("Erreur DB")
            def first(self):
                raise Exception("Erreur DB")
            def get(self, id):  # Ajout pour le test remove
                raise Exception("Erreur DB")
        return Query()
    def add(self, obj):
        raise Exception("Erreur DB")
    def commit(self):
        raise Exception("Erreur DB")
    def refresh(self, obj):
        raise Exception("Erreur DB")
    def delete(self, obj):
        raise Exception("Erreur DB")

def test_create_loan(db_session, user, book):
    repo = LoanRepository(Loan, db_session)
    loan_data = {
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=14),
        "return_date": None
    }
    loan = repo.create(obj_in=loan_data)
    assert loan.id is not None
    assert loan.user_id == user.id
    assert loan.book_id == book.id
    assert loan.return_date is None

def test_get_active_loans(db_session, user, book):
    repo = LoanRepository(Loan, db_session)
    # Crée un emprunt actif
    loan = repo.create(obj_in={
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=14),
        "return_date": None
    })
    active_loans = repo.get_active_loans()
    assert any(l.id == loan.id for l in active_loans)

def test_get_overdue_loans(db_session, user, book):
    repo = LoanRepository(Loan, db_session)
    # Crée un emprunt en retard
    loan = repo.create(obj_in={
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow() - timedelta(days=30),
        "due_date": datetime.utcnow() - timedelta(days=15),
        "return_date": None
    })
    overdue_loans = repo.get_overdue_loans()
    assert any(l.id == loan.id for l in overdue_loans)

def test_get_loans_by_user(db_session, user, book):
    repo = LoanRepository(Loan, db_session)
    loan = repo.create(obj_in={
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=14),
        "return_date": None
    })
    user_loans = repo.get_loans_by_user(user_id=user.id)
    assert any(l.id == loan.id for l in user_loans)

def test_get_loans_by_book(db_session, user, book):
    repo = LoanRepository(Loan, db_session)
    loan = repo.create(obj_in={
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=14),
        "return_date": None
    })
    book_loans = repo.get_loans_by_book(book_id=book.id)
    assert any(l.id == loan.id for l in book_loans)

def test_remove_loan(db_session, user, book):
    repo = LoanRepository(Loan, db_session)
    loan = repo.create(obj_in={
        "user_id": user.id,
        "book_id": book.id,
        "loan_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=14),
        "return_date": None
    })
    repo.remove(id=loan.id)
    assert repo.get(loan.id) is None

def test_get_active_loans_exception():
    session = DummySession()
    repo = LoanRepository(Loan, session) 
    with pytest.raises(CustomException) as exc:
        repo.get_active_loans()
    assert "Erreur lors de la récupération des emprunts actifs" in str(exc.value)

def test_create_loan_exception():
    session = DummySession()
    repo = LoanRepository(Loan, session)
    with pytest.raises(CustomException) as exc:
        repo.create(obj_in={
            "user_id": 1,
            "book_id": 1,
            "loan_date": datetime.utcnow(),
            "due_date": datetime.utcnow() + timedelta(days=14)
        })
    assert "Erreur lors de la création" in str(exc.value)

def test_remove_loan_exception():
    session = DummySession()
    repo = LoanRepository(Loan, session)
    with pytest.raises(CustomException) as exc:
        repo.remove(id=1)  # Correction ici
    assert "Erreur lors de la suppression" in str(exc.value)