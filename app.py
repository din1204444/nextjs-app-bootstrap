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
    recent_transactions = Transaction.query.order_by(Transaction.borrow_date.desc()).limit(5).all()
    return render_template('index.html', 
                         books_count=books_count,
                         users_count=users_count,
                         active_loans=active_loans,
                         recent_transactions=recent_transactions)

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
        # Input validation
        required_fields = ['title', 'author', 'isbn', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        try:
            new_book = Book(
                title=data['title'],
                author=data['author'],
                genre=data.get('genre', ''),
                isbn=data['isbn'],
                quantity=int(data['quantity'])
            )
            db.session.add(new_book)
            db.session.commit()
            return jsonify({'message': 'Book added successfully'}), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding book: {e}")
            return jsonify({'error': 'Failed to add book'}), 500
    
    books = Book.query.all()
    return jsonify([{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'genre': book.genre,
        'isbn': book.isbn,
        'quantity': book.quantity
    } for book in books])

@app.route('/api/books/<int:book_id>', methods=['GET', 'PUT', 'DELETE'])
def api_book_detail(book_id):
    book = Book.query.get_or_404(book_id)

    if request.method == 'GET':
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'genre': book.genre,
            'isbn': book.isbn,
            'quantity': book.quantity
        })

    elif request.method == 'PUT':
        data = request.json
        required_fields = ['title', 'author', 'isbn', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        try:
            book.title = data['title']
            book.author = data['author']
            book.genre = data.get('genre', '')
            book.isbn = data['isbn']
            book.quantity = int(data['quantity'])
            db.session.commit()
            return jsonify({'message': 'Book updated successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating book: {e}")
            return jsonify({'error': 'Failed to update book'}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(book)
            db.session.commit()
            return jsonify({'message': 'Book deleted successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting book: {e}")
            return jsonify({'error': 'Failed to delete book'}), 500

@app.route('/api/users', methods=['GET', 'POST'])
def api_users():
    if request.method == 'POST':
        data = request.json
        # Input validation
        required_fields = ['name', 'email', 'membership_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        try:
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
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding user: {e}")
            return jsonify({'error': 'Failed to add user'}), 500
    
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

@app.route('/api/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def api_user_detail(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'GET':
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'student_id': user.student_id,
            'membership_type': user.membership_type,
            'join_date': user.join_date.strftime('%Y-%m-%d'),
            'books_loaned': user.books_loaned
        })

    elif request.method == 'PUT':
        data = request.json
        required_fields = ['name', 'email', 'membership_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        try:
            user.name = data['name']
            user.email = data['email']
            user.student_id = data.get('student_id')
            user.membership_type = data['membership_type']
            db.session.commit()
            return jsonify({'message': 'User updated successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating user: {e}")
            return jsonify({'error': 'Failed to update user'}), 500

    elif request.method == 'DELETE':
        try:
            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'User deleted successfully'})
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting user: {e}")
            return jsonify({'error': 'Failed to delete user'}), 500

@app.route('/api/transactions', methods=['GET', 'POST'])
def api_transactions():
    if request.method == 'POST':
        data = request.json
        # Input validation
        required_fields = ['book_id', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        try:
            book = Book.query.get(data['book_id'])
            user = User.query.get(data['user_id'])
            if not book or book.quantity <= 0:
                return jsonify({'error': 'Book not available'}), 400
            if not user:
                return jsonify({'error': 'User not found'}), 400

            new_transaction = Transaction(
                book_id=data['book_id'],
                user_id=data['user_id'],
                borrow_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=14),
                status="Borrowed"
            )
            db.session.add(new_transaction)

            # Update book and user records
            book.quantity -= 1
            user.books_loaned += 1

            db.session.commit()
            return jsonify({'message': 'Transaction created successfully'}), 201
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating transaction: {e}")
            return jsonify({'error': 'Failed to create transaction'}), 500
    
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

@app.route('/api/transactions/<int:transaction_id>', methods=['GET'])
def api_transaction_detail(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return jsonify({
        'id': transaction.id,
        'book_title': transaction.book.title,
        'user_name': transaction.user.name,
        'borrow_date': transaction.borrow_date.strftime('%Y-%m-%d'),
        'due_date': transaction.due_date.strftime('%Y-%m-%d'),
        'return_date': transaction.return_date.strftime('%Y-%m-%d') if transaction.return_date else None,
        'status': transaction.status,
        'penalty_fee': transaction.calculate_penalty()
    })

@app.route('/api/transactions/<int:transaction_id>/return', methods=['POST'])
def api_return_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.status != 'Borrowed':
        return jsonify({'error': 'Transaction is not currently borrowed'}), 400
    try:
        transaction.status = 'Returned'
        transaction.return_date = datetime.utcnow()
        # Update book quantity and user loan count
        transaction.book.quantity += 1
        transaction.user.books_loaned -= 1
        db.session.commit()
        return jsonify({'message': 'Book returned successfully'})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error returning book: {e}")
        return jsonify({'error': 'Failed to return book'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
