import pytest
from src.repositories.users import UserRepository
from src.models.users import User

def test_create_user(db_session):
    repo = UserRepository(User, db_session)
    user_data = {
        "email": "createuser@example.com",
        "full_name": "Create User",
        "hashed_password": "hashed",
        "is_active": True
    }
    user = repo.create(obj_in=user_data)
    assert user.id is not None
    assert user.email == "createuser@example.com"
    assert user.full_name == "Create User"
    assert user.is_active is True

def test_get_by_email(db_session):
    repo = UserRepository(User, db_session)
    user = User(
        email="findme@example.com",
        full_name="Find Me",
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    found = repo.get_by_email(email="findme@example.com")
    assert found is not None
    assert found.email == "findme@example.com"

def test_update_user(db_session):
    repo = UserRepository(User, db_session)
    user = User(
        email="updateuser@example.com",
        full_name="Update User",
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    update_data = {"full_name": "Updated Name"}
    updated = repo.update(db_obj=user, obj_in=update_data)
    assert updated.full_name == "Updated Name"

def test_remove_user(db_session):
    repo = UserRepository(User, db_session)
    user = User(
        email="deleteuser@example.com",
        full_name="Delete User",
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    repo.remove(id=user.id)
    assert repo.get(user.id) is None