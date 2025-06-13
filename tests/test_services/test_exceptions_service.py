import pytest
from src.services.users import UserService
from src.services.books import BookService
from src.services.stats import StatsService
from src.exceptions import CustomException

class DummyRepo:
    def get_by_email(self, email):
        return None
    def create(self, obj_in):
        raise Exception("Erreur création")
    def get(self, id):
        return None
    def get_multi(self, skip=0, limit=100):
        raise Exception("Erreur multi")
    def update(self, db_obj, obj_in):
        raise Exception("Erreur update")
    def remove(self, id):
        raise Exception("Erreur remove")

def test_userservice_create_email_exists():
    repo = DummyRepo()
    service = UserService(repo)
    # Simule un utilisateur déjà existant
    service.get_by_email = lambda email: True
    with pytest.raises(CustomException) as exc:
        service.create(obj_in=type("UserCreate", (), {"email": "a@a.com", "password": "1234", "dict": lambda self: {"email": "a@a.com", "password": "1234"}})())
    assert "déjà utilisé" in str(exc.value)

def test_userservice_create_db_error():
    repo = DummyRepo()
    service = UserService(repo)
    service.get_by_email = lambda email: None
    with pytest.raises(CustomException):
        service.create(obj_in=type("UserCreate", (), {"email": "a@a.com", "password": "1234", "dict": lambda self: {"email": "a@a.com", "password": "1234"}})())

def test_userservice_authenticate_not_found():
    repo = DummyRepo()
    service = UserService(repo)
    service.get_by_email = lambda email: None
    with pytest.raises(CustomException) as exc:
        service.authenticate(email="notfound@a.com", password="1234")
    assert "Utilisateur non trouvé" in str(exc.value)

def test_bookservice_create_isbn_exists():
    repo = DummyRepo()
    service = BookService(repo)
    service.get_by_isbn = lambda isbn: True
    with pytest.raises(CustomException) as exc:
        service.create(obj_in=type("BookCreate", (), {"isbn": "123", "dict": lambda self: {"isbn": "123"}})())
    assert "ISBN est déjà utilisé" in str(exc.value)

def test_baseservice_get_multi_exception():
    from src.services.base import BaseService
    repo = DummyRepo()
    service = BaseService(repo)
    with pytest.raises(CustomException):
        service.get_multi()

def test_baseservice_update_exception():
    from src.services.base import BaseService
    repo = DummyRepo()
    service = BaseService(repo)
    with pytest.raises(CustomException):
        service.update(db_obj=None, obj_in={})

def test_baseservice_remove_exception():
    from src.services.base import BaseService
    repo = DummyRepo()
    service = BaseService(repo)
    with pytest.raises(CustomException):
        service.remove(id=1)