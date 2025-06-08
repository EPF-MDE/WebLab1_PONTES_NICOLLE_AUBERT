from src.models.reservation import Reservation
from src.repositories.reservation import ReservationRepository
from src.services.loans import LoanService
from src.models.users import User
from src.models.books import Book
from src.repositories.loans import LoanRepository
from src.repositories.books import BookRepository
from src.repositories.users import UserRepository

class ReservationRepository:
    def __init__(self, model, db_session):
        self.model = model
        self.db = db_session

    def add(self, reservation):
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return reservation

def test_reserve_book(db_session):
    # Crée un utilisateur et un livre
    user = User(full_name="Test", email="test@test.com", hashed_password="fakehash", is_active=True, is_admin=False)
    book = Book(title="Test Book", author="Author", isbn="1234567890123", publication_year=2024, description="desc", quantity=1)
    db_session.add(user)
    db_session.add(book)
    db_session.commit()
    db_session.refresh(user)
    db_session.refresh(book)

    reservation_repository = ReservationRepository(Reservation, db_session)
    loan_repository = LoanRepository(None, db_session)
    book_repository = BookRepository(None, db_session)
    user_repository = UserRepository(None, db_session)
    service = LoanService(loan_repository, book_repository, user_repository, reservation_repository)
    reservation = service.reserve_book(user_id=user.id, book_id=book.id)

    assert reservation.user_id == user.id
    assert reservation.book_id == book.id