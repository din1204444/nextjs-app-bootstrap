-- SDCKL Library Management System SQL Schema

-- Books table
CREATE TABLE books (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  genre VARCHAR(100),
  isbn VARCHAR(20) UNIQUE NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 0
);

-- Users table
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  student_id VARCHAR(50),
  membership_type VARCHAR(50) NOT NULL,
  join_date DATE NOT NULL,
  books_loaned INTEGER DEFAULT 0
);

-- Transactions table
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  book_id INTEGER NOT NULL,
  user_id INTEGER NOT NULL,
  borrow_date DATE NOT NULL,
  due_date DATE NOT NULL,
  return_date DATE,
  status VARCHAR(50) NOT NULL,
  penalty_fee DECIMAL(10, 2) DEFAULT 0.00,
  FOREIGN KEY (book_id) REFERENCES books(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);
