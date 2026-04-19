from library.forms import book_form, member_form
from library import app, db
from library.models import Book, Member, Transaction, Book_borrowed

import requests
import json
from datetime import date
from flask import render_template, redirect, url_for, flash, request, jsonify
from sqlalchemy import desc


def get_borrow_context():
    """Helper to get common borrow/return context variables."""
    return {
        'books_to_borrow': Book.query.filter(Book.borrow_stock > 0).all(),
        'members_can_borrow': Member.query.filter(Member.to_pay < 500).all(),
        'books_to_return': Book.query.filter(Book.borrower).all(),
    }


# Home
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', endpoint='home_page')
def home_page():
    ctx = get_borrow_context()
    return render_template('home.html',
                           member_form=member_form(),
                           book_form=book_form(),
                           book=False,
                           **ctx)


# Reports
@app.route('/reports', methods=['GET', 'POST'])
def report_page():
    books = Book.query.all()
    members = Member.query.all()

    popular_books = Book.query.order_by(desc(Book.member_count)).limit(10).all()
    most_paying_members = Member.query.order_by(desc(Member.total_paid)).limit(10).all()

    popular_books_title = [b.title[0:20] for b in popular_books if b.member_count > 0]
    books_count = [b.member_count for b in popular_books if b.member_count > 0]
    member_paying_most = [m.member_name for m in most_paying_members if m.total_paid > 0]
    member_paid = [m.total_paid for m in most_paying_members if m.total_paid > 0]

    return render_template('reports.html',
                           members=len(members),
                           books=len(books),
                           member_paid=json.dumps(member_paid),
                           book_title=json.dumps(popular_books_title),
                           members_name=json.dumps(member_paying_most),
                           book_count=json.dumps(books_count))


# Books list
@app.route('/books', methods=['GET', 'POST'], endpoint='books_page')
def books_page():
    ctx = get_borrow_context()
    if request.method == 'POST':
        form = book_form()
        if form.validate_on_submit():
            new_book = Book(
                title=form.title.data,
                isbn=form.isbn.data,
                author=form.author.data,
                stock=form.stock.data,
                borrow_stock=form.stock.data
            )
            db.session.add(new_book)
            db.session.commit()
            flash('Book created successfully!', 'success')
        else:
            flash('Error creating book.', 'danger')
        return redirect(url_for('books_page'))

    books = Book.query.all()
    return render_template('books/books.html',
                           books=books,
                           length=len(books),
                           book_form=book_form(),
                           member_form=member_form(),
                           book=False,
                           **ctx)


# Delete book
@app.route('/delete-book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted.', 'success')
    return redirect(url_for('books_page'))


