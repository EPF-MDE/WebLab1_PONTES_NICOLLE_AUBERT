import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from ...db.session import get_db
from ...models.users import User as UserModel
from ..schemas.token import Token
from ...repositories.users import UserRepository
from ...services.users import UserService
from ...utils.security import create_access_token
from ...config import settings
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    logger.info("Login attempt for user: %s", form_data.username)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    try:
        user = service.authenticate(email=form_data.username, password=form_data.password)
        if not user:
            logger.warning("Failed login for user: %s (invalid credentials)", form_data.username)
            raise CustomException("Email ou mot de passe incorrect", status_code=status.HTTP_401_UNAUTHORIZED)
        if not service.is_active(user=user):
            logger.warning("Inactive user login attempt: %s", form_data.username)
            raise CustomException("Utilisateur inactif", status_code=status.HTTP_401_UNAUTHORIZED)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token(
            subject=user.id, expires_delta=access_token_expires
        )
        logger.info("User %s authenticated successfully", form_data.username)
        return {
            "access_token": token,
            "token_type": "bearer",
        }
    except CustomException as ce:
        raise HTTPException(
            status_code=ce.status_code,
            detail=ce.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'authentification : {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne lors de l'authentification",
        )