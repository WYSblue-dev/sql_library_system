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
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional
from datetime import date

engine = create_engine("sqlite:///library.db", echo=False)


# This is the super class we will inherit upon other tables
class Base(DeclarativeBase):
    pass


# Create the association/junction table for Book <-> Genre (many-to-many)
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # made optional and that lets us have a None value in the db
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    books: Mapped[list["Book"]] = relationship(back_populates="author")


# Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    books: Mapped[list["Book"]] = relationship(
        secondary=book_genres,
        back_populates="genres",
    )


# Implement the Book model
# Attributes: id (PK), title (required), isbn (unique, required),
#             published_year (optional), author_id (FK), available (bool, default True)
# Relationships: author (many-to-one), genres (many-to-many via book_genres)
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(
        Integer,
        # does this need to be authors?
        ForeignKey("authors.id"),
        nullable=False,
    )
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    author: Mapped["Author"] = relationship(back_populates="books")
    genres: Mapped[list["Genre"]] = relationship(
        secondary="book_genres", back_populates="books"
    )
    checkouts: Mapped[list["Checkout"]] = relationship(back_populates="book")


# Implement the Borrower model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Borrower(Base):
    __tablename__ = "borrowers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String)
    checkouts: Mapped[list["Checkout"]] = relationship(back_populates="borrower")


# Implement the Checkout model
# Attributes: id (PK), book_id (FK), borrower_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, borrower
class Checkout(Base):
    __tablename__ = "checkouts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id"), nullable=False
    )
    borrower_id: Mapped[int] = mapped_column(
        Integer,
        # does this need to be borrowers?
        ForeignKey("borrowers.id"),
        nullable=False,
    )
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Optional[date]] = mapped_column(Date)
    book: Mapped["Book"] = relationship(back_populates="checkouts")
    borrower: Mapped["Borrower"] = relationship(back_populates="checkouts")


def init_db():
    """Create all database tables. Call this before using any other functions."""
    Base.metadata.create_all(engine)


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================


def add_author(name: str, bio: str = None):
    """Add a new author. Returns the created Author object."""
    with Session(engine) as session:
        session.add(Author(name=name, bio=bio))
        session.commit()


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
    with Session(engine) as session:
        # Confirm that the supplied author exists.
        author = session.get(Author, author_id)
        if author is None:
            raise ValueError(f"No author found with ID {author_id}")
        # Create the Book object first.
        book = Book(
            title=title,
            isbn=isbn,
            author_id=author_id,
            published_year=published_year,
        )
        # genre_names could be None, so use an empty list in that case.
        for genre_name in genre_names or []:
            # Look for an existing Genre with this name.
            genre = session.scalar(select(Genre).where(Genre.name == genre_name))
            # Create the Genre if it does not already exist.
            if genre is None:
                genre = Genre(name=genre_name)
            # Add the Genre object to the Book's relationship collection.
            book.genres.append(genre)
        session.add(book)
        session.commit()
        return book


def add_borrower(name: str, email: str, phone: str = None):
    """Register a new borrower. Returns the created Borrower object."""
    # implement
    with Session(engine) as session:
        session.add(Borrower(name=name, email=email, phone=phone))
        session.commit()


def checkout_book(book_id: int, borrower_id: int, days: int = 14):
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    # implement
    with Session(engine) as session:
        book = session.get(Book, book_id)
        if book.available:
            due_date = date.today() + days
            book.available = False
            session.add(
                Checkout, book_id=book_id, borrower_id=borrower_id, due_date=due_date
            )
        else:
            raise ValueError
        session.commit()


def return_book(checkout_id: int):
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # implement
    with Session(engine) as session:
        checkout = session.get(Checkout, checkout_id)
        checkout.return_date = date.today()
        checkout.book.available = True
        session.commit()


# ============================================================
# QUERY FUNCTIONS
# ============================================================


def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # implement — use LIKE or ilike for partial matching
    with Session(engine) as session:
        stmt = select()
        things = session.scalars(stmt)
        for loop in things:
            print()
        print()


def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # implement
    with Session(engine) as session:
        stmt = select()
        things = session.scalars(stmt)
        for loop in things:
            print()
        print()


def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # implement — needs a join through Book to Checkout
    with Session(engine) as session:
        stmt = select()
        things = session.scalars(stmt)
        for loop in things:
            print()
        print()


def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # implement
    with Session(engine) as session:
        stmt = select()
        things = session.scalars(stmt)
        for loop in things:
            print()
        print()
