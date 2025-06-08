from typing import List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session
from functools import lru_cache
from src.utils.logger import logger

from ..repositories.books import BookRepository
from ..models.books import Book
from ..models.categories import Category
from ..api.schemas.books import BookCreate, BookUpdate
from .base import BaseService


class BookService(BaseService[Book, BookCreate, BookUpdate]):
    """
    Service pour la gestion des livres.
    """
    def __init__(self, repository: BookRepository):
        super().__init__(repository)
        self.repository = repository
        self.db = repository.db

    def get_by_isbn(self, *, isbn: str) -> Optional[Book]:
        """
        Récupère un livre par son ISBN.
        """
        return self.repository.get_by_isbn(isbn=isbn)
    
    def get_by_title(self, *, title: str) -> List[Book]:
        """
        Récupère des livres par leur titre (recherche partielle).
        """
        return self.repository.get_by_title(title=title)

    def get_by_author(self, *, author: str) -> List[Book]:
        """
        Récupère des livres par leur auteur (recherche partielle).
        """
        return self.repository.get_by_author(author=author)

    def create(self, *, obj_in: BookCreate) -> Book:
        """
        Crée un nouveau livre, en vérifiant que l'ISBN n'est pas déjà utilisé.
        """
        # Vérifier si l'ISBN est déjà utilisé
        existing_book = self.get_by_isbn(isbn=obj_in.isbn)
        if existing_book:
            raise ValueError("L'ISBN est déjà utilisé")

        # Extraire les category_ids
        category_ids = getattr(obj_in, "category_ids", None)
        # Créer le livre sans category_ids
        book_data = obj_in.dict(exclude={"category_ids"})
        book = Book(**book_data)
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)

        # Ajouter les catégories si besoin
        if category_ids:
            categories = self.db.query(Category).filter(Category.id.in_(category_ids)).all()
            book.categories = categories
            self.db.commit()
            self.db.refresh(book)

        return book

    def update_quantity(self, *, book_id: int, quantity_change: int) -> Book:
        """
        Met à jour la quantité d'un livre.
        """
        book = self.get(id=book_id)
        if not book:
            raise ValueError(f"Livre avec l'ID {book_id} non trouvé")

        new_quantity = book.quantity + quantity_change
        if new_quantity < 0:
            raise ValueError("La quantité ne peut pas être négative")

        return self.repository.update(db_obj=book, obj_in={"quantity": new_quantity})

@lru_cache(maxsize=128)
def get_all_books_cached():
    logger.info("Accès au cache pour la liste des livres")
    # Ici, retournez la liste des livres sans session SQLAlchemy
    # Par exemple, charger depuis un fichier statique ou une source externe
    return []