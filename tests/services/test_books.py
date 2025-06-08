import pytest
from sqlalchemy.orm import Session

from src.models.books import Book
from src.repositories.books import BookRepository
from src.services.books import BookService
from src.api.schemas.books import BookCreate, BookUpdate

def test_create_book(db_session: Session):
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    book_in = BookCreate(
        title="Test Book",
        author="Test Author",
        isbn="1234567890123",
        publication_year=2020,
        description="A test book.",
        quantity=5
    )

    book = service.create(obj_in=book_in)

    assert book.title == "Test Book"
    assert book.author == "Test Author"
    assert book.isbn == "1234567890123"
    assert book.publication_year == 2020
    assert book.description == "A test book."
    assert book.quantity == 5

def test_create_book_isbn_already_used(db_session: Session):
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    book_in = BookCreate(
        title="Book1",
        author="Author1",
        isbn="1111111111111",
        publication_year=2021,
        description="Book 1",
        quantity=2
    )
    service.create(obj_in=book_in)

    # Tentative de création avec le même ISBN
    with pytest.raises(ValueError):
        service.create(obj_in=book_in)

def test_update_book(db_session: Session):
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    book_in = BookCreate(
        title="Book2",
        author="Author2",
        isbn="2222222222222",
        publication_year=2022,
        description="Book 2",
        quantity=3
    )
    book = service.create(obj_in=book_in)

    book_update = BookUpdate(title="Updated Title", quantity=10)
    updated_book = service.update(db_obj=book, obj_in=book_update)

    assert updated_book.title == "Updated Title"
    assert updated_book.quantity == 10

def test_get_by_isbn(db_session: Session):
    repository = BookRepository(Book, db_session)
    service = BookService(repository)

    book_in = BookCreate(
        title="Book3",
        author="Author3",
        isbn="3333333333333",
        publication_year=2023,
        description="Book 3",
        quantity=1
    )
    book = service.create(obj_in=book_in)

    retrieved_book = service.get_by_isbn(isbn="3333333333333")
    assert retrieved_book is not None
    assert retrieved_book.id == book.id

    # ISBN inexistant
    assert service.get_by_isbn(isbn="notfound") is None