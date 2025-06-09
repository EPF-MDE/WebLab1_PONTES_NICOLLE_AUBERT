import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from ...db.session import get_db
from ...models.loans import Loan as LoanModel
from ...models.books import Book as BookModel
from ...models.users import User as UserModel
from ..schemas.loans import Loan, LoanCreate, LoanUpdate, LoanWithDetails
from ...repositories.loans import LoanRepository
from ...repositories.books import BookRepository
from ...repositories.users import UserRepository
from ...services.loans import LoanService
from ..dependencies import get_current_active_user, get_current_admin_user
from src.exceptions import CustomException  # Ajout de l'import

logger = logging.getLogger(__name__)

router = APIRouter()

class LoanRequest(BaseModel):
    book_id: int
    loan_period_days: int = 14


@router.get("/me", response_model=List[LoanWithDetails])
def get_my_loans(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    from sqlalchemy.orm import joinedload
    loans = db.query(LoanModel).options(joinedload(LoanModel.book)).filter(LoanModel.user_id == current_user.id).all()
    return loans


@router.post("/me", response_model=Loan, status_code=status.HTTP_201_CREATED)
def create_my_loan(
    *,
    db: Session = Depends(get_db),
    data: LoanRequest,
    current_user = Depends(get_current_active_user)
):
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loan = service.create_loan(
            user_id=current_user.id,
            book_id=data.book_id,
            loan_period_days=data.loan_period_days
        )
        return loan
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de la création de l'emprunt")


# --- ENSUITE seulement les routes dynamiques ---
@router.get("/{id}", response_model=Loan)
def read_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    logger.info(f"User {current_user.id} requests loan {id}")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loan = service.get(id=id)
        if not loan:
            logger.warning(f"Loan {id} not found")
            raise CustomException("Emprunt non trouvé", status_code=status.HTTP_404_NOT_FOUND)
        if not current_user.is_admin and current_user.id != loan.user_id:
            logger.warning(f"User {current_user.id} forbidden to access loan {id}")
            raise CustomException("Accès non autorisé", status_code=status.HTTP_403_FORBIDDEN)
        logger.debug(f"Loan {id} returned to user {current_user.id}")
        return loan
    except CustomException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching loan {id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération de l'emprunt")


@router.post("/{id}/return", response_model=Loan)
def return_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info(f"Admin {current_user.id} returns loan {id}")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loan = service.return_loan(loan_id=id)
        logger.info(f"Loan {id} marked as returned")
        return loan
    except CustomException as e:
        logger.error(f"Error returning loan {id}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error returning loan {id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du retour de l'emprunt")


@router.post("/{id}/extend", response_model=Loan)
def extend_loan(
    *,
    db: Session = Depends(get_db),
    id: int,
    extension_days: int = 7,
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info(f"Admin {current_user.id} extends loan {id} by {extension_days} days")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loan = service.extend_loan(loan_id=id, extension_days=extension_days)
        logger.info(f"Loan {id} extended by {extension_days} days")
        return loan
    except CustomException as e:
        logger.error(f"Error extending loan {id}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error extending loan {id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la prolongation de l'emprunt")


@router.get("/active/", response_model=List[Loan])
def read_active_loans(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info(f"Admin {current_user.id} requests active loans")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loans = service.get_active_loans()
        logger.debug(f"Found {len(loans)} active loans")
        return loans
    except CustomException as e:
        logger.error(f"Error fetching active loans: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching active loans: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des emprunts actifs")


@router.get("/overdue/", response_model=List[Loan])
def read_overdue_loans(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info(f"Admin {current_user.id} requests overdue loans")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loans = service.get_overdue_loans()
        logger.debug(f"Found {len(loans)} overdue loans")
        return loans
    except CustomException as e:
        logger.error(f"Error fetching overdue loans: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching overdue loans: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des emprunts en retard")


@router.get("/user/{user_id}", response_model=List[Loan])
def read_user_loans(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user = Depends(get_current_active_user)
) -> Any:
    if not current_user.is_admin and current_user.id != user_id:
        logger.warning(f"User {current_user.id} forbidden to access loans of user {user_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès non autorisé"
        )
    logger.info(f"User {current_user.id} requests loans for user {user_id}")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loans = service.get_loans_by_user(user_id=user_id)
        logger.debug(f"Found {len(loans)} loans for user {user_id}")
        return loans
    except CustomException as e:
        logger.error(f"Error fetching loans for user {user_id}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching loans for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des emprunts de l'utilisateur")


@router.get("/book/{book_id}", response_model=List[Loan])
def read_book_loans(
    *,
    db: Session = Depends(get_db),
    book_id: int,
    current_user = Depends(get_current_admin_user)
) -> Any:
    logger.info(f"Admin {current_user.id} requests loans for book {book_id}")
    loan_repository = LoanRepository(LoanModel, db)
    book_repository = BookRepository(BookModel, db)
    user_repository = UserRepository(UserModel, db)
    service = LoanService(loan_repository, book_repository, user_repository)
    try:
        loans = service.get_loans_by_book(book_id=book_id)
        logger.debug(f"Found {len(loans)} loans for book {book_id}")
        return loans
    except CustomException as e:
        logger.error(f"Error fetching loans for book {book_id}: {e}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error fetching loans for book {book_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des emprunts du livre")