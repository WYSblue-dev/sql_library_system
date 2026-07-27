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


# Authors and books associantion table.
# the purpose of this table is to be able to set many books with many authors
book_authors = Table(
    "book_authors",
    Base.metadata,
    # removed the Foreign key on book to author becasue they reside here
    # with pointers back to here.
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
)

# books ↔ members (borrowings): Track which member borrowed which book, with
# checkout_date and return_date (NULL if not returned yet). This can be
# implemented as an association table with extra columns, or as its own model
# with foreign keys to both books and members.

# it would seem like to me that I need to migrate the functionality of the
# borrowers in a sense to the membership instance. Also track the book borrowed
# by the member with the either A Borrower table or B a own model with
# foreignkeys

# what that sounds like to be a member can have many books checked out. So I
# need to be able to take the time to add in that specifically.

# checkout_date, and return_date are the most important.


class Members(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String, unique=True)
    membership_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=date.today(),
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
    books: Mapped[list["Book"]] = relationship(
        secondary=book_authors,
        back_populates="authors",
    )


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


# a member can check out many books one to many
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)

    # Borrower can check out many books. One book one chekcout.

    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # this is the many to one relationship put into action. This accesses the
    # author via the the author_id that is present in the row which must exist.
    # we can access an authors books via book.author.books because of the books
    # that is setup on the author class which points here and queries the db
    # to get all books that match the author_id.
    authors: Mapped[list["Author"]] = relationship(
        secondary=book_authors,
        back_populates="books",
    )
    # genres points back to the association/junction talbe pointing at the
    # Colum we defined
    genres: Mapped[list["Genre"]] = relationship(
        secondary=book_genres,
        back_populates="books",
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
        author = Author(name=name, bio=bio)
        session.add(author)
        session.commit()
        session.refresh(author)
        return author


def add_book(
    title: str,
    isbn: str,
    author_ids: list[int],
    published_year: int = None,
    genre_names: list = None,
):
    """
    Add a new book. Assigns genres by name (creates genre if it doesn't exist yet).
    Returns the created Book object.
    """
    title = title.strip()
    isbn = isbn.strip()

    if not title:
        raise ValueError("A book title is required.")

    if not isbn:
        raise ValueError("An ISBN is required.")

    if not author_ids:
        raise ValueError("A book must have at least one author.")

    # Remove duplicate author IDs while preserving their input order.
    unique_author_ids = list(dict.fromkeys(author_ids))

    with Session(engine) as session:
        # Check for an existing book before attempting the insert.
        existing_book = session.scalar(select(Book).where(Book.isbn == isbn))

        if existing_book is not None:
            raise ValueError(f"A book with ISBN {isbn} already exists.")

        authors = []

        for author_id in unique_author_ids:
            author = session.get(Author, author_id)
            if author is None:
                raise ValueError(f"No author found with ID {author_id}.")
            authors.append(author)
        # Create the Book object first.
        book = Book(
            title=title,
            isbn=isbn,
            published_year=published_year,
        )

        # Populate the Book.authors relationship collection.
        # this is new because we have the many to many relationship now.
        book.authors.extend(authors)

        # remove duplicates
        genre_names = set(genre_names)

        # genre_names could be None, so use an empty list in that case.
        for genre_name in genre_names or []:
            update_genre_name = genre_name.strip().lower()
            # now looks with strip and lower
            genre = session.scalar(select(Genre).where(Genre.name == update_genre_name))
            # Create the Genre if it does not already exist.
            if genre is None:
                # Create the Genre obj in the genres table if doesn't exist
                genre = Genre(name=genre_name)
            # Add the Genre object to the Book's relationship collection(list).
            book.genres.append(genre)
        # Now that we know author exist and the genres have been added we add
        # to the books tabled
        session.add(book)
        # commit the changes to the database
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError(
                "The book could not be added due to a violation" "of constraints"
            ) from error
        session.refresh(book)
        # return the book
        return book


def add_borrower(
    name: str,
    email: str,
    phone: str | None = None,
) -> Borrower:
    """Register a new borrower and return the created Borrower object."""

    with Session(engine) as session:
        borrower = Borrower(
            name=name,
            email=email,
            phone=phone,
        )

        session.add(borrower)

        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError("A borrower with that email may already exist.") from error

        # refresh so that
        session.refresh(borrower)
        return borrower


def checkout_book(book_id: int, borrower_id: int, days: int = 14):
    """
    Check out a book. Sets book.available = False. due_date = today + days.
    Raises ValueError if the book is not available.
    Returns the created Checkout object.
    """
    if days <= 0:
        raise ValueError("Checkout days must be greater than 0")
    with Session(engine) as session:
        book = session.get(Book, book_id)

        # see if book exist.
        if book is None:
            raise ValueError(f"Book ID {book_id} does not exist.")

        # see if book available
        if not book.available:
            raise ValueError(f'"{book.title}" is not currently available.')

        # see if borrower exist
        borrower = session.get(Borrower, borrower_id)

        # statement as to not borrower exisiting
        if borrower is None:
            raise ValueError(f"Borrower ID {borrower_id} does not exist.")

        # combine the days date with the timedelta
        due_date = date.today() + timedelta(days=days)

        # create the Checkout databasse obj/row with the information that is now
        # valid
        new_checkout = Checkout(
            book_id=book.id,
            borrower_id=borrower.id,
            due_date=due_date,
        )
        # set the book obj that we know exist to avaiable to false
        book.available = False
        # now add the checkout to that database
        session.add(new_checkout)
        # save with rollback protection
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError(
                "The checkout could not be saved because it "
                "violated a database constraint."
            ) from error
        # refresh so the obj is up to date in the session
        session.refresh(new_checkout)
        return new_checkout


def return_book(checkout_id: int):
    """
    Return a book. Sets book.available = True, sets return_date = today.
    Returns the updated Checkout object.
    """
    # implement
    with Session(engine) as session:
        while True:
            try:
                checkout = session.get(Checkout, checkout_id)
                break
            except ValueError:
                print("The value entered must be a int not a string.")
            except IntegrityError:
                print("The int entered doesn't exist.")

        checkout.return_date = date.today()
        # modify the book available attribute/field
        checkout.book.available = True
        session.commit()
        session.refresh(checkout)
        return checkout


# ============================================================
# QUERY FUNCTIONS
# ============================================================


def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # implement — use LIKE or ilike for partial matching
    with Session(engine) as session:
        stmt = (
            # might be able to do this differently now since there is a means
            # to be able to looks at multiple authors on one book. So may find
            # a book that has one author. Maybe we could perform pattern
            # matching here.
            # select the Book table
            select(Book)
            # joins the Book to the authors table privided the relationship
            # is set up correctly.
            .join(Book.author)
            # search for where the Author table has the name field/att that
            # matches the author name argument that is passed to the function.
            # We use .ilike for the insensitive casing.
            .where(
                # percentage gives partial pattern matching.
                Author.name.ilike(f"%{author_name}%"),
            )
        )
        # Scalars are what we grab from the ORM Book, Genre etc...
        # Hence the reason we call .all() becuase we want to collect them in
        # the list
        books = session.scalars(stmt).all()
        # return the list of the books
        return books


def get_author_by_name(name: str) -> Author | None:
    with Session(engine) as session:
        stmt = func.lower(Author.name) == name.strip().lower()
        return session.scalar(stmt)


def get_overdue_books() -> list:
    """Return all Checkout objects where due_date < today and return_date is None."""
    # implement
    with Session(engine) as session:
        # here we need the overdue books. What table could hold this
        # information. Checkout holds the fields that we can use to find books
        # that haven't been returned in time. We could also use the books with
        # the days and expected day back maybe? No just check back in the
        # due_date vs. the dates day.
        stmt = select(Checkout).where(
            # we can simply check against todays date
            Checkout.due_date < date.today(),
            # This is another condition implemented for the purpose of checking
            # if the attribute return_date is None. Would be used in the
            # instance where the return_date hasn't been established.(still
            # not returned/still active)
            Checkout.return_date.is_(None),
        )
        # using scalers here is that execution through a table or tables to
        # retrieve all of the relative objs or rows hence .all() to get list
        overdue_checkouts = session.scalars(stmt).all()
        return overdue_checkouts


def get_popular_genres(limit: int = 3) -> list:
    """Return the top `limit` genres by checkout count."""
    # implement — needs a join through Book to Checkout
    # Assign the Session Class we use for working with the engine as session
    with Session(engine) as session:
        # this func we needed to import in the top of the file from sqlalchemy.
        # This is the equivlent to sqlalchemy.
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
            # group because COUNT() must calculate a separate checkout count
            # for each genre.
            .group_by(Genre.id, Genre.name)
            # Order by
            .order_by(checkout_count.desc())
            .limit(limit)
        )
        popular_genres = session.scalars(stmt).all()
        return popular_genres


def get_available_books() -> list:
    """Return all Book objects where available == True."""
    # implement
    with Session(engine) as session:
        # retrieve Book table books where the books att/field available
        # is True.
        stmt = select(Book).where(Book.available.is_(True))
        books = session.scalars(stmt).all()
        return books
