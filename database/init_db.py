from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Book, User, Transaction
from datetime import datetime, timedelta

# Create database engine (using SQLite for simplicity)
DATABASE_URL = "sqlite:///library.db"
engine = create_engine(DATABASE_URL)

# Create all tables
Base.metadata.create_all(engine)

# Create a session factory
Session = sessionmaker(bind=engine)
session = Session()

def init_database():
    try:
        # Add sample books
        books = [
            Book(
                title="The Great Gatsby",
                author="F. Scott Fitzgerald",
                genre="Classic Fiction",
                isbn="978-0743273565",
                quantity=3
            ),
            Book(
                title="1984",
                author="George Orwell",
                genre="Science Fiction",
                isbn="978-0451524935",
                quantity=2
            ),
            Book(
                title="To Kill a Mockingbird",
                author="Harper Lee",
                genre="Literary Fiction",
                isbn="978-0446310789",
                quantity=4
            )
        ]
        session.add_all(books)
        session.commit()

        # Add sample users
        users = [
            User(
                name="John Smith",
                email="john.smith@email.com",
                student_id="STU2024001",
                membership_type="Student",
                join_date=datetime(2024, 1, 15).date(),
                books_loaned=2
            ),
            User(
                name="Sarah Johnson",
                email="sarah.j@email.com",
                membership_type="Faculty",
                join_date=datetime(2023, 12, 1).date(),
                books_loaned=3
            ),
            User(
                name="Michael Brown",
                email="m.brown@email.com",
                student_id="STU2024003",
                membership_type="Student",
                join_date=datetime(2024, 2, 1).date(),
                books_loaned=1
            )
        ]
        session.add_all(users)
        session.commit()

        # Add sample transactions
        transactions = [
            Transaction(
                book_id=1,
                user_id=1,
                borrow_date=datetime(2024, 2, 15).date(),
                due_date=datetime(2024, 3, 1).date(),
                status="Borrowed",
                penalty_fee=0.00
            ),
            Transaction(
                book_id=2,
                user_id=2,
                borrow_date=datetime(2024, 2, 10).date(),
                due_date=datetime(2024, 2, 24).date(),
                status="Overdue",
                penalty_fee=50.00
            ),
            Transaction(
                book_id=3,
                user_id=3,
                borrow_date=datetime(2024, 2, 1).date(),
                due_date=datetime(2024, 2, 15).date(),
                return_date=datetime(2024, 2, 14).date(),
                status="Returned",
                penalty_fee=0.00
            )
        ]
        session.add_all(transactions)
        session.commit()

        print("Database initialized successfully with sample data!")

    except Exception as e:
        print(f"Error initializing database: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_database()
