# Flask Library Management System

A comprehensive web-based library management system built with Flask, SQLAlchemy, and Bootstrap. This application provides complete functionality for managing books, members, borrowing/returning operations, and generating reports.

## Features

### 📚 Book Management
- Add, edit, and delete books
- Track book stock and availability
- Search books by title or author
- Import books from Frappe Library API
- View detailed book information (ISBN, author, stock)

### 👥 Member Management
- Add, edit, and delete members
- Track member borrowing history
- Manage member dues and payments
- Unique member names and phone numbers

### 🔄 Borrowing & Returning System
- Borrow books with automatic stock deduction
- Return books with payment processing
- Automatic dues calculation (Rs. 100 per borrow)
- Member borrowing limits (max Rs. 500 outstanding)
- Real-time availability checking

### 📊 Reports & Analytics
- Popular books ranking (most borrowed)
- Top paying members
- Library statistics (total books, members)
- Visual charts for data visualization

### 💰 Transaction Tracking
- Complete transaction history
- Borrow and return records
- Payment tracking
- Date-stamped operations

## Tech Stack

- **Backend**: Flask 3.1.1
- **Database**: SQLAlchemy 2.0.40 (SQLite by default)
- **Frontend**: Bootstrap, Jinja2 templates
- **Forms**: Flask-WTF, WTForms
- **API Integration**: Requests for Frappe Library import
- **Deployment**: Gunicorn ready

## Project Structure

```
.
├── app.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── Procfile                  # Heroku deployment config
├── instance/
│   └── library.db           # SQLite database
├── library/
│   ├── __init__.py          # Flask app initialization
│   ├── models.py            # Database models (Book, Member, Transaction)
│   ├── forms.py             # WTForms definitions
│   ├── routes/
│   │   └── routes.py        # All application routes
│   ├── static/
│   │   ├── style.css        # Custom CSS
│   │   └── app.js           # JavaScript functionality
│   └── templates/
│       ├── base.html        # Base template
│       ├── home.html        # Dashboard
│       ├── reports.html     # Analytics page
│       ├── books/           # Book management templates
│       ├── members/         # Member management templates
│       └── transactions/    # Transaction templates
```

## Database Models

### Book
- `id` (Primary Key)
- `title` (String, required)
- `isbn` (String, required)
- `author` (String, required)
- `stock` (Integer, default: 0)
- `borrow_stock` (Integer, available for borrowing)
- `member_count` (Integer, times borrowed)
- `returned` (Boolean, default: False)

### Member
- `id` (Primary Key)
- `name` (String, required)
- `member_name` (String, required, unique)
- `phone_number` (String, required, unique)
- `to_pay` (Integer, outstanding dues)
- `total_paid` (Integer, total payments)
- `borrowed` (Relationship to Book)

### Transaction
- `id` (Primary Key)
- `book_name` (String)
- `member_name` (String)
- `type_of_transaction` (String, 'borrow' or 'return')
- `date` (Date)
- `amount` (Integer)

### Book_borrowed (Join Table)
- `id` (Primary Key)
- `member` (Foreign Key to Member)
- `book` (Foreign Key to Book)

## Installation & Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python app.py
   ```

3. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

The database is automatically created when you first run the application.

## Usage Guide

### Adding Books
1. Navigate to Books page
2. Click "Add Book" button
3. Fill in book details (title, ISBN, author, stock)
4. Submit the form

### Adding Members
1. Navigate to Members page
2. Click "Add Member" button
3. Fill in member details (name, member name, phone number)
4. Submit the form

### Borrowing a Book
1. From the homepage, select a book from "Books to Borrow"
2. Select a member from "Members who can borrow"
3. Click "Borrow" button
4. System automatically:
   - Deducts from available stock
   - Adds Rs. 100 to member's dues
   - Creates a transaction record

### Returning a Book
1. From the homepage, select a book from "Books to Return"
2. Select the member who borrowed it
3. Check "Paid" checkbox if paying dues
4. Click "Return" button
5. System automatically:
   - Returns book to stock
   - Clears member's dues if paid
   - Creates a transaction record

### Importing Books from Frappe
1. Navigate to Books page
2. Enter a book title in the import section
3. Click "Import" button
4. System fetches books from Frappe Library API and adds them

