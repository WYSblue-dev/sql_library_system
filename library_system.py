"""
Module 3 Project: Library Management System
library_system.py — Database models and query functions

Your job: Implement the SQLAlchemy models and all functions marked with # TODO.
"""

from sqlalchemy import (
    create_engine,
    String,
    Integer,
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
#             year_published (optional), author_id (FK), available_copies (int, nullable=False)
# Relationships: author (many-to-one), genres (many-to-many via book_genres)


# a member can check out many books one to many
class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    year_published: Mapped[int] = mapped_column(Integer, nullable=False)

    # Member can check out many books. One book one chekcout.

    available_copies: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
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


# Implement the Member model
# Attributes: id (PK), name (required), email (unique, required), phone (optional)
class Member(Base):
    __tablename__ = "members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String)
    # member can have many checkouts need to look at the relationship to under
    # -stand where this value comes from. Would work in conjuction with the
    # checkout/borrowing. I opt to like the use of checkouts and not muddy
    # the concept of the lookup by using borrowings but we can make it work.
    checkouts: Mapped[list["Checkout"]] = relationship(back_populates="member")
    membership_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )


# Implement the Checkout model
# Attributes: id (PK), book_id (FK), member_id (FK),
#             checkout_date (date), due_date (date), return_date (date, nullable)
# Relationships: book, member

# checkout would be an id that is attatched to a book and sets the bool on the Book


class Checkout(Base):
    __tablename__ = "checkouts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("books.id"), nullable=False
    )
    member_id: Mapped[int] = mapped_column(
        Integer,
        # does this need to be members?
        ForeignKey("members.id"),
        nullable=False,
    )
    checkout_date: Mapped[date] = mapped_column(
        Date,
        default=date.today,
        nullable=False,
    )
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[Optional[date]] = mapped_column(Date)
    book: Mapped["Book"] = relationship(back_populates="checkouts")
    # this is the list of chekcouts that will be updated for one member based
    # on the books that they have checked out. Books that are checked are
    # assumed to only have one. This is due to the potential of only one book.
    member: Mapped["Member"] = relationship(back_populates="checkouts")
    # need to add a means to decremeant the books available_copies


def init_db():
    """Create all database tables. Call this before using any other functions."""
    Base.metadata.create_all(engine)


# ============================================================
# CRUD FUNCTIONS — implement each one
# ============================================================


def add_author(
    name: str,
    # this pipe with None = None is what is setup to be able to protect the
    # db in a sense. Bio is typed as a str if a value is entered otherwise
    # default to None
    bio: str | None = None,
):
    """Add a new author. Returns the created Author object."""
    name = name.strip()
    # if there is a value present setup correctly.
    bio = bio.strip() if bio else None

    with Session(engine) as session:
        # we need to check if the author already exist.
        stmt = select(Author)
        authors = session.scalars(stmt).all()
        for author in authors:
            if author.name == name:
                raise ValueError("This name is already taken. Try again.")
        else:
            new_author = Author(name=name, bio=bio)
            # add the new author
            session.add(new_author)
            # save the changes
            session.commit()
            session.refresh(new_author)
            # return new author
            return new_author


