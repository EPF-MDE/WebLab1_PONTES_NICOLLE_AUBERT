import pytest
from sqlalchemy.exc import SQLAlchemyError
from src.exceptions import CustomException

# Dummy SQLAlchemy session and model for testing
class DummySession:
    def __init__(self):
        self.should_fail = False
        self.should_return_none = False
    def query(self, model):
        class Query:
            def __init__(self, parent):
                self.parent = parent
            def filter(self, *args, **kwargs):
                return self
            def first(self):
                if self.parent.should_fail:
                    raise SQLAlchemyError("Erreur DB")
                if self.parent.should_return_none:
                    return None
                return "dummy"
            def offset(self, skip):
                return self
            def limit(self, limit):
                return self
            def all(self):
                if self.parent.should_fail:
                    raise SQLAlchemyError("Erreur DB")
                return ["dummy"]
            def get(self, id):
                if self.parent.should_return_none:
                    return None
                return "dummy"
        return Query(self)
    def add(self, obj):
        if self.should_fail:
            raise SQLAlchemyError("Erreur DB")
    def commit(self):
        if self.should_fail:
            raise SQLAlchemyError("Erreur DB")
    def refresh(self, obj):
        if self.should_fail:
            raise SQLAlchemyError("Erreur DB")
    def delete(self, obj):
        if self.should_fail:
            raise SQLAlchemyError("Erreur DB")

class DummyModel:
    id = 1
    __name__ = "Dummy"

# Importe le repository de base
from src.repositories.base import BaseRepository

def test_update_exception():
    session = DummySession()
    repo = BaseRepository(DummyModel, session)
    # On force l'échec lors du commit
    session.should_fail = True
    with pytest.raises(CustomException) as exc:
        repo.update(db_obj=DummyModel(), obj_in={"id": 1})
    assert "Erreur lors de la mise à jour" in str(exc.value)

def test_remove_not_found():
    session = DummySession()
    repo = BaseRepository(DummyModel, session)
    session.should_return_none = True
    with pytest.raises(CustomException) as exc:
        repo.remove(id=123)
    assert "Erreur lors de la suppression" in str(exc.value)

def test_remove_db_error():
    session = DummySession()
    repo = BaseRepository(DummyModel, session)
    # On force l'échec lors du delete
    session.should_fail = True
    with pytest.raises(CustomException) as exc:
        repo.remove(id=1)
    assert "Erreur lors de la suppression" in str(exc.value)