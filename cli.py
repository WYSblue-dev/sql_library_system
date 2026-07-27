"""
Module 3 Project: Library Management System
cli.py — Command-line interface

Your job: Implement each menu handler function below.
The main menu loop is already provided — just fill in the handlers.
"""

from library_system import (
    init_db,
    add_author,
    add_book,
    add_borrower,
    checkout_book,
    return_book,
    find_books_by_author,
    get_overdue_books,
    get_popular_genres,
    get_available_books,
    # added a helper to obtain the author based on existence
    get_author_by_name,
    # added for the clarity of acknoleding name
    Borrower,
)


def menu_add_book():
    """Prompt for book details and add to the database."""
    # capture values needed
    title = input("Title: ").strip()
    isbn = input("ISBN: ").strip()
    author_name = input("Author name: ").strip()

    # if not value entered for any reqs
    if not title or not isbn or not author_name:
        print("Title, ISBN, and author name are required.")
        return

    # Keep asking until the user enters a valid year or leaves it blank.
    while True:
        year_input = input("Published year (optional): ").strip()
        # blank input
        if not year_input:
            published_year = None
            break
        # try numeric
        try:
            published_year = int(year_input)
            break
        except ValueError:
            print("Published year must be a whole number.")
    # capture the genres(need to handle if not seperated with commas)
    genre_input = input("Genres(separated by commas): ").strip()
    # list comp for genre names using the commas to split
    genre_names = [genre.strip() for genre in genre_input.split(",") if genre.strip()]
    # Look for the author directly in the authors table by their name
    # made not case sensitive
    author = get_author_by_name(author_name)

    # no author found then creates a new
    if author is None:
        print(f'Author "{author_name}" was not found.')
        bio = input("Author bio (optional): ").strip() or None
        # uses the name that was entered for the author.(maybe ask if want to
        # add first before assuming....?)
        author = add_author(
            name=author_name,
            bio=bio,
        )
    # add the book
    new_book = add_book(
        title=title,
        isbn=isbn,
        author_id=author.id,
        published_year=published_year,
        genre_names=genre_names,
    )
    # print a nice message
    print(f'Book "{new_book.title}" by {author.name} ' "was added successfully!")


def menu_add_borrower():
    """Prompt for borrower details and register in the database."""
    while True:
        name = input("Name: ").strip()
        email = input("Email: ").strip()
        # equals the input or if black None? This is new to me I believe
        phone = input("Phone (Optional): ").strip() or None
        # conditionally check nots in place.
        if not name or not email:
            print("Name and Email are required try again.")
            continue
        try:
            borrower = add_borrower(
                name=name,
                email=email,
                phone=phone,
            )
        except ValueError as error:
            print(error)
            continue
        print(
            f"{borrower.name} was successfully added "
            f"with borrower ID {borrower.id}."
        )
        break


def menu_checkout():
    """Prompt for book ID and borrower ID, then check out the book."""
    # TODO: Show available books (call get_available_books())
    # need the book id and the borrower id to be able to check out a book.
    # so we'll get those via a loop and the call the chekcout_book function,
    # and handle the checkout_book()
    # show books
    while True:
        try:
            borrower_id = int(input("Please enter your borrower id: "))
            break
        except ValueError:
            print("Please enter a valid id number. Try again.")
            continue

    books = get_available_books()
    # need to handle if they're no books and need to handle the book id itself
    # from the users selection. This is more of a ui decision.
    if not books:
        print("No books are currently available sorry.")
        return
    # displays books since they exist
    for place, book in enumerate(books, start=1):
        print(f"{place}. Book title - {book.title} ID - {book.id}")

    # True loop for input handling
    while True:
        try:
            prompt = int(input("What book would you like to check out(ID)?"))
        # needs to be a integer handling
        except ValueError:
            print("Please enter a valid number. Try again.")
            # restart loop
            continue
        # we didn't handle the checkout_book days. That's optional. Who should
        # be checking that work?
        for book in books:
            if prompt == book.id:
                print(f"It looks like you selected {book.title}")
                # since this returns a checkout date we could add a timestamp for
                # the due_date to the user.
                taken_book = checkout_book(book_id=prompt, borrower_id=borrower_id)
                # The pretty print out.
                print(f"{book.title} has been successfully checked out.")
                # how do we get and set the book to unavailable? did we handle this
                # in our class? yes we did so that is taken care of.
                return taken_book
        print("Please enter a valid ID. Try again")
        continue


def menu_return():
    """Prompt for checkout ID and return the book."""
    # TODO: Prompt for checkout_id, call return_book(), print confirmation
    while True:
        prompt = "I need your checkout ID to return the book you have checked out."
        user_checkout_id = int(input(prompt, "\nID: "))
        returned_book = return_book(checkout_id=user_checkout_id)
        return returned_book


def menu_search_by_author():
    """Prompt for author name and display matching books."""
    # TODO: Prompt for author_name, call find_books_by_author(), print results


def menu_overdue():
    """Display all overdue checkouts."""
    # TODO: Call get_overdue_books() and print results


def menu_popular_genres():
    """Display the most popular genres by checkout count."""
    # TODO: Call get_popular_genres() and print results


def main():
    init_db()

    while True:
        print("\n=== Library Management System ===")
        print("1. Add a book")
        print("2. Register a borrower")
        print("3. Check out a book")
        print("4. Return a book")
        print("5. Search by author")
        print("6. View overdue books")
        print("7. View popular genres")
        print("8. Quit")

        choice = input("\nChoose an option (1-8): ").strip()

        if choice == "1":
            menu_add_book()
        elif choice == "2":
            menu_add_borrower()
        elif choice == "3":
            menu_checkout()
        elif choice == "4":
            menu_return()
        elif choice == "5":
            menu_search_by_author()
        elif choice == "6":
            menu_overdue()
        elif choice == "7":
            menu_popular_genres()
        elif choice == "8":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-8.")


if __name__ == "__main__":
    main()
