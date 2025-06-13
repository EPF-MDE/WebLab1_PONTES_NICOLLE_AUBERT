import logging
from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.users import User
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User, None, None]):
    def get_by_email(self, *, email: str) -> User:
        """
        Récupère un utilisateur par son email.
        """
        logger.debug(f"Recherche de l'utilisateur avec l'email: {email}")
        try:
            user = self.db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de l'utilisateur avec l'email '{email}': {e}")
            raise CustomException("Erreur lors de la recherche de l'utilisateur", status_code=500)
        if user:
            logger.info(f"Utilisateur trouvé: {user}")
        else:
            logger.warning(f"Aucun utilisateur trouvé avec l'email: {email}")
        return user