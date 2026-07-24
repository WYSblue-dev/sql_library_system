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
# themselves. That is why metadata is so important. If gives this table
# reference to all of our tables to work correctly.
book_genres = Table(
    "book_genres",
    Base.metadata,
    # Column of our book_genres table that points to a Book id for as many used
    # a Book will get a genre and can have multiple. Multiple books can have
    # the same genres.
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    # This is a Column of this association table to access the type of genre
    # that is to be associated with the corresponding books.
    Column("genre_id", Integer, ForeignKey("genres.id"), primary_key=True),
)


# Implement the Author model
# Attributes: id (PK), name (required), bio (optional)
class Author(Base):
    __tablename__ = "authors"
    # define columns
    # primary key of the table authors one to many. 1 author to many books?
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    # made optional and that lets us have a None value in the db
    bio: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # one to many realationship established to the books(list) table Book with the
    # realationship function. back_populates points to the author.
    books: Mapped[list["Book"]] = relationship(back_populates="author")


# Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # books is an genres attribute/field we are creating on this table.
    # It can be a list of Book table objs.
    # We set a relationship to access the book_genres(many to many) table.
    # We can then access the values via a query like genre.books to see how
    # many books a specific genre has or we can look at a book.genres to see
    # how many genres it has.
    books: Mapped[list["Book"]] = relationship(
        # points to the association table to be able to access a book.genres
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
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(
        # author_id on a book is a pointer to the id of the author of the book
        # so we create the relationship with the ForeignKey accessing the athour.id
        Integer,
        ForeignKey("author.id"),
        nullable=False,
    )
    # default is set so that we assume a book is in stock when we add a book
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # many to one(author can have many books.)(many books can have one author)
    # so we'll need the relationship here
    # When a book is used to access the author book.author is like a query.
    # Points to the attribute of the Author model with the author_id attrbute
    # we have set on the Book table. To access the authors rows and info.
    author: Mapped["Author"] = relationship(back_populates="books")
    # many to many(many generes will apply to many books)
    # so we'll need the relationship here.(This also has the book_generes table)
    genres: Mapped[str] = relationship(secondary="books_genres", back_populates="books")

    # the checkout wasn't defined in the example setup but this is where it
    # should take place?
    # One Book many historical Checkout records
    checkouts: Mapped[list["Checkout"]] = relationship(back_populates="book")


# Implement the Borrower model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Borrower(Base):
    __tablename__ = "borrowers"
    # define columns
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # phone numbers are strings but why again?
    phone: Mapped[Optional[str]] = mapped_column(String)
    # this is a borrower who checks out multiples(Checkouts) one to many
    checkouts: Mapped[list["Checkout"]] = relationship(back_populates="borrower")


# Implement the Checkout model
# Attributes: id (PK), book_id (FK), borrower_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, borrower
class Checkout(Base):
    __tablename__ = "checkouts"
    # define columns and relationships
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # this is the book_id that will apply to what book obj it is in the db
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id"), nullable=False
    )
    borrower_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("borrower.id"), nullable=False
    )
    # The date when the book was checked out.
    checkout_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    # can be checked out then not returned so it can be left blank.
    return_date: Mapped[Optional[date]] = mapped_column(Date)

    # now we want to establish the many checkout records to the one book(history)
    book: Mapped["Book"] = relationship(back_populates="checkouts")
    # Many checkout records to one borrower
    borrower: Mapped["Borrower"] = relationship(back_populates="checkouts")


def init_db():
    """Create all database tables. Call this before using any other functions."""
    # we use create_all to set up the database by connecting and setting the tables
    Base.metadata.create_all(engine)
    # do we need pass here(can be a infinite loop if not? I wouldn't think
    # that to be the case as the create_all terminates surely)


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================


# I think that I need to set up a session var that accesses the Session obj
def add_author(name: str, bio: str = None):
    """Add a new author. Returns the created Author object."""
    Session.add(Author(name, bio))
    # open Session, create Author, add + commit, return it
    Session.commit()


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
    Session.add(Book(title, isbn, author_id, published_year, genre_names))
    Session.commit()


def add_borrower(name: str, email: str, phone: str = None):
    """Register a new borrower. Returns the created Borrower object."""
    # implement
    Session.add(Borrower(name, email, phone))
    Session.commit()


def checkout_book(book_id: int, borrower_id: int, days: int = 14):
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    # implement
    # use the datetime.now to access the current day and date.
    # I think I should be using a .get here change the valuse of the obj and
    # then commiting the changes. The next thing to say here is that is seems
    # there is redudent code that will be repetted and that is the connection
    # to a specific database. That will be where we call .connection and assign
    # that to the var session
    session = Session.connection("sqlite:///library.db")
    session.
    session.commit()


def return_book(checkout_id: int):
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # implement
    # Is this where we use scaler/scalers? I need to go back and reference.
    Session.get(checkout_id)

    


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
