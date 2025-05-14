from datetime import datetime, timedelta
from .models import Session, Book, User, Transaction
from .config import Config

class LibrarySystem:
    def __init__(self):
        self.session = Session()
        self.library_name = Config.LIBRARY_NAME
        self.domain = Config.DOMAIN_NAME

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

    def add_user(self, name, email, student_id, membership_type):
        try:
            # Format email with domain if not provided
            if '@' not in email:
                email = f"{email}@{self.domain}"
                
            user = User(
                name=name,
                email=email,
                student_id=student_id,
                membership_type=membership_type,
                join_date=datetime.utcnow()
            )
            self.session.add(user)
            self.session.commit()
            return user
        except Exception as e:
            self.session.rollback()
            raise e

    def borrow_book(self, book_id, user_id):
        try:
            book = self.session.query(Book).get(book_id)
            user = self.session.query(User).get(user_id)

            if not book or not user:
                raise ValueError("Book or user not found")

            if book.quantity <= 0:
                raise ValueError("Book not available")

            if user.books_loaned >= Config.MAX_BOOKS_PER_USER:
                raise ValueError(f"User has reached maximum number of books allowed ({Config.MAX_BOOKS_PER_USER})")

            transaction = Transaction(
                book_id=book_id,
                user_id=user_id,
                borrow_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=Config.LOAN_PERIOD_DAYS),
                status="Borrowed"
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

            transaction.return_date = datetime.utcnow()
            transaction.status = "Returned"
            transaction.penalty_fee = transaction.calculate_penalty()

            transaction.book.quantity += 1
            transaction.user.books_loaned -= 1

            self.session.commit()
            return transaction
        except Exception as e:
            self.session.rollback()
            raise e

    def get_overdue_books(self):
        today = datetime.utcnow().date()
        return self.session.query(Transaction).filter(
            Transaction.status == "Borrowed",
            Transaction.due_date < today
        ).all()

    def search_books(self, query):
        return self.session.query(Book).filter(
            (Book.title.ilike(f"%{query}%")) |
            (Book.author.ilike(f"%{query}%")) |
            (Book.genre.ilike(f"%{query}%")) |
            (Book.isbn.ilike(f"%{query}%"))
        ).all()

    def search_users(self, query):
        return self.session.query(User).filter(
            (User.name.ilike(f"%{query}%")) |
            (User.email.ilike(f"%{query}%")) |
            (User.student_id.ilike(f"%{query}%"))
        ).all()

    def get_user_history(self, user_id):
        return self.session.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.borrow_date.desc()).all()

    def get_book_history(self, book_id):
        return self.session.query(Transaction).filter(
            Transaction.book_id == book_id
        ).order_by(Transaction.borrow_date.desc()).all()

    def get_system_info(self):
        return {
            "library_name": self.library_name,
            "domain": self.domain,
            "version": Config.VERSION,
            "loan_period": Config.LOAN_PERIOD_DAYS,
            "max_books_per_user": Config.MAX_BOOKS_PER_USER,
            "penalty_rate": Config.PENALTY_RATE,
            "max_penalty": Config.MAX_PENALTY
        }

    def close(self):
        self.session.close()
