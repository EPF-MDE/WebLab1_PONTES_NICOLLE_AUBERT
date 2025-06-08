from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from .base import Base

# Table d'association pour la relation many-to-many entre livres et catégories
book_category = Table(
    "book_category",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True),
)


class Category(Base):
    """
    Modèle SQLAlchemy pour les catégories de livres.
    """
    __tablename__ = "categories"
    name = Column(String(50), nullable=False, unique=True, index=True)
    description = Column(String(200), nullable=True)

    # Relations
    books = relationship(
        "Book",
        secondary=book_category,
        back_populates="categories"
    )