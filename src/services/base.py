import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.base import Base
from ..repositories.base import BaseRepository
from src.exceptions import CustomException  # Ajout de l'import

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)

class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Service de base avec des méthodes CRUD génériques.
    """
    def __init__(self, repository: BaseRepository):
        self.repository = repository
        logger.debug(f"{self.__class__.__name__} initialized with repository {repository.__class__.__name__}")
    
    def get(self, id: Any) -> Optional[ModelType]:
        try:
            logger.info(f"Getting object with id={id}")
            return self.repository.get(id=id)
        except Exception as e:
            logger.error(f"Error getting object with id={id}: {e}")
            raise CustomException(f"Erreur lors de la récupération de l'objet: {e}")
    
    def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        try:
            logger.info(f"Getting multiple objects with skip={skip}, limit={limit}")
            return self.repository.get_multi(skip=skip, limit=limit)
        except Exception as e:
            logger.error(f"Error getting multiple objects: {e}")
            raise CustomException(f"Erreur lors de la récupération des objets: {e}")
    
    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        try:
            logger.info(f"Creating new object with data: {obj_in}")
            return self.repository.create(obj_in=obj_in)
        except Exception as e:
            logger.error(f"Error creating object: {e}")
            raise CustomException(f"Erreur lors de la création de l'objet: {e}")
    
    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        try:
            logger.info(f"Updating object {db_obj} with data: {obj_in}")
            return self.repository.update(db_obj=db_obj, obj_in=obj_in)
        except Exception as e:
            logger.error(f"Error updating object: {e}")
            raise CustomException(f"Erreur lors de la mise à jour de l'objet: {e}")
    
    def remove(self, *, id: int) -> ModelType:
        try:
            logger.info(f"Removing object with id={id}")
            return self.repository.remove(id=id)
        except Exception as e:
            logger.error(f"Error removing object with id={id}: {e}")
            raise CustomException(f"Erreur lors de la suppression de l'objet: {e}")