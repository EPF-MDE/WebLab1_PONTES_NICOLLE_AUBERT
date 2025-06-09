import logging
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Nom de la catégorie")
    description: Optional[str] = Field(None, max_length=200, description="Description de la catégorie")

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"CategoryBase created with data: {data}")

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Nom de la catégorie")

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"CategoryUpdate created with data: {data}")

class CategoryInDBBase(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"CategoryInDBBase created with data: {data}")

class Category(CategoryInDBBase):
    pass

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Titre du livre")
    author: str = Field(..., min_length=1, max_length=100, description="Auteur du livre")
    isbn: str = Field(..., min_length=10, max_length=13, description="ISBN du livre")
    publication_year: int = Field(..., ge=1000, le=datetime.now().year, description="Année de publication")
    description: Optional[str] = Field(None, max_length=1000, description="Description du livre")
    quantity: int = Field(..., ge=0, description="Nombre d'exemplaires disponibles")
    publisher: Optional[str] = Field(None, max_length=100, description="Éditeur du livre")
    language: Optional[str] = Field(None, max_length=50, description="Langue du livre")
    pages: Optional[int] = Field(None, gt=0, description="Nombre de pages")

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"BookBase created with data: {data}")

class BookCreate(BookBase):
    category_ids: Optional[List[int]] = Field(None, description="IDs des catégories")

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"BookCreate created with data: {data}")

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="Titre du livre")
    author: Optional[str] = Field(None, min_length=1, max_length=100, description="Auteur du livre")
    isbn: Optional[str] = Field(None, min_length=10, max_length=13, description="ISBN du livre")
    publication_year: Optional[int] = Field(None, ge=1000, le=datetime.now().year, description="Année de publication")
    description: Optional[str] = Field(None, max_length=1000, description="Description du livre")
    quantity: Optional[int] = Field(None, ge=0, description="Nombre d'exemplaires disponibles")
    publisher: Optional[str] = Field(None, max_length=100, description="Éditeur du livre")
    language: Optional[str] = Field(None, max_length=50, description="Langue du livre")
    pages: Optional[int] = Field(None, gt=0, description="Nombre de pages")
    category_ids: Optional[List[int]] = Field(None, description="IDs des catégories")

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"BookUpdate created with data: {data}")

class BookInDBBase(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"BookInDBBase created with data: {data}")

class Book(BookInDBBase):
    categories: List[Category] = []

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(f"Book created with data: {data}")