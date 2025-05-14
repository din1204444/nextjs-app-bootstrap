from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sdckl_library_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    genre = db.Column(db.String(100))
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0)
    transactions = db.relationship('Transaction', backref='book', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    student_id = db.Column(db.String(50))
    membership_type = db.Column(db.String(50), nullable=False)
    join_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    books_loaned = db.Column(db.Integer, default=0)
    transactions = db.relationship('Transaction', backref='user', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrow_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    status = db.Column(db.String(50), nullable=False)
    penalty_fee = db.Column(db.Float, default=0.00)

    def calculate_penalty(self):
        if self.status == "Returned" or self.status == "Borrowed":
            return 0.00
        
        today = datetime.utcnow().date()
        days_overdue = (today - self.due_date).days
        if days_overdue <= 0:
            return 0.00
            
        penalty_rate = 5.00  # RM 5.00 per day
        max_penalty = 50.00  # Maximum RM 50.00
        penalty = min(days_overdue * penalty_rate, max_penalty)
        return penalty

# Routes
@app.route('/')
def index():
    books_count = Book.query.count()
    users_count = User.query.count()
    active_loans = Transaction.query.filter_by(status="Borrowed").count()
    return render_template('index.html', 
                         books_count=books_count,
                         users_count=users_count,
                         active_loans=active_loans)

@app.route('/books')
def books():
    books = Book.query.all()
    return render_template('books.html', books=books)

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/transactions')
def transactions():
    transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=transactions)

# API Routes
@app.route('/api/books', methods=['GET', 'POST'])
def api_books():
    if request.method == 'POST':
        data = request.json
        new_book = Book(
            title=data['title'],
            author=data['author'],
            genre=data['genre'],
            isbn=data['isbn'],
            quantity=data['quantity']
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201
    
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'isbn': book.isbn,
        'quantity': book.quantity
    } for book in books])

@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if request.method == 'POST':
        data = request.json
        new_user = User(
            name=data['name'],
            email=data['email'],
            student_id=data.get('student_id'),
            membership_type=data['membership_type'],
            join_date=datetime.utcnow()
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User added successfully'}), 201
    
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'student_id': user.student_id,
        'membership_type': user.membership_type,
        'join_date': user.join_date.strftime('%Y-%m-%d'),
        'books_loaned': user.books_loaned
    } for user in users])

@app.route('/api/transactions', methods=['GET', 'POST'])
def api_transactions():
    if request.method == 'POST':
        data = request.json
        new_transaction = Transaction(
            book_id=data['book_id'],
            user_id=data['user_id'],
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=14),
            status="Borrowed"
        )
        db.session.add(new_transaction)
        
        # Update book and user records
        book = Book.query.get(data['book_id'])
        user = User.query.get(data['user_id'])
        book.quantity -= 1
        user.books_loaned += 1
        
        db.session.commit()
        return jsonify({'message': 'Transaction created successfully'}), 201
    
    transactions = Transaction.query.all()
    return jsonify([{
        'id': t.id,
        'book_title': t.book.title,
        'user_name': t.user.name,
        'borrow_date': t.borrow_date.strftime('%Y-%m-%d'),
        'due_date': t.due_date.strftime('%Y-%m-%d'),
        'return_date': t.return_date.strftime('%Y-%m-%d') if t.return_date else None,
        'status': t.status,
        'penalty_fee': t.calculate_penalty()
    } for t in transactions])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
