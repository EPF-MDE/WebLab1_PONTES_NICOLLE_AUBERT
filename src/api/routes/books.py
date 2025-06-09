import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Any, Optional
from ...utils.pagination import PaginationParams, paginate, Page
from ...db.session import get_db
from ...models.books import Book as BookModel
from ...models.books import book_category  # nécessaire pour la jointure
from ..schemas.books import Book, BookCreate, BookUpdate
from ...repositories.books import BookRepository
from ...services.books import BookService
from ..dependencies import get_current_active_user, get_current_admin_user
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=Page[Book])
def read_books(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    sort_desc: bool = Query(False)
) -> Any:
    logger.info("Fetching books: skip=%s, limit=%s, sort_by=%s, sort_desc=%s", skip, limit, sort_by, sort_desc)
    repository = BookRepository(BookModel, db)
    query = db.query(BookModel)
    params = PaginationParams(skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc)
    return paginate(query, params, BookModel)

@router.post("/", response_model=Book, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    db: Session = Depends(get_db),
    book_in: BookCreate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info("Creating a new book: %s", book_in)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        book = service.create(obj_in=book_in)
        logger.info("Book created with ID: %s", book.id)
        return book
    except CustomException as e:
        logger.error("Error creating book: %s", e)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error creating book: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la création du livre"
        )

@router.get("/{id}", response_model=Book)
def read_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    logger.info("Fetching book with ID: %s", id)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        book = service.get(id=id)
        if not book:
            logger.warning("Book not found: ID %s", id)
            raise CustomException("Livre non trouvé", status_code=status.HTTP_404_NOT_FOUND)
        return book
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error fetching book: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la récupération du livre"
        )

@router.put("/{id}", response_model=Book)
def update_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    book_in: BookUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info("Updating book ID: %s", id)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        book = service.get(id=id)
        if not book:
            logger.warning("Book not found for update: ID %s", id)
            raise CustomException("Livre non trouvé", status_code=status.HTTP_404_NOT_FOUND)
        book = service.update(db_obj=book, obj_in=book_in)
        logger.info("Book updated: ID %s", id)
        return book
    except CustomException as e:
        logger.error("Error updating book ID %s: %s", id, e)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error updating book: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la mise à jour du livre"
        )

@router.delete("/{id}", response_model=Book)
def delete_book(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info("Deleting book ID: %s", id)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        book = service.get(id=id)
        if not book:
            logger.warning("Book not found for deletion: ID %s", id)
            raise CustomException("Livre non trouvé", status_code=status.HTTP_404_NOT_FOUND)
        book = service.remove(id=id)
        logger.info("Book deleted: ID %s", id)
        return book
    except CustomException as e:
        logger.error("Error deleting book ID %s: %s", id, e)
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error deleting book: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de la suppression du livre"
        )

@router.get("/search/title/{title}", response_model=List[Book])
def search_books_by_title(
    *,
    db: Session = Depends(get_db),
    title: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    logger.info("Searching books by title: %s", title)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        books = service.get_by_title(title=title)
        return books
    except Exception as e:
        logger.error("Error searching books by title: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche par titre"
        )

@router.get("/search/author/{author}", response_model=List[Book])
def search_books_by_author(
    *,
    db: Session = Depends(get_db),
    author: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    logger.info("Searching books by author: %s", author)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        books = service.get_by_author(author=author)
        return books
    except Exception as e:
        logger.error("Error searching books by author: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche par auteur"
        )

@router.get("/search/isbn/{isbn}", response_model=Book)
def search_book_by_isbn(
    *,
    db: Session = Depends(get_db),
    isbn: str,
    current_user = Depends(get_current_active_user)
) -> Any:
    logger.info("Searching book by ISBN: %s", isbn)
    repository = BookRepository(BookModel, db)
    service = BookService(repository)
    try:
        book = service.get_by_isbn(isbn=isbn)
        if not book:
            logger.warning("Book not found by ISBN: %s", isbn)
            raise CustomException("Livre non trouvé", status_code=status.HTTP_404_NOT_FOUND)
        return book
    except CustomException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Error searching book by ISBN: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche par ISBN"
        )

@router.get("/search/", response_model=Page[Book])
def search_books(
    db: Session = Depends(get_db),
    query: Optional[str] = Query(None, min_length=1),
    category_id: Optional[int] = Query(None),
    author: Optional[str] = Query(None),
    publication_year: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    sort_by: Optional[str] = Query(None),
    sort_desc: bool = Query(False),
    current_user = Depends(get_current_active_user)
) -> Any:
    logger.info("Advanced search: query=%s, category_id=%s, author=%s, publication_year=%s", query, category_id, author, publication_year)
    repository = BookRepository(BookModel, db)
    try:
        search_query = db.query(BookModel)
        if query:
            search_query = search_query.filter(
                or_(
                    BookModel.title.ilike(f"%{query}%"),
                    BookModel.author.ilike(f"%{query}%"),
                    BookModel.isbn.ilike(f"%{query}%"),
                    BookModel.description.ilike(f"%{query}%")
                )
            )
        if category_id:
            search_query = search_query.join(book_category).filter(
                book_category.c.category_id == category_id
            )
        if author:
            search_query = search_query.filter(BookModel.author.ilike(f"%{author}%"))
        if publication_year:
            search_query = search_query.filter(BookModel.publication_year == publication_year)
        params = PaginationParams(skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc)
        return paginate(search_query, params, BookModel)
    except Exception as e:
        logger.error("Error in advanced search: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche avancée"
        )
