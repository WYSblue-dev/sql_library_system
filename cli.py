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
    add_member,
    checkout_book,
    return_book,
    find_books_by_author,
    get_overdue_books,
    get_popular_genres,
    get_available_books,
    # added a helper to obtain the author based on existence
    get_author_by_name,
    # added for the clarity of acknoleding name
    Member,
    # my added functions that need associated commands
    list_all_books,
    search_books_by_title,
    get_member_current_borrowings,
    update_member_email,
    remove_book,
    remove_member,
)


def menu_add_book():
    """Prompt for book details and add to the database."""
    title = input("Title: ").strip()
    isbn = input("ISBN: ").strip()

    author_input = input("Author names (separated by commas): ").strip()

    author_names = [name.strip() for name in author_input.split(",") if name.strip()]

    if not title or not isbn or not author_names:
        print("Title, ISBN, and at least one author are required.")
        return

    while True:
        year_input = input("Published year (optional): ").strip()
        if not year_input:
            year_published = None
            break

        try:
            year_published = int(year_input)
            break
        except ValueError:
            print("Published year must be a whole number.")

    genre_input = input("Genres (separated by commas): ").strip()
    genre_names = [genre.strip() for genre in genre_input.split(",") if genre.strip()]

    authors = []
    for author_name in author_names:
        author = get_author_by_name(author_name)
        if author is None:
            print(f'Author "{author_name}" was not found.')
            bio = input(f'Bio for "{author_name}" (optional): ').strip() or None
            author = add_author(
                name=author_name,
                bio=bio,
            )
        authors.append(author)
    author_ids = [author.id for author in authors]
    try:
        new_book = add_book(
            title=title,
            isbn=isbn,
            author_ids=author_ids,
            year_published=year_published,
            genre_names=genre_names,
        )
    except ValueError as error:
        print(f"Book could not be added: {error}")
        return

    author_display = ", ".join(author.name for author in authors)
    print(f'Book "{new_book.title}" by {author_display} ' "was added successfully!")
    return new_book


def menu_add_member():
    """Prompt for member details and register in the database."""
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
            member = add_member(
                name=name,
                email=email,
                phone=phone,
            )
        except ValueError as error:
            print(error)
            continue
        print(f"{member.name} was successfully added " f"with member ID {member.id}.")
        break


def menu_checkout():
    """Prompt for book ID and member ID, then check out the book."""
    # TODO: Show available books (call get_available_books())
    books = get_available_books()

    if not books:
        print("No books are currently available sorry.")
        return

    # displays books since they exist
    print("\nAvailable books:")

    # this is the better bet to handle the selected book later that is available
    # without this the user could then enter a valid book id that wasn't shown
    # but can't be checked out. Using available books with a dictionary lets
    # us handle the keys with the .get function that python provides
    available_books = {book.id: book for book in books}

    for book in books:
        print(f"Book ID: {book.id} | Title: {book.title}")

    # True loop for input handling
    while True:
        try:
            member_id = int(input("\nPlease enter your member ID: ").strip())

            book_id = int(input("Please enter the book ID: ").strip())
        # needs to be a integer handling
        except ValueError:
            print("Please enter a valid whole numbers. Try again.")
            # restart loop
            continue

        # interation utilizing next function until the condiiton of the
        # if conditional is satisfied.
        # original approach
        # selected_book = next(book for book in books if book.id == book_id)

        # uses the .get to handle key errors
        selected_book = available_books.get(book_id)
        # now we check if the books actually is available
        if selected_book is None:
            print("That ID does not belong to one of the available books.")
            # reset the loop
            continue

        # handle the checkout creation now that we know the input is validated
        try:
            checkout = checkout_book(
                book_id=book_id,
                member_id=member_id,
            )

        # Handle error in worst case senario
        except ValueError as error:
            print(f"Checkout failed: {error}")
            continue

        # Nice print out statement
        print(f'"{selected_book.title}" was successfully checked out.')
        # express due date
        print(f"Due date: {checkout.due_date}")

        return checkout


