"""
seed_data.py — Populate the database with sample data for testing.
Run this AFTER implementing the models in library_system.py:
    python seed_data.py
"""

from library_system import init_db, add_author, add_book, add_member


from library_system import (
    Base,
    engine,
    init_db,
    add_author,
    add_book,
    add_member,
    checkout_book,
    return_book,
)


def seed():
    # Reset the demonstration database so this script can be run repeatedly.
    # WARNING: This deletes the current database contents.
    Base.metadata.drop_all(engine)
    init_db()

    print("Database initialized.")

    # --------------------------------------------------------
    # Authors
    # Requirement: at least 3
    # We use 4 so Good Omens can demonstrate multiple authors.
    # --------------------------------------------------------

    tolkien = add_author(
        "J.R.R. Tolkien",
        "Author of The Lord of the Rings",
    )

    austen = add_author(
        "Jane Austen",
        "English novelist known for social commentary",
    )

    gaiman = add_author(
        "Neil Gaiman",
        "English author of fantasy fiction",
    )

    pratchett = add_author(
        "Terry Pratchett",
        "English fantasy author",
    )

    # --------------------------------------------------------
    # Books
    # Requirement: at least 5
    # --------------------------------------------------------

    hobbit = add_book(
        title="The Hobbit",
        isbn="978-0618260300",
        author_ids=[tolkien.id],
        year_published=1937,
        available_copies=2,
        genre_names=["Fantasy", "Adventure"],
    )

    lord_of_the_rings = add_book(
        title="The Lord of the Rings",
        isbn="978-0544003415",
        author_ids=[tolkien.id],
        year_published=1954,
        available_copies=1,
        genre_names=["Fantasy", "Adventure"],
    )

    pride_and_prejudice = add_book(
        title="Pride and Prejudice",
        isbn="978-0141439518",
        author_ids=[austen.id],
        year_published=1813,
        available_copies=1,
        genre_names=["Fiction", "Romance"],
    )

    emma = add_book(
        title="Emma",
        isbn="978-0141439587",
        author_ids=[austen.id],
        year_published=1815,
        available_copies=1,
        genre_names=["Fiction", "Romance"],
    )

    good_omens = add_book(
        title="Good Omens",
        isbn="978-0060853983",
        author_ids=[gaiman.id, pratchett.id],
        year_published=1990,
        available_copies=2,
        genre_names=["Fantasy", "Comedy"],
    )

    # --------------------------------------------------------
    # Members
    # Requirement: at least 4
    # --------------------------------------------------------

    alice = add_member(
        "Alice Chen",
        "alice@example.com",
        "555-0101",
    )

    bob = add_member(
        "Bob Martinez",
        "bob@example.com",
    )

    carla = add_member(
        "Carla Singh",
        "carla@example.com",
        "555-0103",
    )

    david = add_member(
        "David Brooks",
        "david@example.com",
    )

    # --------------------------------------------------------
    # Borrowings
    # Requirement: at least 6, some returned and some active
    # --------------------------------------------------------

    # Borrowing 1 — returned
    checkout_1 = checkout_book(
        book_id=hobbit.id,
        member_id=alice.id,
    )

    # Borrowing 2 — returned
    checkout_2 = checkout_book(
        book_id=pride_and_prejudice.id,
        member_id=bob.id,
    )

    # Borrowing 3 — returned
    checkout_3 = checkout_book(
        book_id=good_omens.id,
        member_id=carla.id,
    )

    # Setting return_date through the project's return function.
    return_book(checkout_1.id)
    return_book(checkout_2.id)
    return_book(checkout_3.id)

    # Borrowing 4 — still active
    checkout_book(
        book_id=lord_of_the_rings.id,
        member_id=david.id,
    )

    # Borrowing 5 — still active
    checkout_book(
        book_id=emma.id,
        member_id=alice.id,
    )

    # Borrowing 6 — still active
    checkout_book(
        book_id=good_omens.id,
        member_id=bob.id,
    )

    print("Seed complete: " "5 books, " "4 authors, " "4 members, " "and 6 borrowings.")


if __name__ == "__main__":
    seed()
