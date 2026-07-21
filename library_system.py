"""
Module 3 Project: Library Management System
library_system.py — Database models and query functions

Your job: Implement the SQLAlchemy models and all functions marked with # TODO.
"""

from sqlalchemy import create_engine, String, Integer, Boolean, ForeignKey, Table, Column, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import date

engine = create_engine("sqlite:///library.db", echo=False)

class Base(DeclarativeBase):
    pass

# TODO: Create the association table for Book <-> Genre (many-to-many)
book_genres = Table(
    "book_genres",
    Base.metadata,
    Column("book_id",  Integer, ForeignKey("books.id"),  primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)

# TODO: Implement the Author model
# Attributes: id (PK), name (required), bio (optional)
class Author(Base):
    __tablename__ = "authors"
    # TODO: define columns
    # primary key of the table authors
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    bio: Mapped[str] = mapped_column(String, nullable=True)
# TODO: Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    # TODO: define columns
    pass

# TODO: Implement the Book model
# Attributes: id (PK), title (required), isbn (unique, required),
#             published_year (optional), author_id (FK), available (bool, default True)
# Relationships: author (many-to-one), genres (many-to-many via book_genres)
class Book(Base):
    __tablename__ = "books"
    # TODO: define columns and relationships
    pass

# TODO: Implement the Borrower model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Borrower(Base):
    __tablename__ = "borrowers"
    # TODO: define columns
    pass

# TODO: Implement the Checkout model
# Attributes: id (PK), book_id (FK), borrower_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, borrower
class Checkout(Base):
    __tablename__ = "checkouts"
    # TODO: define columns and relationships
    pass


def init_db():
    """Create all database tables. Call this before using any other functions."""
    # TODO: Base.metadata.create_all(engine)
    pass


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================

def add_author(name: str, bio: str = None):
    """Add a new author. Returns the created Author object."""
    # TODO: open Session, create Author, add + commit, return it
    pass

def add_book(title: str, isbn: str, author_id: int,
             published_year: int = None, genre_names: list = None):
    """
    Add a new book. Assigns genres by name (creates genre if it doesn't exist yet).
    Returns the created Book object.
    """
    # TODO: implement
    pass

def add_borrower(name: str, email: str, phone: str = None):
    """Register a new borrower. Returns the created Borrower object."""
    # TODO: implement
    pass

def checkout_book(book_id: int, borrower_id: int, days: int = 14):
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    # TODO: implement
    pass

def return_book(checkout_id: int):
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # TODO: implement
    pass


# ============================================================
# QUERY FUNCTIONS
# ============================================================

def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # TODO: implement — use LIKE or ilike for partial matching
    pass

def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # TODO: implement
    pass

def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # TODO: implement — needs a join through Book to Checkout
    pass

def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # TODO: implement
    pass
