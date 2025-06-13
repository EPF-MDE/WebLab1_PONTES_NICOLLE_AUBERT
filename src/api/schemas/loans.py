import logging
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from .users import User
from .books import Book

logger = logging.getLogger(__name__)

class LoanBase(BaseModel):
    user_id: int = Field(..., description="ID de l'utilisateur")
    book_id: int = Field(..., description="ID du livre")
    loan_date: datetime = Field(default_factory=datetime.utcnow, description="Date d'emprunt")
    return_date: Optional[datetime] = Field(None, description="Date de retour")
    due_date: datetime = Field(..., description="Date d'échéance")
    extended: bool = Field(False, description="Indique si l'emprunt a été prolongé")

    def __init__(self, **data):
        logger.debug(f"Creating LoanBase with data: {data}")
        super().__init__(**data)

class LoanCreate(LoanBase):
    def __init__(self, **data):
        logger.debug(f"Creating LoanCreate with data: {data}")
        super().__init__(**data)

class LoanUpdate(BaseModel):
    return_date: Optional[datetime] = Field(None, description="Date de retour")
    due_date: Optional[datetime] = Field(None, description="Date d'échéance")
    extended: Optional[bool] = Field(None, description="Indique si l'emprunt a été prolongé")

    def __init__(self, **data):
        logger.debug(f"Updating Loan with data: {data}")
        super().__init__(**data)

class LoanInDBBase(LoanBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        logger.debug(f"Creating LoanInDBBase with data: {data}")
        super().__init__(**data)

class Loan(LoanInDBBase):
    def __init__(self, **data):
        logger.debug(f"Creating Loan with data: {data}")
        super().__init__(**data)

class LoanWithDetails(Loan):
    user: User
    book: Book

    def __init__(self, **data):
        logger.debug(f"Creating LoanWithDetails with data: {data}")
        super().__init__(**data)