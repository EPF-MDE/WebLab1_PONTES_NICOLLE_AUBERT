import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from pydantic import BaseModel

from ...db.session import get_db
from ...models.users import User as UserModel
from ..schemas.users import User, UserCreate, UserUpdate
from ...repositories.users import UserRepository
from ...services.users import UserService
from ..dependencies import get_current_active_user, get_current_admin_user
from src.exceptions import CustomException  # Ajout de l'import
from ...utils.security import verify_password, get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100 #,
    #current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère la liste des utilisateurs.
    """
    logger.info("Fetching users: skip=%d, limit=%d", skip, limit)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    users = service.get_multi(skip=skip, limit=limit)
    logger.debug("Fetched %d users", len(users))
    return users


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
    #,
    #current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Crée un nouvel utilisateur.
    """
    logger.info("Creating user with email: %s", user_in.email)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    try:
        user = service.create(obj_in=user_in)
        logger.info("User created with id: %s", user.id)
        return user
    except CustomException as e:
        logger.error("Error creating user: %s", str(e))
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error creating user: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création de l'utilisateur"
        )


@router.get("/me", response_model=User)
def read_user_me(
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Récupère l'utilisateur connecté.
    """
    logger.info("Fetching current user: id=%s", current_user.id)
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user = Depends(get_current_active_user)
) -> Any:
    """
    Met à jour l'utilisateur connecté.
    """
    logger.info("Updating current user: id=%s", current_user.id)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    try:
        user = service.update(db_obj=current_user, obj_in=user_in)
        logger.info("Current user updated: id=%s", user.id)
        return user
    except CustomException as e:
        logger.error("Error updating current user: %s", str(e))
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error updating current user: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de l'utilisateur"
        )


@router.get("/{id}", response_model=User)
def read_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère un utilisateur par son ID.
    """
    logger.info("Fetching user by id: %d", id)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        logger.warning("User not found: id=%d", id)
        raise HTTPException( 
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    logger.debug("User found: id=%d", id)
    return user


@router.put("/{id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    user_in: UserUpdate,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Met à jour un utilisateur.
    """
    logger.info("Updating user: id=%d", id)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        logger.warning("User not found for update: id=%d", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    try:
        user = service.update(db_obj=user, obj_in=user_in)
        logger.info("User updated: id=%d", id)
        return user
    except CustomException as e:
        logger.error("Error updating user id=%d: %s", id, str(e))
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error updating user id=%d: %s", id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la mise à jour de l'utilisateur"
        )


@router.delete("/{id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Supprime un utilisateur.
    """
    logger.info("Deleting user: id=%d", id)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    user = service.get(id=id)
    if not user:
        logger.warning("User not found for deletion: id=%d", id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    if user.id == current_user.id:
        logger.warning("Attempt to delete current user: id=%d", id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Impossible de supprimer l'utilisateur connecté"
        )
    try:
        user = service.remove(id=id)
        logger.info("User deleted: id=%d", id)
        return user
    except CustomException as e:
        logger.error("Error deleting user id=%d: %s", id, str(e))
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error deleting user id=%d: %s", id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de l'utilisateur"
        )


@router.get("/by-email/{email}", response_model=User)
def get_user_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Récupère un utilisateur par son email.
    """
    logger.info("Fetching user by email: %s", email)
    repository = UserRepository(UserModel, db)
    service = UserService(repository)
    try:
        user = service.get_by_email(email=email)
        if not user:
            logger.warning("User not found by email: %s", email)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        logger.debug("User found by email: %s", email)
        return user
    except CustomException as e:
        logger.error("Error fetching user by email: %s", str(e))
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logger.error("Unexpected error fetching user by email: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération de l'utilisateur par email"
        )


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.post("/me/change-password")
def change_password(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    Permet à l'utilisateur connecté de changer son mot de passe.
    """
    # Vérifie l'ancien mot de passe
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe actuel incorrect")
    # Met à jour le mot de passe
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    return {"message": "Mot de passe changé avec succès"}
