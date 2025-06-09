import pytest
from datetime import datetime, timedelta
from src.services.loans import LoanService
from src.exceptions import CustomException

class DummyLoanRepo:
    def __init__(self):
        self.active_loans = []
        self.loans = []
        self.created = False
        self.updated = False
        self.last_update = None
        self.last_create = None
        self.last_get_id = None
    def get_active_loans(self):
        return self.active_loans
    def get(self, id):
        self.last_get_id = id
        for loan in self.loans:
            if loan.id == id:
                return loan
        return None
    def create(self, obj_in):
        self.created = True
        self.last_create = obj_in
        loan = type("Loan", (), obj_in.copy())()
        loan.id = 42
        loan.return_date = obj_in.get("return_date", None)
        loan.due_date = obj_in.get("due_date", datetime.utcnow() + timedelta(days=14))
        loan.loan_date = obj_in.get("loan_date", datetime.utcnow())
        loan.user_id = obj_in["user_id"]
        loan.book_id = obj_in["book_id"]
        return loan
    def update(self, db_obj, obj_in):
        self.updated = True
        self.last_update = obj_in
        for k, v in obj_in.items():
            setattr(db_obj, k, v)
        return db_obj

class DummyBookRepo:
    def __init__(self, available=True):
        self.books = {1: type("Book", (), {"id": 1, "quantity": 2})()}
        if not available:
            self.books[1].quantity = 0
        self.updated = False
    def get(self, id):
        return self.books.get(id)
    def update(self, db_obj, obj_in):
        self.updated = True
        for k, v in obj_in.items():
            setattr(db_obj, k, v)
        return db_obj

class DummyUserRepo:
    def __init__(self, active=True):
        self.users = {1: type("User", (), {"id": 1, "is_active": active})()}
    def get(self, id):
        return self.users.get(id)

def test_create_loan_user_not_found():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo()
    service = LoanService(loan_repo, book_repo, user_repo)
    with pytest.raises(CustomException) as exc:
        service.create_loan(user_id=999, book_id=1)
    assert "Utilisateur avec l'ID 999 non trouvé" in str(exc.value)

def test_create_loan_book_not_found():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    book_repo.books = {}  # Aucun livre
    user_repo = DummyUserRepo()
    service = LoanService(loan_repo, book_repo, user_repo)
    with pytest.raises(CustomException) as exc:
        service.create_loan(user_id=1, book_id=999)
    assert "Livre avec l'ID 999 non trouvé" in str(exc.value)

def test_create_loan_book_not_available():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo(available=False)
    user_repo = DummyUserRepo()
    service = LoanService(loan_repo, book_repo, user_repo)
    with pytest.raises(CustomException) as exc:
        service.create_loan(user_id=1, book_id=1)
    assert "n'est pas disponible" in str(exc.value)

def test_create_loan_user_inactive():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo(active=False)
    service = LoanService(loan_repo, book_repo, user_repo)
    with pytest.raises(CustomException) as exc:
        service.create_loan(user_id=1, book_id=1)
    assert "inactif" in str(exc.value)

def test_create_loan_success():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo()
    service = LoanService(loan_repo, book_repo, user_repo)
    loan = service.create_loan(user_id=1, book_id=1)
    assert loan_repo.created
    assert book_repo.books[1].quantity == 1  # décrémenté
    assert loan.user_id == 1
    assert loan.book_id == 1

def test_return_loan_success():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo()
    # Ajoute un emprunt actif
    loan = type("Loan", (), {
        "id": 10,
        "user_id": 1,
        "book_id": 1,
        "return_date": None,
        "due_date": datetime.utcnow() + timedelta(days=7),
        "loan_date": datetime.utcnow()
    })()
    loan_repo.loans.append(loan)
    loan_repo.get = lambda id: loan if id == 10 else None
    loan_repo.update = lambda db_obj, obj_in: setattr(db_obj, "return_date", obj_in["return_date"]) or db_obj
    service = LoanService(loan_repo, book_repo, user_repo)
    result = service.return_loan(loan_id=10)
    assert result.return_date is not None
    assert book_repo.books[1].quantity == 3  # augmenté

def test_return_loan_already_returned():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo()
    loan = type("Loan", (), {
        "id": 10,
        "user_id": 1,
        "book_id": 1,
        "return_date": datetime.utcnow(),
        "due_date": datetime.utcnow() + timedelta(days=7),
        "loan_date": datetime.utcnow()
    })()
    loan_repo.get = lambda id: loan if id == 10 else None
    service = LoanService(loan_repo, book_repo, user_repo)
    with pytest.raises(CustomException) as exc:
        service.return_loan(loan_id=10)
    assert "déjà été retourné" in str(exc.value)

def test_extend_loan_success():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo()
    loan = type("Loan", (), {
        "id": 10,
        "user_id": 1,
        "book_id": 1,
        "return_date": None,
        "due_date": datetime.utcnow() + timedelta(days=7),
        "loan_date": datetime.utcnow()
    })()
    loan_repo.get = lambda id: loan if id == 10 else None
    loan_repo.update = lambda db_obj, obj_in: setattr(db_obj, "due_date", obj_in["due_date"]) or db_obj
    service = LoanService(loan_repo, book_repo, user_repo)
    new_due = loan.due_date + timedelta(days=7)
    result = service.extend_loan(loan_id=10, extension_days=7)
    assert result.due_date == new_due

def test_extend_loan_already_extended():
    loan_repo = DummyLoanRepo()
    book_repo = DummyBookRepo()
    user_repo = DummyUserRepo()
    loan = type("Loan", (), {
        "id": 10,
        "user_id": 1,
        "book_id": 1,
        "return_date": None,
        "due_date": datetime.utcnow() + timedelta(days=21),
        "loan_date": datetime.utcnow()
    })()
    loan_repo.get = lambda id: loan if id == 10 else None
    service = LoanService(loan_repo, book_repo, user_repo)
    with pytest.raises(CustomException) as exc:
        service.extend_loan(loan_id=10, extension_days=7)
    assert "déjà été prolongé" in str(exc.value)
