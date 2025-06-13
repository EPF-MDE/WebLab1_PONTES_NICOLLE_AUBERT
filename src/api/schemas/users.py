import logging
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email de l'utilisateur")
    full_name: str = Field(..., min_length=1, max_length=100, description="Nom complet de l'utilisateur")
    is_active: bool = Field(True, description="Indique si l'utilisateur est actif")
    is_admin: bool = Field(False, description="Indique si l'utilisateur est administrateur")
    phone: Optional[str] = Field(None, max_length=20, description="Numéro de téléphone")
    address: Optional[str] = Field(None, max_length=200, description="Adresse")

    def __init__(self, **data):
        logger.debug(f"Creating UserBase with data: {data}")
        super().__init__(**data)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Mot de passe de l'utilisateur")

    def __init__(self, **data):
        logger.debug(f"Creating UserCreate with data: {data}")
        super().__init__(**data)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(None, description="Email de l'utilisateur")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nom complet de l'utilisateur")
    password: Optional[str] = Field(None, min_length=8, description="Mot de passe de l'utilisateur")
    is_active: Optional[bool] = Field(None, description="Indique si l'utilisateur est actif")
    is_admin: Optional[bool] = Field(None, description="Indique si l'utilisateur est administrateur")
    phone: Optional[str] = Field(None, max_length=20, description="Numéro de téléphone")
    address: Optional[str] = Field(None, max_length=200, description="Adresse")

    def __init__(self, **data):
        logger.debug(f"Updating User with data: {data}")
        super().__init__(**data)

class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    def __init__(self, **data):
        logger.debug(f"Creating UserInDBBase with data: {data}")
        super().__init__(**data)

class User(UserInDBBase):
    def __init__(self, **data):
        logger.debug(f"Creating User with data: {data}")
        super().__init__(**data)

class UserWithPassword(UserInDBBase):
    hashed_password: str

    def __init__(self, **data):
        logger.debug(f"Creating UserWithPassword with data: {data}")
        super().__init__(**data)