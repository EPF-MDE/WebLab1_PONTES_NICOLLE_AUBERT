import logging
from typing import Generic, TypeVar, List, Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Query
from fastapi import Query as QueryParam

T = TypeVar('T')

logger = logging.getLogger(__name__)

class PaginationParams:
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_desc: bool = False
    ):
        self.skip = skip
        self.limit = limit
        self.sort_by = sort_by
        self.sort_desc = sort_desc


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        arbitrary_types_allowed = True


def paginate(query: Query, params: PaginationParams, schema) -> Page:
    """
    Pagine une requête SQLAlchemy.
    """
    logger.debug(f"Pagination params: skip={params.skip}, limit={params.limit}, sort_by={params.sort_by}, sort_desc={params.sort_desc}")

    # Compter le nombre total d'éléments
    total = query.count()
    logger.info(f"Total items in query: {total}")
    
    # Appliquer le tri si spécifié
    if params.sort_by:
        if hasattr(schema, params.sort_by):
            column = getattr(schema, params.sort_by)
            logger.debug(f"Sorting by: {params.sort_by}, descending: {params.sort_desc}")
            if params.sort_desc:
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)
        else:
            logger.warning(f"Sort column '{params.sort_by}' does not exist in schema '{schema.__name__}'")
    
    # Appliquer la pagination
    items = query.offset(params.skip).limit(params.limit).all()
    logger.debug(f"Fetched {len(items)} items from database")

    # Calculer le nombre de pages
    pages = (total + params.limit - 1) // params.limit if params.limit > 0 else 1
    page = (params.skip // params.limit) + 1 if params.limit > 0 else 1

    logger.info(f"Returning page {page}/{pages} with size {params.limit}")

    return Page(
        items=items,
        total=total,
        page=page,
        size=params.limit,
        pages=pages
    )