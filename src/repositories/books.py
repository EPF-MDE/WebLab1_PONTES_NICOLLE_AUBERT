from sqlalchemy.orm import Session
from typing import List

from .base import BaseRepository
from ..models.books import Book
from src.api.schemas.books import BookCreate, BookUpdate


class BookRepository(BaseRepository[Book, BookCreate, BookUpdate]):
    def __init__(self, model, db):
        self.model = model
        self.db = db

    def get_by_isbn(self, isbn: str):
        """
        Récupère un livre par son ISBN.
        """
        return self.db.query(self.model).filter(self.model.isbn == isbn).first()
    
    def get_by_title(self, db: Session, *, title: str) -> List[Book]:
        """
        Récupère des livres par leur titre (recherche partielle).
        """
        return db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()

    def get_by_author(self, db: Session, *, author: str) -> List[Book]:
        """
        Récupère des livres par leur auteur (recherche partielle).
        """
        return db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()