# Module 3 Project: Library Management System

## Setup

1. Activate your virtual environment:
   ```bash
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Seed the database with sample data:
   ```bash
   python seed_data.py
   ```
4. Launch the CLI:
   ```bash
   python cli.py
   ```

## What You're Building

A command-line library management system backed by SQLAlchemy. You'll implement:

- **Models** (`library_system.py`): Book, Author, Borrower, Genre with proper relationships
- **CRUD operations**: Add books/borrowers, check out and return books
- **Queries**: Search by author, find overdue books, most popular genres
- **CLI** (`cli.py`): A menu-driven interface for all operations

## Schema

- **Author**: id, name, bio (optional)
- **Genre**: id, name (unique)
- **Book**: id, title, isbn (unique), published_year, author_id (FK), available (bool). Many-to-many with Genre.
- **Borrower**: id, name, email (unique), phone (optional)
- **Checkout**: id, book_id (FK), borrower_id (FK), checkout_date, due_date, return_date (NULL if not returned)

## File Overview

| File | Your Job |
|------|----------|
| `library_system.py` | Implement SQLAlchemy models and all database functions |
| `cli.py` | Implement the menu handler functions (loop provided) |
| `seed_data.py` | Add seed data to test your system |
