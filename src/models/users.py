import logging
from sqlalchemy import Column, String, Boolean, CheckConstraint
from sqlalchemy.orm import relationship

from .base import Base

logger = logging.getLogger(__name__)

class User(Base):
    email = Column(String(100), nullable=False, unique=True, index=True)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    phone = Column(String(20), nullable=True)
    address = Column(String(200), nullable=True)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint("email LIKE '%@%.%'", name="check_email_format"),
    )
    
    # Relations
    loans = relationship("Loan", back_populates="user", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        logger.debug(f"Creating User with: {kwargs}")
        super().__init__(**kwargs)

    def __repr__(self):
        logger.debug(f"User __repr__ called for: {self.email}")
        return f"<User(email={self.email}, full_name={self.full_name})>"