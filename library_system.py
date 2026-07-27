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
    # needed import
    select,
    # needed import
    func,
)

# The IntegrityError is important for handling the cases where and email is
# entered twice and need to be unique. We will add that catch of this issue in
# a try except block.
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    Session,
)

# Optional is for when we want a value to be tranlated between python and sql
# as either None or NULL. Optional makes the field/attribute optional though.
from typing import Optional

# datetime for the purpose of time stamping.
# also timedelta is for the purpose of handling and editng the timedelta
from datetime import date, timedelta

# connect to the database with echo set to false.
# to see the raw sql set echo to True.
engine = create_engine("sqlite:///library.db", echo=False)


# This is the super class we will inherit upon other tables
class Base(DeclarativeBase):
    pass


# Create the association/junction table for Book <-> Genre (many-to-many)
# many books have many genres.
book_genres = Table(
    "book_genres",
    # metadata for connecting and context
    Base.metadata,
    # set up Keys for reference
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
    # connects to the books table via relationship. Book.author
    # gives us the list of books by one author when handling the author obj
    # author.books think loop through books to get matchs.
    books: Mapped[list["Book"]] = relationship(back_populates="author")


# Implement the Genre model
# Attributes: id (PK), name (required, unique)
class Genre(Base):
    __tablename__ = "genres"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # looks at a list of books based on the relationship. Refrences the
    # junc.table (multiple rows with same book but different genre number)
    # genres.books looks at Book(books).genres attribute setup on that table to
    # get values
    books: Mapped[list["Book"]] = relationship(
        # pointer to association/junc table
        secondary=book_genres,
        # for the caller when working with other end of relationship.
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
    # the ForeignKey that is pointing at the authors.id integer/primary_key
    # note this is different from the relationship.
    author_id: Mapped[int] = mapped_column(
        Integer,
        # does this need to be authors?
        ForeignKey("authors.id"),
        nullable=False,
    )
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # this is the many to one relationship put into action. This accesses the
    # author via the the author_id that is present in the row which must exist.
    # we can access an authors books via book.author.books because of the books
    # that is setup on the author class which points here and queries the db
    # to get all books that match the author_id.
    author: Mapped["Author"] = relationship(back_populates="books")
    # genres points back to the association/junction talbe pointing at the
    # Colum we defined
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
            # Have to use the scalar to query for existing.(Not a simple .get())
            genre = session.scalar(select(Genre).where(Genre.name == genre_name))
            # Create the Genre if it does not already exist.
            if genre is None:
                # Create the Genre obj in the genres table
                genre = Genre(name=genre_name)
            # Add the Genre object to the Book's relationship collection(list).
            book.genres.append(genre)
        # Now that we know author exist and the genres have been added we add
        # to the books table
        session.add(book)
        # commit the changes to the database
        session.commit()
        # return the book
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
            # capture current date and add days to it.
            due_date = date.today() + days
            # set available to False on the book row being accessed
            book.available = False
            # add the Checkout
            session.add(
                Checkout, book_id=book_id, borrower_id=borrower_id, due_date=due_date
            )
        else:
            # if the book isn't available we can't let a checkout. Could use
            # a try here with a print stmt for caliry in the CLI
            raise ValueError
        # commit the changes to the db
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
        stmt = (
            # select the Book table
            select(Book)
            # joins the Book to the author
            .join(Book.author)
            # search for where the Author table has the name field/att that
            # matches the author name argument that is passed to the function.
            # We use .ilike for the insensitive casing.
            .where(
                Author.name.ilike(f"%{author_name}%"),
            )
        )
        # What are scalers again? It is like the execute query to obtain all
        # matches. Hence the reason we call .all() becuase there can be
        # multiple objects
        books = session.scalars(stmt).all()
        return books


def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # implement
    with Session(engine) as session:
        # here we need the overdue books. What table could hold this
        # information. Checkout holds the fields that we can use to find books
        # that haven't been returned in time. We could also use the books with
        # the days and expected day back maybe?
        stmt = select(Checkout).where(
            # we can simply check against todays date
            Checkout.due_date < date.today(),
            # This is another condition implemented for the purpose of checking
            # if the attribute return_date is None. Would be used in the
            # instance where one need to be set?
            Checkout.return_date.is_(None),
        )
        # using scalers here is that execution through a table or tables to
        # retrieve all of the relative objs or rows hence .all()
        overdue_books = session.scalars(stmt).all()
        return overdue_books


def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # implement — needs a join through Book to Checkout
    # Assign the Session Class we use for working with the engine as session
    with Session(engine) as session:
        # ins't there a sqlalchemy count we can use instead?
        # this is used to obtain a count for books that have matching genres
        # applied. Also used for ordering purposes based on quantity.
        checkout_count = func.count(Checkout.id)
        # stmt to query.
        stmt = (
            select(Genre)
            .join(Genre.books)
            # why do we use 2x joins here? This is because we want to see a
            # query result that is from the combined tables right? So we want
            # to see the Genres that pattern match in correlation with the book
            # by the checkouts though.
            .join(Book.checkouts)
            # we use the gourp_by since we have the 2x joins right. Working out
            # of 2 tables vs. 1 where we could have just used a where.
            # we group by the id and the name of the Genre so that we have the
            # correct patterns.
            .group_by(Genre.id, Genre.name)
            # Order by
            .order_by(checkout_count.desc())
            .limit(limit=limit),
        )
        popular_genres = session.scalars(stmt).all()
        return popular_genres


def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # implement
    with Session(engine) as session:
        stmt = select(Book).where(Book.available.is_(True))

        books = session.scalars(stmt).all()
        return books