# Update book
@app.route('/update-book/<int:book_id>', methods=['POST'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    form = book_form()
    if form.validate_on_submit():
        book.title = form.title.data
        book.isbn = form.isbn.data
        book.author = form.author.data
        book.stock = form.stock.data
        book.borrow_stock = form.stock.data
        db.session.commit()
        flash('Book updated.', 'success')
    return redirect(url_for('books_page'))


# Members list
@app.route('/members', methods=['GET', 'POST'], endpoint='members_page')
def members_page():
    ctx = get_borrow_context()
    if request.method == 'POST':
        form = member_form()
        if form.validate_on_submit():
            new_member = Member(
                name=form.name.data,
                member_name=form.member_name.data,
                phone_number=form.phone_number.data
            )
            db.session.add(new_member)
            db.session.commit()
            flash('Member created successfully!', 'success')
        else:
            flash('Error creating member.', 'danger')
        return redirect(url_for('members_page'))

    members = Member.query.all()
    return render_template('members/members.html',
                           members=members,
                           length=len(members),
                           member_form=member_form(),
                           book_form=book_form(),
                           book=False,
                           **ctx)


# Delete member
@app.route('/delete-member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted.', 'success')
    return redirect(url_for('members_page'))


# Update member
@app.route('/update-member/<int:member_id>', methods=['POST'])
def update_member(member_id):
    member = Member.query.get_or_404(member_id)
    form = member_form()
    if form.validate_on_submit():
        member.name = form.name.data
        member.member_name = form.member_name.data
        member.phone_number = form.phone_number.data
        db.session.commit()
        flash('Member updated.', 'success')
    return redirect(url_for('members_page'))


# Transactions list
@app.route('/transactions', methods=['GET'], endpoint='transactions_page')
def transactions_page():
    ctx = get_borrow_context()
    transactions = Transaction.query.order_by(desc(Transaction.id)).all()
    return render_template('transactions/transactions.html',
                           transactions=transactions,
                           length=len(transactions),
                           book_form=book_form(),
                           member_form=member_form(),
                           book=False,
                           **ctx)


# Borrow book
@app.route('/borrow-book', methods=['POST'])
def borrow_book():
    book_id = request.form.get('book_name')
    member_id = request.form.get('member_name')

    book = Book.query.get(book_id)
    member = Member.query.get(member_id)

    if not book or not member:
        flash('Invalid book or member.', 'danger')
        return redirect(url_for('home_page'))

    if book.borrow_stock <= 0:
        flash('Book not available for borrowing.', 'danger')
        return redirect(url_for('home_page'))

    if member.to_pay >= 500:
        flash('Member has outstanding dues over Rs.500.', 'danger')
        return redirect(url_for('home_page'))

    book.borrow_stock -= 1
    book.member_count += 1
    member.to_pay += 100

    borrow_record = Book_borrowed(member=member.id, book=book.id)
    db.session.add(borrow_record)

    transaction = Transaction(
        book_name=book.title,
        member_name=member.member_name,
        type_of_transaction='borrow',
        date=date.today(),
        amount=0
    )
    db.session.add(transaction)
    db.session.commit()
    flash(f'"{book.title}" borrowed by {member.member_name}.', 'success')
    return redirect(url_for('home_page'))


# Return book
@app.route('/return-book', methods=['POST'])
def return_book():
    book_id = request.form.get('book_name')
    member_id = request.form.get('member_name')
    paid = request.form.get('paid')

    book = Book.query.get(book_id)
    member = Member.query.get(member_id)

    if not book or not member:
        flash('Invalid book or member.', 'danger')
        return redirect(url_for('home_page'))

    book.borrow_stock += 1
    amount_paid = 0

    if paid:
        amount_paid = member.to_pay
        member.total_paid += amount_paid
        member.to_pay = 0

    borrow_record = Book_borrowed.query.filter_by(book=book.id, member=member.id).first()
    if borrow_record:
        db.session.delete(borrow_record)

    transaction = Transaction(
        book_name=book.title,
        member_name=member.member_name,
        type_of_transaction='return',
        date=date.today(),
        amount=amount_paid
    )
    db.session.add(transaction)
    db.session.commit()
    flash(f'"{book.title}" returned by {member.member_name}.', 'success')
    return redirect(url_for('home_page'))


# API: get members who borrowed a book (for return modal JS)
@app.route('/book/<int:book_id>', methods=['GET'])
def get_book_members(book_id):
    records = Book_borrowed.query.filter_by(book=book_id).all()
    members = []
    for r in records:
        m = Member.query.get(r.member)
        if m:
            members.append({'id': m.id, 'member_name': m.member_name})
    return jsonify({'members': members})


# Search
@app.route('/search', methods=['POST'])
def search_page():
    query = request.form.get('query', '')
    books = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) | (Book.author.ilike(f'%{query}%'))
    ).all()
    return render_template('books/search_page.html', books=books, length=len(books))


# Import from Frappe
@app.route('/import-from-frappe', methods=['POST'])
def import_from_frappe():
    title = request.form.get('title', '')
    try:
        response = requests.get(
            'https://frappe.io/api/method/frappe-library',
            params={'title': title, 'page': 1}
        )
        data = response.json().get('message', [])
        for item in data:
            existing = Book.query.filter_by(isbn=item.get('isbn', '')).first()
            if not existing:
                book = Book(
                    title=item.get('title', ''),
                    isbn=item.get('isbn', ''),
                    author=item.get('authors', ''),
                    stock=1,
                    borrow_stock=1
                )
                db.session.add(book)
        db.session.commit()
        flash('Books imported successfully!', 'success')
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'danger')
    return redirect(url_for('books_page'))
