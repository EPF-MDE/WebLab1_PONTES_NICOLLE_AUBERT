import logging
from typing import List, Optional, Any, Dict, Union
from sqlalchemy.orm import Session

from ..repositories.books import BookRepository
from ..models.books import Book
from ..api.schemas.books import BookCreate, BookUpdate
from .base import BaseService
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

class BookService(BaseService[Book, BookCreate, BookUpdate]):
    """
    Service pour la gestion des livres.
    """
    def __init__(self, repository: BookRepository):
        super().__init__(repository)
        self.repository = repository
        logger.debug("BookService initialized with repository: %s", repository)
    
    def get_by_isbn(self, *, isbn: str) -> Optional[Book]:
        """
        Récupère un livre par son ISBN.
        """
        logger.info("Recherche du livre avec ISBN: %s", isbn)
        return self.repository.get_by_isbn(isbn=isbn)
    
    def get_by_title(self, *, title: str) -> List[Book]:
        """
        Récupère des livres par leur titre (recherche partielle).
        """
        logger.info("Recherche des livres avec le titre contenant: %s", title)
        return self.repository.get_by_title(title=title)
    
    def get_by_author(self, *, author: str) -> List[Book]:
        """
        Récupère des livres par leur auteur (recherche partielle).
        """
        logger.info("Recherche des livres avec l'auteur contenant: %s", author)
        return self.repository.get_by_author(author=author)
    
    def create(self, *, obj_in: BookCreate) -> Book:
        """
        Crée un nouveau livre, en vérifiant que l'ISBN n'est pas déjà utilisé.
        """
        logger.info("Tentative de création d'un livre avec ISBN: %s", obj_in.isbn)
        existing_book = self.get_by_isbn(isbn=obj_in.isbn)
        if existing_book:
            logger.warning("Échec de création: ISBN déjà utilisé (%s)", obj_in.isbn)
            raise CustomException("L'ISBN est déjà utilisé")  # Utilisation de CustomException
        
        book = self.repository.create(obj_in=obj_in)
        logger.info("Livre créé avec succès: %s", book)
        return book
    
    def update_quantity(self, *, book_id: int, quantity_change: int) -> Book:
        """
        Met à jour la quantité d'un livre.
        """
        logger.info("Mise à jour de la quantité pour le livre ID: %d, changement: %d", book_id, quantity_change)
        book = self.get(id=book_id)
        if not book:
            logger.error("Livre avec l'ID %d non trouvé", book_id)
            raise CustomException(f"Livre avec l'ID {book_id} non trouvé")  # Utilisation de CustomException
        
        new_quantity = book.quantity + quantity_change
        if new_quantity < 0:
            logger.warning("Tentative de définir une quantité négative pour le livre ID: %d", book_id)
            raise CustomException("La quantité ne peut pas être négative")  # Utilisation de CustomException
        
        updated_book = self.repository.update(db_obj=book, obj_in={"quantity": new_quantity})
        logger.info("Quantité mise à jour pour le livre ID: %d, nouvelle quantité: %d", book_id, new_quantity)
        return updated_book
    
    def search(self, query: str):
        """
        Recherche des livres par un terme donné (dans le titre, l'auteur, ou la description).
        """
        logger.info("Recherche de livres avec le terme: %s", query)
        return self.repository.search(query=query)