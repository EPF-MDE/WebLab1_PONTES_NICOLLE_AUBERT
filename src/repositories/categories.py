import logging
from sqlalchemy.orm import Session
from typing import List, Optional

from .base import BaseRepository
from ..models.categories import Category
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

class CategoryRepository(BaseRepository[Category, None, None]):
    def get_by_name(self, *, name: str) -> Optional[Category]:
        """
        Récupère une catégorie par son nom.
        """
        logger.debug(f"Recherche de la catégorie avec le nom: {name}")
        try:
            category = self.db.query(Category).filter(Category.name == name).first()
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de la catégorie '{name}': {e}")
            raise CustomException("Erreur lors de la recherche de la catégorie", status_code=500)
        if category:
            logger.info(f"Catégorie trouvée: {category}")
        else:
            logger.info(f"Aucune catégorie trouvée pour le nom: {name}")
        return category
    
    def get_or_create(self, *, name: str, description: Optional[str] = None) -> Category:
        """
        Récupère une catégorie par son nom ou la crée si elle n'existe pas.
        """
        logger.debug(f"get_or_create appelé avec name={name}, description={description}")
        try:
            category = self.get_by_name(name=name)
            if not category:
                logger.info(f"Catégorie '{name}' non trouvée, création en cours.")
                category_data = {"name": name}
                if description:
                    category_data["description"] = description
                category = self.create(obj_in=category_data)
                logger.info(f"Catégorie créée: {category}")
            else:
                logger.info(f"Catégorie '{name}' déjà existante.")
        except Exception as e:
            logger.error(f"Erreur lors de la récupération ou création de la catégorie '{name}': {e}")
            raise CustomException("Erreur lors de la récupération ou création de la catégorie", status_code=500)
        return category