import logging
from sqlalchemy import Column, Integer, ForeignKey, DateTime, CheckConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

logger = logging.getLogger(__name__)

class Loan(Base):
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("book.id"), nullable=False)
    loan_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    return_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=False)
    extended = Column(Boolean, default=False, nullable=False)
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('due_date > loan_date', name='check_due_date_after_loan_date'),
        CheckConstraint('return_date IS NULL OR return_date >= loan_date', name='check_return_date_after_loan_date'),
        # Index pour les recherches fréquentes
        Index('idx_loan_user_id', 'user_id'),
        Index('idx_loan_book_id', 'book_id'),
        Index('idx_loan_return_date', 'return_date'),
    )
    
    # Relations
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")

    def __init__(self, user_id, book_id, due_date, loan_date=None, return_date=None, extended=False):
        logger.debug(f"Creating Loan: user_id={user_id}, book_id={book_id}, due_date={due_date}, loan_date={loan_date}, return_date={return_date}, extended={extended}")
        self.user_id = user_id
        self.book_id = book_id
        self.due_date = due_date
        self.loan_date = loan_date or datetime.utcnow()
        self.return_date = return_date
        self.extended = extended

    def extend_loan(self, new_due_date):
        logger.info(f"Extending loan {self} to new due date: {new_due_date}")
        self.due_date = new_due_date
        self.extended = True

    def mark_returned(self, return_date=None):
        logger.info(f"Marking loan {self} as returned on {return_date or datetime.utcnow()}")
        self.return_date = return_date or datetime.utcnow()