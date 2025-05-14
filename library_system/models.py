from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from .config import Config

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    isbn = Column(String(20), unique=True, nullable=False)
    quantity = Column(Integer, default=0)
    transactions = relationship('Transaction', back_populates='book')

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    student_id = Column(String(50))
    membership_type = Column(String(50), nullable=False)
    join_date = Column(Date, nullable=False, default=datetime.utcnow)
    books_loaned = Column(Integer, default=0)
    transactions = relationship('Transaction', back_populates='user')

    @property
    def email_with_domain(self):
        # Returns email with the configured domain
        local_part = self.email.split('@')[0]
        return f"{local_part}@{Config.DOMAIN_NAME}"

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    borrow_date = Column(Date, nullable=False, default=datetime.utcnow)
    due_date = Column(Date, nullable=False)
    return_date = Column(Date)
    status = Column(String(50), nullable=False)
    penalty_fee = Column(Float, default=0.00)
    
    book = relationship('Book', back_populates='transactions')
    user = relationship('User', back_populates='transactions')

    def calculate_penalty(self):
        if self.status == "Returned" or self.status == "Borrowed":
            return 0.00
        
        today = datetime.utcnow().date()
        days_overdue = (today - self.due_date).days
        if days_overdue <= 0:
            return 0.00
            
        return min(days_overdue * Config.PENALTY_RATE, Config.MAX_PENALTY)

# Database setup
engine = create_engine(Config.DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
