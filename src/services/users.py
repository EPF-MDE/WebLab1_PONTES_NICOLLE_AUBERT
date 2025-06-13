import logging
from typing import Optional, List, Any, Dict, Union
from sqlalchemy.orm import Session

from ..repositories.users import UserRepository
from ..models.users import User
from ..api.schemas.users import UserCreate, UserUpdate
from ..utils.security import get_password_hash, verify_password
from .base import BaseService
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    Service pour la gestion des utilisateurs.
    """
    def __init__(self, repository: UserRepository):
        super().__init__(repository)
        self.repository = repository
    
    def get_by_email(self, *, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email.
        """
        logger.debug(f"Recherche de l'utilisateur avec l'email: {email}")
        return self.repository.get_by_email(email=email)
    
    def create(self, *, obj_in: UserCreate) -> User:
        """
        Crée un nouvel utilisateur avec un mot de passe hashé.
        """
        logger.info(f"Tentative de création d'un utilisateur avec l'email: {obj_in.email}")
        existing_user = self.get_by_email(email=obj_in.email)
        if existing_user:
            logger.warning(f"Création échouée: l'email {obj_in.email} est déjà utilisé.")
            raise CustomException("L'email est déjà utilisé", status_code=409)
        
        hashed_password = get_password_hash(obj_in.password)
        user_data = obj_in.dict()
        del user_data["password"]
        user_data["hashed_password"] = hashed_password

        try:
            user = self.repository.create(obj_in=user_data)
            logger.info(f"Utilisateur créé avec succès: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
            raise CustomException("Erreur lors de la création de l'utilisateur", status_code=500)
    
    def update(
        self,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        Met à jour un utilisateur, en hashant le nouveau mot de passe si fourni.
        """
        logger.debug(f"Mise à jour de l'utilisateur: {db_obj.email}")
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            logger.debug(f"Hashage du nouveau mot de passe pour l'utilisateur: {db_obj.email}")
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            del update_data["password"]
        
        user = super().update(db_obj=db_obj, obj_in=update_data)
        logger.info(f"Utilisateur mis à jour: {user.email}")
        return user
    
    def authenticate(self, *, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur par email et mot de passe.
        """
        logger.debug(f"Tentative d'authentification pour l'email: {email}")
        user = self.get_by_email(email=email)
        if not user:
            logger.warning(f"Authentification échouée: utilisateur {email} non trouvé.")
            raise CustomException("Utilisateur non trouvé", status_code=404)
        if not verify_password(password, user.hashed_password):
            logger.warning(f"Authentification échouée: mot de passe incorrect pour {email}.")
            raise CustomException("Mot de passe incorrect", status_code=401)
        logger.info(f"Authentification réussie pour l'utilisateur: {email}")
        return user
    
    def is_active(self, *, user: User) -> bool:
        """
        Vérifie si un utilisateur est actif.
        """
        logger.debug(f"Vérification de l'état actif pour l'utilisateur: {user.email}")
        return user.is_active
    
    def is_admin(self, *, user: User) -> bool:
        """
        Vérifie si un utilisateur est administrateur.
        """
        logger.debug(f"Vérification du statut administrateur pour l'utilisateur: {user.email}")
        return user.is_admin