import logging
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any

from .base import BaseRepository
from ..models.books import Book
from ..models.categories import Category, book_category
from ..utils.cache import cache, invalidate_cache
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

class BookRepository(BaseRepository[Book, None, None]):
    def get_by_isbn(self, *, isbn: str) -> Optional[Book]:
        logger.debug(f"Recherche du livre avec ISBN: {isbn}")
        return self.db.query(Book).filter(Book.isbn == isbn).first()
    
    def get_by_title(self, *, title: str) -> List[Book]:
        logger.debug(f"Recherche des livres avec titre contenant: {title}")
        return self.db.query(Book).filter(Book.title.ilike(f"%{title}%")).all()
    
    def get_by_author(self, *, author: str) -> List[Book]:
        logger.debug(f"Recherche des livres avec auteur contenant: {author}")
        return self.db.query(Book).filter(Book.author.ilike(f"%{author}%")).all()
    
    def get_with_categories(self, *, id: int) -> Optional[Book]:
        logger.debug(f"Recherche du livre avec ID {id} et ses catégories")
        return self.db.query(Book).options(joinedload(Book.categories)).filter(Book.id == id).first()
    
    def get_multi_with_categories(self, *, skip: int = 0, limit: int = 100) -> List[Book]:
        logger.debug(f"Recherche de plusieurs livres avec catégories (skip={skip}, limit={limit})")
        return self.db.query(Book).options(joinedload(Book.categories)).offset(skip).limit(limit).all()
    
    def search(self, *, query: str) -> List[Book]:
        logger.debug(f"Recherche des livres par titre, auteur ou ISBN contenant: {query}")
        return self.db.query(Book).filter(
            or_(
                Book.title.ilike(f"%{query}%"),
                Book.author.ilike(f"%{query}%"),
                Book.isbn.ilike(f"%{query}%")
            )
        ).all()
    
    def get_by_category(self, *, category_id: int, skip: int = 0, limit: int = 100) -> List[Book]:
        logger.debug(f"Recherche des livres pour la catégorie ID {category_id} (skip={skip}, limit={limit})")
        return self.db.query(Book).join(book_category).filter(
            book_category.c.category_id == category_id
        ).offset(skip).limit(limit).all()
    
    def add_category(self, *, book_id: int, category_id: int) -> None:
        logger.info(f"Ajout de la catégorie ID {category_id} au livre ID {book_id}")
        book = self.get(id=book_id)
        if not book:
            logger.error(f"Livre avec l'ID {book_id} non trouvé")
            raise CustomException(f"Livre avec l'ID {book_id} non trouvé", status_code=404)
        
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            logger.error(f"Catégorie avec l'ID {category_id} non trouvée")
            raise CustomException(f"Catégorie avec l'ID {category_id} non trouvée", status_code=404)
        
        book.categories.append(category)
        try:
            self.db.commit()
            logger.info(f"Catégorie ID {category_id} ajoutée au livre ID {book_id}")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la catégorie : {e}")
            raise CustomException("Erreur lors de l'ajout de la catégorie au livre", status_code=500)
    
    def remove_category(self, *, book_id: int, category_id: int) -> None:
        logger.info(f"Suppression de la catégorie ID {category_id} du livre ID {book_id}")
        book = self.get(id=book_id)
        if not book:
            logger.error(f"Livre avec l'ID {book_id} non trouvé")
            raise CustomException(f"Livre avec l'ID {book_id} non trouvé", status_code=404)
        
        category = self.db.query(Category).filter(Category.id == category_id).first()
        if not category:
            logger.error(f"Catégorie avec l'ID {category_id} non trouvée")
            raise CustomException(f"Catégorie avec l'ID {category_id} non trouvée", status_code=404)
        
        book.categories.remove(category)
        try:
            self.db.commit()
            logger.info(f"Catégorie ID {category_id} supprimée du livre ID {book_id}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de la catégorie : {e}")
            raise CustomException("Erreur lors de la suppression de la catégorie du livre", status_code=500)
    
    @cache(expiry=60)  # Cache pendant 1 minute
    def get_stats(self) -> Dict[str, Any]:
        logger.info("Récupération des statistiques sur les livres")
        try:
            total_books = self.db.query(func.sum(Book.quantity)).scalar() or 0
            unique_books = self.db.query(func.count(Book.id)).scalar() or 0
            avg_publication_year = self.db.query(func.avg(Book.publication_year)).scalar() or 0
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des statistiques : {e}")
            raise CustomException("Erreur lors de la récupération des statistiques sur les livres", status_code=500)
        
        stats = {
            "total_books": total_books,
            "unique_books": unique_books,
            "avg_publication_year": avg_publication_year
        }
        logger.debug(f"Statistiques récupérées: {stats}")
        return stats

    def create(self, *, obj_in: Any) -> Any:
        logger.info("Création d'un nouveau livre")
        obj_in_data = obj_in.dict() if hasattr(obj_in, "dict") else dict(obj_in)
        model_columns = {c.name for c in self.model.__table__.columns}
        filtered_data = {k: v for k, v in obj_in_data.items() if k in model_columns}
        db_obj = self.model(**filtered_data)
        try:
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Livre créé avec ID {db_obj.id}")
        except Exception as e:
            logger.error(f"Erreur lors de la création du livre : {e}")
            raise CustomException("Erreur lors de la création du livre", status_code=500)
        return db_obj
    
    def update(self, *, db_obj: Book, obj_in: Any) -> Book:
        logger.info(f"Mise à jour du livre ID {db_obj.id}")
        try:
            book = super().update(db_obj=db_obj, obj_in=obj_in)
            invalidate_cache("src.repositories.books")
            logger.debug("Cache invalidé après mise à jour")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du livre : {e}")
            raise CustomException("Erreur lors de la mise à jour du livre", status_code=500)
        return book
    
    def remove(self, *, id: int) -> Book:
        logger.info(f"Suppression du livre ID {id}")
        try:
            book = super().remove(id=id)
            invalidate_cache("src.repositories.books")
            logger.debug("Cache invalidé après suppression")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du livre : {e}")
            raise CustomException("Erreur lors de la suppression du livre", status_code=500)
        return book
