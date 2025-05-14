from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Book, User, Transaction
from datetime import datetime, timedelta
from decimal import Decimal

# Database configuration
DATABASE_URL = "sqlite:///library.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Penalty fee configuration
PENALTY_RATE_PER_DAY = Decimal('5.00')  # RM 5.00 per day
MAX_PENALTY_FEE = Decimal('50.00')      # Maximum RM 50.00

class LibraryOperations:
    def __init__(self):
        self.session = Session()

    def close(self):
        self.session.close()

    # Book Operations
    def add_book(self, title, author, genre, isbn, quantity):
        try:
            book = Book(
                title=title,
                author=author,
                genre=genre,
                isbn=isbn,
                quantity=quantity
            )
            self.session.add(book)
            self.session.commit()
            return book
        except Exception as e:
            self.session.rollback()
            raise e

    def get_book(self, book_id):
        return self.session.query(Book).get(book_id)

    def search_books(self, query):
        return self.session.query(Book).filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%")) |
            (Book.isbn.ilike(f"%{query}%"))
        ).all()

    def update_book_quantity(self, book_id, new_quantity):
        book = self.get_book(book_id)
        if book:
            book.quantity = new_quantity
            self.session.commit()
            return True
        return False

    # User Operations
    def add_user(self, name, email, student_id, membership_type):
        try:
            user = User(
                name=name,
                email=email,
                student_id=student_id,
                membership_type=membership_type,
                join_date=datetime.now().date(),
                books_loaned=0
            )
            self.session.add(user)
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            raise e

    def get_user(self, user_id):
        return self.session.query(User).get(user_id)

    def search_users(self, query):
        return self.session.query(User).filter(
            (User.name.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%")) |
            (User.student_id.ilike(f"%{query}%"))
        ).all()

    # Transaction Operations
    def borrow_book(self, book_id, user_id, due_date):
        try:
            book = self.get_book(book_id)
            user = self.get_user(user_id)
            
            if not book or not user:
                raise ValueError("Book or user not found")
            
            if book.quantity <= 0:
                raise ValueError("Book not available")
            
            transaction = Transaction(
                book_id=book_id,
                user_id=user_id,
                borrow_date=datetime.now().date(),
                due_date=due_date,
                status="Borrowed",
                penalty_fee=0.00
            )
            
            book.quantity -= 1
            user.books_loaned += 1
            
            self.session.add(transaction)
            self.session.commit()
            return transaction
        except Exception as e:
            self.session.rollback()
            raise e

    def return_book(self, transaction_id):
        try:
            transaction = self.session.query(Transaction).get(transaction_id)
            if not transaction:
                raise ValueError("Transaction not found")
            
            if transaction.status == "Returned":
                raise ValueError("Book already returned")
            
            # Calculate penalty if overdue
            today = datetime.now().date()
            if today > transaction.due_date:
                days_overdue = (today - transaction.due_date).days
                penalty = Decimal(str(days_overdue)) * PENALTY_RATE_PER_DAY
                transaction.penalty_fee = min(penalty, MAX_PENALTY_FEE)
            
            transaction.return_date = today
            transaction.status = "Returned"
            
            # Update book quantity and user's borrowed books count
            book = self.get_book(transaction.book_id)
            user = self.get_user(transaction.user_id)
            book.quantity += 1
            user.books_loaned -= 1
            
            self.session.commit()
            return transaction
        except Exception as e:
            self.session.rollback()
            raise e

    def get_overdue_transactions(self):
        today = datetime.now().date()
        return self.session.query(Transaction).filter(
            Transaction.due_date < today,
            Transaction.status != "Returned"
        ).all()

    def calculate_penalty(self, transaction_id):
        transaction = self.session.query(Transaction).get(transaction_id)
        if not transaction:
            raise ValueError("Transaction not found")
        
        if transaction.status == "Returned":
            return transaction.penalty_fee
        
        today = datetime.now().date()
        if today > transaction.due_date:
            days_overdue = (today - transaction.due_date).days
            penalty = Decimal(str(days_overdue)) * PENALTY_RATE_PER_DAY
            return min(penalty, MAX_PENALTY_FEE)
        return Decimal('0.00')

# Example usage:
if __name__ == "__main__":
    lib = LibraryOperations()
    try:
        # Search for books
        books = lib.search_books("Gatsby")
        for book in books:
            print(f"Found book: {book.title} by {book.author}")
        
        # Check overdue books
        overdue = lib.get_overdue_transactions()
        for transaction in overdue:
            penalty = lib.calculate_penalty(transaction.id)
            print(f"Overdue book: {transaction.book.title}, Penalty: RM {penalty:.2f}")
            
    finally:
        lib.close()
