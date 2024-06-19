from flask import Flask, render_template, Blueprint, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from forms import *
from models import *

user = Blueprint("user", __name__, template_folder = "templates/user")

def groups_of(n, l):
  groups = []
  for i in range(0, len(l), n):
    groups.append(l[i:i+n])
  return groups

@user.context_processor
def user_base():
    form = SearchForm()
    return dict(form = form)

@user.route("/", methods = ['GET'])
def home():
    if current_user.is_authenticated and current_user.role == 'admin':
        flash("Admins are not allowed to access this page, you have been redirected to the admin home")
        return redirect(url_for('admin.home'))
    books1 = Books.query.all()[:4]
    books2 = Books.query.all()[4:8]
    return render_template("user/user-home.html", books1 = books1, books2 = books2)

@user.route("/login/", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated: 
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
        else:
            flash("You are already logged in")
            return redirect(url_for('user.home'))

    form = UserLoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if not user:
            flash("A user with this email does not exist")
            return render_template("user/user-login.html", form = form)
        if not check_password_hash(user.password_hash, form.password.data):
            flash("You've entered the incorrect password")
            return render_template("user/user-login.html", form = form)
        login_user(user)
        flash("Successfully Logged In")
        return redirect(url_for('user.home'))
    return render_template("user/user-login.html", form = form)

@user.route("/register/", methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated: 
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
        else:
            flash("Please logout before creating a new account")
            return redirect(url_for('user.home'))

    form = UserRegistrationForm()
    if form.validate_on_submit():
        if Users.query.filter_by(email = form.email.data).first():
            flash("This email already exists. Please enter a different one")
            return render_template("user/user-register.html", form = form)
        
        if form.password.data != form.confirm_password.data:
            flash("The passwords do not match")
            return render_template("user/user-register.html", form = form)
        
        new_user = Users(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password_hash = generate_password_hash(form.password.data),
            role = 'user'
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember = True)
        flash("Successfully Registered")
        return redirect(url_for('user.home'))
    return render_template("user/user-register.html", form = form)

@user.route("/search/", methods = ['GET', 'POST'])
def search():
    if current_user.is_authenticated and current_user.role == 'admin':
        flash("Admins are not allowed to access this page, you have been redirected to the admin home")
        return redirect(url_for('admin.home'))
    
    form = SearchForm()
    if form.validate_on_submit():
        searched = form.searched.data.lower()
        books = groups_of(4, Books.query.filter(Books.name.contains(searched)).all())
        genres = groups_of(4, Genres.query.filter(Genres.name.contains(searched)).all())
        books_by_author = groups_of(4, Books.query.filter(Books.author.contains(searched)).all())
        return render_template("search.html", searched = searched, form = form, books = books, genres = genres, books_by_author = books_by_author)

@user.route("/browse/genres", methods = ['GET', 'POST'])
def browse_genres():
    if current_user.is_authenticated and current_user.role == 'admin':
        flash("Admins are not allowed to access this page, you have been redirected to the admin home")
        return redirect(url_for('admin.home'))

    genres = Genres.query.all()
    rows = groups_of(4, genres)
    return render_template("browse-genres.html", rows = rows)

@user.route("/browse/genres/<genre_id>/", methods = ['GET', 'POST'])
def browse_books(genre_id):
    if current_user.is_authenticated and current_user.role == 'admin':
        flash("Admins are not allowed to access this page, you have been redirected to the admin home")
        return redirect(url_for('admin.home'))

    genre = Genres.query.filter_by(id = genre_id).first()
    if not genre:
        flash("This genre does not exist")
        return redirect (url_for('user.browse_genres'))
    books = genre.books
    rows = groups_of(4, books)
    return render_template("browse-books.html", genre = genre, rows = rows)

@user.route("/books/<book_id>/", methods = ['GET', 'POST'])
def view_book(book_id):
    if current_user.is_authenticated: 
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect(url_for('user.login'))

    form = BookReviewForm()
    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("This book does not exist")
        return redirect(url_for('user.home'))

    genre = Genres.query.filter_by(id = book.genre).first()
    already_borrowed = Borrowings.query.filter_by(user_id = current_user.id, book_id = book.id).first()
    already_purchased = Purchases.query.filter_by(user_id = current_user.id, book_id = book.id).first()
    
    review_details = []
    for review in book.reviews:
        content = review.content
        user = Users.query.filter_by(id = review.user_id).first()
        review_details.append((user, content))
    
    if form.validate_on_submit():
        new_review = Reviews(
            content = form.review.data,
            user_id = current_user.id,
            book_id = book.id
        )
        db.session.add(new_review)
        db.session.commit()
        flash("Your review has been posted")
        return redirect(url_for('user.view_book', book_id = book.id))
    return render_template("view-book.html", book = book, genre = genre, form = form, review_details = review_details, already_borrowed = already_borrowed, already_purchased = already_purchased)

@user.route("/books/<book_id>/borrow/", methods = ['GET', 'POST'])
def borrow_book(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect('user.login')
    
    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("This book does not exist")
        return redirect(url_for('user.home'))
    
    already_requested = Requests.query.filter_by(user_id = current_user.id, book_id = book.id).first()
    if already_requested:
        flash("You have already requested this book")
        return redirect(url_for('user.home'))
    
    user_borrowings = Borrowings.query.filter_by(user_id = current_user.id).all()
    if len(user_borrowings) >= 5:
        flash("You can borrow only 5 books at a time")
        return redirect(url_for('user.home'))
    
    new_request = Requests(
        user_id = current_user.id,
        book_id = book.id,
    )
    db.session.add(new_request)
    db.session.commit()
    flash("Your request has been sent, you will be able to read the book once an admin approves it")
    return redirect(url_for('user.home'))

@user.route("/books/<book_id>/return/", methods = ['GET', 'POST'])
def return_book(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect('user.login')
    
    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("This book does not exist")
        return redirect(url_for('user.home'))
    
    borrowing = Borrowings.query.filter_by(user_id = current_user.id, book_id = book.id).first()
    if not borrowing:
        flash("You have not borrowed this book")
        return redirect(url_for('user.home'))
    
    new_return = PastBorrowings(
        book_name = book.name,
        genre = Genres.query.filter_by(id = book.genre).first().name
    )

    db.session.add(new_return)
    db.session.delete(borrowing)
    db.session.commit()
    flash("You have successfully returned the book")
    return redirect(url_for('user.home'))

@user.route("/books/<book_id>/read/", methods = ['GET', 'POST'])
def read_book(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect('user.login')
    
    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("This book does not exist")
        return redirect(url_for('user.home'))
    
    borrowed = Borrowings.query.filter_by(user_id = current_user.id, book_id = book.id).first()
    purchased = Purchases.query.filter_by(user_id = current_user.id, book_id = book.id).first()
    if not (borrowed or purchased):
        flash("You have not borrowed or purchased this book")
        return redirect(url_for('user.home'))
    return render_template("read-book.html", book = book)

@user.route("/books/<book_id>/payment/", methods = ['GET', 'POST'])
def payment(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect('user.login')


    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("This book does not exist")
        return redirect(url_for('user.home'))

    return render_template("payment.html", book = book)

@user.route("/books/<book_id>/confirm-payment", methods = ['GET', 'POST'])
def confirm_payment(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect(url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect('user.login')
    
    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("This book does not exist")
        return redirect(url_for('user.home'))
    
    new_purchase = Purchases(
        user_id = current_user.id,
        book_id = book.id
    )
    db.session.add(new_purchase)
    db.session.commit()
    flash("You have successfully purchased the book, you can now read it")
    return redirect(url_for('user.home'))

@user.route("/<user_id>/profile/", methods = ['GET', 'POST'])
def user_profile(user_id):
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            flash("Admins are not allowed to access this page, you have been redirected to the admin home")
            return redirect (url_for('admin.home'))
    else:
        flash("You must login to access this page")
        return redirect(url_for('user.login'))

    user = Users.query.filter_by(id = user_id).first()
    if not user:
        flash("This user does not exist")
        return redirect(url_for('user.home'))
    
    borrowings = []
    for borrowing in user.current_borrowings:
        book = Books.query.filter_by(id = borrowing.book_id).first()
        borrowings.append(book)
    
    purchases = []
    for purchase in user.purchases:
        book = Books.query.filter_by(id = purchase.book_id).first()
        purchases.append(book)
    return render_template("user-profile.html", user = user, borrowings = borrowings, purchases = purchases)

@user.route("/logout/", methods = ['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have successfully logged out")
    return redirect(url_for('user.home'))
    