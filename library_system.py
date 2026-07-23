"""
Module 3 Project: Library Management System
library_system.py — Database models and query functions

Your job: Implement the SQLAlchemy models and all functions marked with # TODO.
"""

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Boolean,
    ForeignKey,
    Table,
    Column,
    Date,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional
from datetime import date

engine = create_engine("sqlite:///library.db", echo=False)


# This is the super class we will inherit upon other tables
class Base(DeclarativeBase):
    pass


# Create the association/junction table for Book <-> Genre (many-to-many)
# we have to specify the name of the table to reference in the tables
# themselves
book_genres = Table(
    "book_genres",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


# Implement the Author model
# Attributes: id (PK), name (required), bio (optional)
class Author(Base):
    __tablename__ = "authors"
    # define columns
    # primary key of the table authors one to many. 1 author to many books?
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # made optional
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # one to many realationship established to the books(list) table Book with the
    # realationship function. back_populates points to the author.
    books: Mapped[list["Book"]] = relationship(back_populates="author")


# Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # I need to take the time to think about generes. I think this would be a
    # author who can have multiple generes(or just on the book itself. this is
    # a design descision.)
    books: Mapped[list["Book"]] = relationship(
        secondary=book_genres, back_populates="genres"
    )


# Implement the Book model
# Attributes: id (PK), title (required), isbn (unique, required),
#             published_year (optional), author_id (FK), available (bool, default True)
# Relationships: author (many-to-one), genres (many-to-many via book_genres)
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    # is this a str or an int. I will assum a str for now.
    isbn: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # by being optional do we mean in the sense of typing as Optional or
    # are we talking about not required? Also is this a datetime datetime moment?.......................
    published_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    author_id: Mapped[int] = mapped_column(
        # author_id on a book is a pointer to the id of the author of the book
        # so we create the relationship with the ForeignKey accessing the athour.id
        Integer,
        ForeignKey("author.id"),
        nullable=False,
    )
    available: Mapped[bool] = mapped_column(Boolean)
    # many to one(author can have many books.)(many books can have one author)
    # so we'll need the relationship here
    author: Mapped[str] = mapped_column(String)
    # many to many(many generes will apply to many books)
    # so we'll need the relationship here.(This also has the book_generes table)
    genres: Mapped[str] = mapped_column(String)


# Implement the Borrower model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Borrower(Base):
    __tablename__ = "borrowers"
    # define columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone: Mapped[int] = mapped_column(Integer, nullable=True)


# Implement the Checkout model
# Attributes: id (PK), book_id (FK), borrower_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, borrower
class Checkout(Base):
    __tablename__ = "checkouts"
    # define columns and relationships
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey, unique=True, nullable=False
    )
    borrower_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)


def init_db():
    """Create all database tables. Call this before using any other functions."""
    # we use create_all to set up the database by connecting and setting the tables
    Base.metadata.create_all(engine)
    # do we need pass here(can be a infinite loop if not? I wouldn't think
    # that to be the case as the create_all terminates surely)
    pass


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================


def add_author(name: str, bio: str = None):
    """Add a new author. Returns the created Author object."""
    # open Session, create Author, add + commit, return it
    pass


def add_book(
    title: str,
    isbn: str,
    author_id: int,
    published_year: int = None,
    genre_names: list = None,
):
    """
    Add a new book. Assigns genres by name (creates genre if it doesn't exist yet).
    Returns the created Book object.
    """
    # implement
    pass


def add_borrower(name: str, email: str, phone: str = None):
    """Register a new borrower. Returns the created Borrower object."""
    # implement
    pass


def checkout_book(book_id: int, borrower_id: int, days: int = 14):
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    # implement
    pass


def return_book(checkout_id: int):
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # implement
    pass


# ============================================================
# QUERY FUNCTIONS
# ============================================================


def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # implement — use LIKE or ilike for partial matching
    pass


def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # implement
    pass


def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # implement — needs a join through Book to Checkout
    pass


def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # implement
    pass
