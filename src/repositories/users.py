from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.users import User
from src.api.schemas.users import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def get_by_email(self, *, email: str) -> User:
        """
        Récupère un utilisateur par son email.
        """
        return self.db.query(User).filter(User.email == email).first()