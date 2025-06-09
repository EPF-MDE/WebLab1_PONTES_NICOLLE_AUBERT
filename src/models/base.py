import logging
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from datetime import datetime
import re

logger = logging.getLogger(__name__)

@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Génère automatiquement le nom de table à partir du nom de la classe
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        tablename = re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
        logger.debug(f"Generated tablename '{tablename}' for class '{cls.__name__}'")
        return tablename