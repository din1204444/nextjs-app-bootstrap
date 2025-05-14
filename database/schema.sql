-- SDCKL Library Management System SQL Schema

-- Books table
CREATE TABLE books (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  genre VARCHAR(100),
  isbn VARCHAR(20) NOT NULL UNIQUE,
  quantity INT NOT NULL DEFAULT 0
);

-- Users table
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  student_id VARCHAR(50),
  membership_type VARCHAR(50) NOT NULL,
  join_date DATE NOT NULL,
  books_loaned INT DEFAULT 0
);

-- Transactions table
CREATE TABLE transactions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  book_id INT NOT NULL,
  user_id INT NOT NULL,
  borrow_date DATE NOT NULL,
  due_date DATE NOT NULL,
  return_date DATE,
  status VARCHAR(50) NOT NULL,
  penalty_fee DECIMAL(10, 2) DEFAULT 0.00,
  FOREIGN KEY (book_id) REFERENCES books(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Sample data for Books
INSERT INTO books (title, author, genre, isbn, quantity) VALUES
('The Great Gatsby', 'F. Scott Fitzgerald', 'Classic Fiction', '978-0743273565', 3),
('1984', 'George Orwell', 'Science Fiction', '978-0451524935', 2),
('To Kill a Mockingbird', 'Harper Lee', 'Literary Fiction', '978-0446310789', 4);

-- Sample data for Users
INSERT INTO users (name, email, student_id, membership_type, join_date, books_loaned) VALUES
('John Smith', 'john.smith@email.com', 'STU2024001', 'Student', '2024-01-15', 2),
('Sarah Johnson', 'sarah.j@email.com', NULL, 'Faculty', '2023-12-01', 3),
('Michael Brown', 'm.brown@email.com', 'STU2024003', 'Student', '2024-02-01', 1);

-- Sample data for Transactions
INSERT INTO transactions (book_id, user_id, borrow_date, due_date, return_date, status, penalty_fee) VALUES
(1, 1, '2024-02-15', '2024-03-01', NULL, 'Borrowed', 0.00),
(2, 2, '2024-02-10', '2024-02-24', NULL, 'Overdue', 50.00),
(3, 3, '2024-02-01', '2024-02-15', '2024-02-14', 'Returned', 0.00);
