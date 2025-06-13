import logging
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..models.base import Base
from src.exceptions import CustomException  # Ajout de l'import

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

logger = logging.getLogger(__name__)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialise le repository avec un modèle et une session de base de données.
        """
        self.model = model
        self.db = db
        logger.debug(f"BaseRepository initialized for model {self.model.__name__}")

    def get(self, id: int):
        """
        Récupère un objet par son ID.
        """
        logger.debug(f"Fetching {self.model.__name__} with id={id}")
        obj = self.db.query(self.model).filter(self.model.id == id).first()
        return obj  # Pas d'exception ici

    def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Récupère plusieurs objets avec pagination.
        """
        logger.debug(f"Fetching multiple {self.model.__name__} objects: skip={skip}, limit={limit}")
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, *, obj_in: Any) -> Any:
        """
        Crée un nouvel objet.
        """
        try:
            obj_in_data = obj_in.dict() if hasattr(obj_in, "dict") else dict(obj_in)
            db_obj = self.model(**obj_in_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Created new {self.model.__name__} with id={db_obj.id}")
            return db_obj
        except Exception as e:
            logger.error(f"Erreur lors de la création : {e}")
            raise CustomException("Erreur lors de la création", status_code=500)

    def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        Met à jour un objet existant.
        """
        try:
            update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else dict(obj_in)
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id={db_obj.id}")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour de {self.model.__name__} : {e}")
            raise CustomException(f"Erreur lors de la mise à jour de {self.model.__name__}", status_code=500)
        return db_obj

    def remove(self, *, id: int) -> Any:
        """
        Supprime un objet.
        """
        try:
            obj = self.db.query(self.model).get(id)
            if not obj:
                raise CustomException("Objet non trouvé", status_code=404)
            self.db.delete(obj)
            self.db.commit()
            logger.info(f"Removed {self.model.__name__} with id={id}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {self.model.__name__} : {e}")
            raise CustomException("Erreur lors de la suppression", status_code=500)
        return obj