import pytest
from sqlalchemy.orm import Session, sessionmaker
from datetime import datetime, timedelta

from src.models.loans import Loan
from src.models.books import Book
from src.models.users import User
from src.models.reservation import Reservation
from src.repositories.loans import LoanRepository
from src.repositories.books import BookRepository
from src.repositories.users import UserRepository
from src.repositories.reservation import ReservationRepository
from src.services.loans import LoanService
import os
from sqlalchemy import create_engine, inspect
from src.models.base import Base

def create_user(db_session):
    user = User(
        email="loanuser@example.com",
        hashed_password="fakehash",
        full_name="Loan User",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.mark.usefixtures("tmp_path")
def test_drop_and_recreate_database(tmp_path):
    """
    Test pour supprimer et recréer la base de données de test.
    """
    db_path = tmp_path / "test_loans.sqlite"
    db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    assert "loans" in inspector.get_table_names()

    Base.metadata.drop_all(engine)
    inspector = inspect(engine)
    assert "loans" not in inspector.get_table_names()

    Base.metadata.create_all(engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "loans" in tables
    assert "users" in tables
    assert "books" in tables

def create_book(db_session, isbn=None):
    if isbn is None:
        # Génère un ISBN unique à chaque appel
        isbn = str(4444444444444 + int(datetime.utcnow().timestamp() * 1000000) % 1000000000000)
    book = Book(
        title="Loan Book",
        author="Loan Author",
        isbn=isbn,
        publication_year=2024,
        description="Loan book",
        quantity=2
    )
    db_session.add(book)
    db_session.commit()
    db_session.refresh(book)
    return book

def test_create_loan(db_session: Session):
    user = create_user(db_session)
    book = create_book(db_session)

    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)

    loan = service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)
    assert loan.user_id == user.id
    assert loan.book_id == book.id
    assert loan.return_date is None
    assert loan.due_date > loan.loan_date

def test_create_loan_book_not_available(db_session: Session):
    user = create_user(db_session)
    book = create_book(db_session)
    book.quantity = 0
    db_session.commit()

    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)

    with pytest.raises(ValueError):
        service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)

def test_return_loan(db_session: Session):
    user = create_user(db_session)
    book = create_book(db_session)

    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)

    loan = service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)
    returned_loan = service.return_loan(loan_id=loan.id)
    assert returned_loan.return_date is not None

def test_extend_loan(db_session: Session):
    user = create_user(db_session)
    book = create_book(db_session)

    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)

    loan = service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)
    old_due_date = loan.due_date
    extended_loan = service.extend_loan(loan_id=loan.id, extension_days=7)
    assert extended_loan.due_date > old_due_date

def test_create_loan_user_not_found(db_session: Session):
    book = create_book(db_session)
    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)
    with pytest.raises(ValueError, match="Utilisateur avec l'ID 9999 non trouvé"):
        service.create_loan(user_id=9999, book_id=book.id, loan_period_days=7)

def test_create_loan_user_inactive(db_session: Session):
    user = create_user(db_session)
    user.is_active = False
    db_session.commit()
    book = create_book(db_session)
    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)
    with pytest.raises(ValueError, match="L'utilisateur est inactif et ne peut pas emprunter de livres"):
        service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)

def test_create_loan_book_not_found(db_session: Session):
    user = create_user(db_session)
    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)
    with pytest.raises(ValueError, match="Livre avec l'ID 9999 non trouvé"):
        service.create_loan(user_id=user.id, book_id=9999, loan_period_days=7)

def test_create_loan_user_already_has_active_loan(db_session: Session):
    user = create_user(db_session)
    book = create_book(db_session)
    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)
    service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)
    with pytest.raises(ValueError, match="L'utilisateur a déjà emprunté ce livre et ne l'a pas encore rendu"):
        service.create_loan(user_id=user.id, book_id=book.id, loan_period_days=7)

def test_create_loan_user_max_active_loans(db_session: Session):
    user = create_user(db_session)
    books = [create_book(db_session) for _ in range(6)]
    loan_repository = LoanRepository(Loan, db_session)
    book_repository = BookRepository(Book, db_session)
    user_repository = UserRepository(User, db_session)
    reservation_repository = ReservationRepository(Reservation, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)
    # Create 5 active loans
    for i in range(5):
        service.create_loan(user_id=user.id, book_id=books[i].id, loan_period_days=7)
    # 6th loan should fail
    with pytest.raises(ValueError, match="L'utilisateur a atteint la limite d'emprunts simultanés"):
        service.create_loan(user_id=user.id, book_id=books[5].id, loan_period_days=7)
        def test_drop_and_recreate_database(tmp_path):
            # Assume SQLite test DB path
            db_path = tmp_path / "test_db.sqlite"
            db_url = f"sqlite:///{db_path}"

            # Create engine and initial tables
            engine = create_engine(db_url)
            Base.metadata.create_all(engine)

            # Drop all tables
            Base.metadata.drop_all(engine)
            # Recreate all tables
            Base.metadata.create_all(engine)

            # Check that tables exist
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            assert "loans" in tables
            assert "users" in tables
            assert "books" in tables