def add_book(
    title: str,
    isbn: str,
    author_ids: list[int],
    copies_count: int,
    year_published: int,
    # default value of 1. Why enter books not had?(Could design decision)
    available_copies: int = 1,
    genre_names: list[str] | None = None,
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

    if year_published <= 0:
        raise ValueError("Year published must be greater than 0.")

    if available_copies < 0:
        raise ValueError("Available copies cannot be negative.")

    # Remove duplicate IDs while preserving their order.
    unique_author_ids = list(dict.fromkeys(author_ids))
    # Normalize first, then remove duplicates.
    cleaned_genre_names = {
        genre_name.strip().lower()
        for genre_name in (genre_names or [])
        if genre_name.strip()
    }

    with Session(engine) as session:
        existing_book = session.scalar(select(Book).where(Book.isbn == isbn))
        if existing_book is not None:
            raise ValueError(f"A book with ISBN {isbn} already exists.")

        authors = []

        for author_id in unique_author_ids:
            author = session.get(Author, author_id)
            if author is None:
                raise ValueError(f"No author found with ID {author_id}.")
            authors.append(author)

        book = Book(
            title=title,
            isbn=isbn,
            year_published=year_published,
            available_copies=copies_count,
        )
        # Attach the book before further queries can trigger autoflush.
        session.add(book)
        # SQLAlchemy creates the book_authors junction rows.
        book.authors.extend(authors)

        for genre_name in cleaned_genre_names:
            genre = session.scalar(select(Genre).where(Genre.name == genre_name))
            if genre is None:
                genre = Genre(name=genre_name)
            book.genres.append(genre)

        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError(
                "The book could not be added because it "
                "violated a database constraint."
            ) from error

        session.refresh(book)
        return book


def add_member(
    name: str,
    email: str,
    phone: str | None = None,
) -> Member:
    """Register a new member and return the created Member object."""
    name = name.strip()
    email = email.strip().lower()
    # set phone to None if no value
    phone = phone.strip() if phone else None

    if not name:
        raise ValueError("A member name is required")

    if not email:
        raise ValueError("A email is required")

    with Session(engine) as session:
        member = Member(
            name=name,
            email=email,
            phone=phone,
        )

        session.add(member)

        try:
            session.commit()
        # handle if a unique value already exists
        except IntegrityError as error:
            session.rollback()
            raise ValueError("A member with that email may already exist.") from error

        # refresh so that
        session.refresh(member)
        return member


def checkout_book(book_id: int, member_id: int, days: int = 14):
    """
    Check out a book. Sets book.available_copies = int. due_date = today + days.
    Raises ValueError if the book is not available_copies.
    Returns the created Checkout object.
    """
    if days <= 0:
        raise ValueError("Checkout days must be greater than 0")
    with Session(engine) as session:
        book = session.get(Book, book_id)

        # see if book exist.
        if book is None:
            raise ValueError(f"Book ID {book_id} does not exist.")

        # see if book available_copies
        if not book.available_copies:
            raise ValueError(f'"{book.title}" is not currently available.')

        # see if member exist
        member = session.get(Member, member_id)

        # statement as to not member exisiting
        if member is None:
            raise ValueError(f"Member ID {member_id} does not exist.")

        # combine the days date with the timedelta
        due_date = date.today() + timedelta(days=days)

        # create the Checkout databasse obj/row with the information that is now
        # valid
        new_checkout = Checkout(
            book_id=book.id,
            member_id=member.id,
            due_date=due_date,
        )
        # set the book obj that we know exist to avaiable to false
        book.available_copies -= 1
        # now add the checkout to that database
        session.add(new_checkout)
        # save with rollback protection
        try:
            session.commit()
        # Notice that if we have set error here as a var to access
        # IntegrityError
        except IntegrityError as error:
            # rollback the session to its working state
            session.rollback()
            # state why didn't work and we roll back
            raise ValueError(
                "The checkout could not be saved because it "
                "violated a database constraint."
            ) from error
        # refresh so the obj is up to date in the session
        session.refresh(new_checkout)
        return new_checkout


def return_book(checkout_id: int):
    """
    Return a book. Increments available_copies += 1, sets return_date = today.
    Returns the updated Checkout object.
    """
    # implement
    with Session(engine) as session:
        checkout = session.get(Checkout, checkout_id)

        if checkout is None:
            raise ValueError(f"The ID entered {checkout_id} doesn't exist.")

        # check the return_date isn't already a value
        if checkout.return_date is not None:
            raise ValueError(f"Checkout ID {checkout_id} has already been returned.")

        book = session.get(Book, checkout.book_id)

        # makes sure the book exist. This feels redudent but is an extra step
        # of validaiton that would prevent crash.
        if book is None:
            raise ValueError(f"Book ID {checkout.book_id} does not exist.")

        # set the date to today
        checkout.return_date = date.today()
        # modify the book available_copies attribute/field from the book in session
        book.available_copies += 1

        session.commit()
        # update the checkout object in the session so it's returned correctly.
        session.refresh(checkout)
        return checkout


# ============================================================
# QUERY FUNCTIONS
# ============================================================


def find_books_by_author(author_name: str) -> list:
    """Return all books whose author name contains author_name (case-insensitive)."""
    # implement — use LIKE or ilike for partial matching

    author_name = author_name.strip()
    if not author_name:
        raise ValueError("An author name is required.")

    with Session(engine) as session:
        stmt = (
            # select the Book table
            select(Book)
            # joins the Book to the authors table privided the relationship
            # is set up correctly.
            .join(Book.authors)
            # search for where the Author table has the name field/att that
            # matches the author name argument that is passed to the function.
            # We use .ilike for the insensitive casing.
            .where(
                # percentage gives partial pattern matching.
                # co authored book can appear twice and needs fixed.
                Author.name.ilike(f"%{author_name}%"),
            )
        )
        return session.scalars(stmt).unique().all()


def get_author_by_name(name: str) -> Author | None:
    normalized_name = name.strip().lower()

    with Session(engine) as session:
        stmt = select(Author).where(
            func.lower(Author.name) == normalized_name,
        )
        return session.scalars(stmt).first()


def get_overdue_books() -> list[Checkout]:
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
    """Return all Book objects where available_copies > 0."""
    # implement
    with Session(engine) as session:
        # retrieve Book table books where the books att/field available_copies
        # is True.
        stmt = select(Book).where(Book.available_copies > 0)
        books = session.scalars(stmt).all()
        return books


# just a query of the Book table of all instances of books.
def list_all_books() -> list[Book]:
    """used to obtain all of the books in the library system"""
    with Session(engine) as session:
        # select books table
        stmt = select(Book)
        # execute to obtain the rows and values
        books = session.scalars(stmt).all()
        return books


# search books by title query
def search_books_by_title(book_title: str) -> list[Book]:
    """Return a list of books with partical matches to the title entered."""
    book_title = book_title.strip()

    if not book_title:
        raise ValueError("A title search term is required.")

    with Session(engine) as session:
        stmt = (
            select(Book).where(Book.title.ilike(f"%{book_title}%")).order_by(Book.title)
        )

        return session.scalars(stmt).all()


# get member borrings by id
def get_member_current_borrowings(member_id: int) -> list[Checkout]:
    """Returns the borrowings a member has by a query of their checkouts that
    they currently have. Long tail to get to the book.title to display but
    we'll figure that out on the actual call to this function for display"""
    with Session(engine) as session:
        # this is performing a query on one instance so not all is needed and
        # the member should then be queried.
        member = session.get(Member, member_id)
        if member is None:
            raise ValueError(f"Member ID {member_id} does not exist.")
        # selectinload and selectinload?
        stmt = (
            # select checkout table
            select(Checkout)
            # comparison to the member_id given
            .where(
                Checkout.member_id == member_id,
                # give the return date for that chekout obj tied to that mem
                Checkout.return_date.is_(None),
                # order by the due date
            ).order_by(Checkout.due_date)
        )
        return session.scalars(stmt).all()


# update member email
def update_member_email(member_id: int, new_email: str) -> Member:
    """This is going to be expecting a member_id to then access that member
    obj that we will then use to update the members email and then commit to
    the database and display the results that are refreshed."""
    if not new_email:
        raise ValueError("Email is required!")

    with Session(engine) as session:
        member = session.get(Member, member_id)

        if member is None:
            raise ValueError(f"That user doesn't exist by that id - {member_id}")

        member.email = new_email
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise ValueError(
                f"A member with email {new_email} aldready exists."
            ) from error
        session.refresh(member)
        return member


# the user needs to specify a particular book_id to be able to access the book
# need to check if the book exist. We can do this with a if None.
# a design decsion here could be to accept a int or a str. So book name or id
# should we show the names of books or ids for selection?


# remove book
def remove_book(book_id: int) -> None:
    """Remove a book from the database idicated by the book_id passed to the
    parameter. Prints a successful removal. This is editing the table itself.
    Commit the changes to the table when finished to save."""
    with Session(engine) as session:
        # again there is still the decsion to decide how we want to be able to
        # obtain this value. Maybe that is what we call inside of the menu_cli
        # in particular.

        # this may be handled in the if None clause
        book = session.get(Book, book_id)
        print("This is a redundent error call and I don't know if needed")

        if book is None:
            # how do we call this again for efficieny?
            raise ValueError(f"That book doens't exist by that id - {book_id}")

        # this will delete the instance of the book needs flush(refresed so
        # that the obj is officially removed after the commit())
        session.delete(book)
        # save the changes
        session.commit()
        # update the cache? Is another way to think about this?
        session.refresh()


# this will be another deletion process. The way we handle this is similar to
# the remove book. The important thing here as well with the last function is
# thinking about the CASCADE deletes as this this also remove all related
# products where applicable. To do so takes a True understanding of the models
# relational states. If we deleted a book we wouldn't want to delete the member
# just because we deleted that book or the author.


# remove member
def remove_member(member_id: int) -> None:
    """Remove the member specified. Will dump that info in the cache in some
    sense when we call the refresh on the engine. Completely removing the
    member from the database. The handling of the memeber for checks with the
    input will take place in the menu_cli_call. Should we need to be able to
    raise particular errors depends on the errors we are raising. Refer ot the
    previous functions for guidence and reference."""
    with Session(engine) as session:
        # passes the member_id to the .get to access the specific obj. Raise
        # error if that member obtainment doesn't exist by that int.
        member = session.get(Member, member_id)
        session.delete(member)
        session.commit()
        session.refresh()


# why don't I need use the try block .get().