def menu_return():
    """Prompt for checkout ID and return the book."""
    # TODO: Prompt for checkout_id, call return_book(), print confirmation
    # our return_book handles the value error already. Maybe handle if None
    # bassed on the int entered by checking against the checkouts table.
    while True:
        # could do a account look up here of sorts.
        prompt = "I need your checkout ID to return the book you have checked out."
        try:
            user_checkout_id = int(input(f"{prompt} \nID: ").strip())
            returned_checkout = return_book(
                checkout_id=user_checkout_id,
            )
        except ValueError as error:
            # will show message with corresponding error
            print(f"Return failed: {error}")
            continue

        print(f"Checkout ID {returned_checkout.id} was successfully returned!")
        return returned_checkout


def menu_search_by_author():
    """Prompt for author name and display matching books."""
    # TODO: Prompt for author_name, call find_books_by_author(), print results
    while True:
        author_search = "Type in the author you are looking for: "
        author_name = str(input(author_search)).strip().lower()
        try:
            books = find_books_by_author(author_name)
            print(f"Author books by {author_name.title()}:")
            for book in books:
                print(f"{book.title.upper()}")
            break
        except ValueError:
            print("Please enter a valid name. Try again.")
            continue


def menu_overdue():
    """Display all overdue checkouts."""
    # TODO: Call get_overdue_books() and print results
    overdue_books = get_overdue_books()
    for checkout in overdue_books:
        print(
            f"Overdue book title - {checkout.book.title}"
            f"\nOverdue member name - {checkout.member.name}\nDue Date - {checkout.due_date}"
        )


def menu_popular_genres():
    """Display the most popular genres by checkout count."""
    # TODO: Call get_popular_genres() and print results
    popular_genres = get_popular_genres()
    print("Most popular genres by count:")
    for genre in popular_genres:
        print(f"{genre}")


# my functions that I have added


def menu_list_all_books():
    """List all of the books in the system. Makes a call to list_all_books."""
    books = list_all_books()
    print("BOOK TITLES:")
    for place, book in enumerate(books, start=1):
        print(f"{place}. TITLE: {book.title}")


def menu_search_books_by_title(book_title: str):
    """Search all books with partial matching to titles. We should set a limit
    inside of the library system to be able to handle the mass amounts of
    potential short matches. Kinda like a fuzzy search?"""
    books = search_books_by_title()
    print(f"SIMILAR BOOKS BY TITLE {book_title}:")
    for place, book in enumerate(books, start=1):
        print(f"{place}. TITLE: {book.title}")


def menu_get_member_current_borrowings(member_id: int):
    """Displays all of the checkouts that a current member has if any. Makes a
    call to the get_member_current_borrowings."""
    member = get_member_current_borrowings()
    print()


def menu_update_member_email(member_id: int):
    """Update the members email. Makes a call to update_member_email."""
    update_member = update_member_email()
    print()


def menu_remove_book(book_id: int):
    """Remove a book from the books table. Makes a call to remove_book."""
    book_removed = remove_book()
    print()


def menu_remove_member(member_id: int):
    """Remove a member from the members table. Makes a call to remove_member."""
    member_removed = remove_member()
    print()


def main():
    init_db()

    while True:
        print("\n=== Library Management System ===")
        print("1. Add a book")
        print("2. Register a member")
        print("3. Check out a book")
        print("4. Return a book")
        print("5. Search by author")
        print("6. View overdue books")
        print("7. View popular genres")
        print("8. List all books")
        print("9. Search book by title")
        print("10. Get members current borrowings")
        print("11. Update member email")
        print("12. Remove book")
        print("13. Remove member")
        print("14. Quit")

        choice = input("\nChoose an option (1-14): ").strip()

        if choice == "1":
            menu_add_book()
        elif choice == "2":
            menu_add_member()
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

        # these particular functions may need the corresponding menu_functions
        # to be able to handle them correclty and have the right prints. The
        # function creation in the library_system itself is what handles the
        # use of the functions from those files. We must print the messages
        # there for the cli display
        elif choice == "8":
            menu_list_all_books()
        elif choice == "9":
            menu_search_books_by_title()
        elif choice == "10":
            menu_get_member_current_borrowings()
        elif choice == "11":
            menu_update_member_email()
        elif choice == "12":
            menu_remove_book()
        elif choice == "13":
            menu_remove_member()
        elif choice == "14":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-14.")


if __name__ == "__main__":
    main()
