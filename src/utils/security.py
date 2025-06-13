import logging
from datetime import datetime, timedelta
from typing import Any, Union, Optional

from jose import jwt
from passlib.context import CryptContext

from ..config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT.
    """
    logger.debug("Creating access token for subject: %s", subject)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
        logger.debug("Using custom expires_delta: %s", expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        logger.debug("Using default ACCESS_TOKEN_EXPIRE_MINUTES: %s", settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Access token created for subject: %s", subject)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Vérifie si un mot de passe en clair correspond à un hash.
    """
    logger.debug("Verifying password.")
    result = pwd_context.verify(plain_password, hashed_password)
    if result:
        logger.info("Password verification succeeded.")
    else:
        logger.warning("Password verification failed.")
    return result


def get_password_hash(password: str) -> str:
    """
    Génère un hash à partir d'un mot de passe en clair.
    """
    logger.debug("Hashing password.")
    hashed = pwd_context.hash(password)
    logger.info("Password hashed successfully.")
    return hashed