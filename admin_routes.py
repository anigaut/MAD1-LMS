from flask import Flask, render_template, Blueprint, request, redirect, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from forms import *
from models import *
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from collections import Counter


admin = Blueprint("admin", __name__, template_folder = "templates/admin")

@admin.route("/admin/", methods = ['GET','POST'])
def home():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    return render_template("admin/admin-home.html")
    
@admin.route("/admin/register/", methods = ['GET','POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
        else:
            return redirect(url_for('admin.home'))
    form = AdminRegisterForm()
    if form.validate_on_submit():
        if form.email.data[-9:] != "@opus.com":
            flash("Your Email Address Must End With '@opus.com'")
            return render_template("admin/admin-register.html", form = form)

        if Users.query.filter_by(email = form.email.data).first():
            flash("An Admin with this Email already Exists, Please enter a different one")
            return render_template("admin/admin-register.html", form = form)
        
        if form.password.data != form.confirm_password.data:
            flash("The passwords do not match")
            return render_template("admin/admin-register.html", form = form)
        
        new_admin = Users(
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            password_hash = generate_password_hash(form.password.data),
            role = 'admin'
        )

        db.session.add(new_admin)
        db.session.commit()
        login_user(new_admin, remember = True)
        flash("Successfully Registered as Admin")
        return redirect(url_for('admin.home'))
    return render_template("admin/admin-register.html", form = form)

@admin.route("/admin/login/", methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
        else:
            return redirect(url_for('admin.home'))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if not user:
            flash("An Admin with this email does not exist")
            return render_template("admin/admin-login.html", form = form)
        
        if form.email.data[-9:] != "@opus.com":
            flash("Your Email Address Must End With '@opus.com'")
            return render_template("admin/admin-login.html", form = form) 

        if not check_password_hash(user.password_hash, form.password.data):
            flash("You've entered the incorrect password")
            return render_template("admin/admin-login.html", form = form)
        login_user(user, remember = True)
        flash("Successfully Logged in as Admin")
        return redirect(url_for('admin.home'))
    return render_template("admin/admin-login.html", form = form)

@admin.route("/admin/books/", methods = ['GET', 'POST'])
def manage_books():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))

    books = Books.query.all()
    return render_template("admin/manage-books.html", books = books)

@admin.route("/admin/books/add/", methods = ['GET', 'POST'])
def add_book():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))

    form = AddBookForm()
    if form.validate_on_submit():
        book_exists = Books.query.filter_by(name = form.name.data).first()
        if book_exists:
            flash("A book with this name already exists")
            return render_template("admin/add-book.html", form = form)
        genre = Genres.query.filter_by(name = form.genre.data).first()
        if not genre:
            flash("This Genre does not exist")
            return render_template("admin/add-book.html", form = form)

        filename = secure_filename(form.file.data.filename)
        file_path = os.path.join("static/books", filename)
        form.file.data.save(file_path)

        cover_pic_filename = secure_filename(form.cover_pic.data.filename)
        cover_pic_path = os.path.join("static/covers", cover_pic_filename)
        form.cover_pic.data.save(cover_pic_path)

        new_book = Books(
            name = form.name.data,
            author = form.author.data,
            genre = genre.id,
            description = form.description.data,
            price = form.price.data,
            file = filename,
            cover_pic = cover_pic_filename
        )
        
        db.session.add(new_book)
        db.session.commit()
        flash("Successfully Added Book")
        return redirect(url_for('admin.manage_books'))
    return render_template("admin/add-book.html", form = form)

@admin.route("/admin/books/edit/<int:book_id>/", methods = ['GET', 'POST'])
def edit_book(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    form = EditBookForm()

    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("Book with this ID does not exist")
        return redirect(url_for('admin.manage_books'))

    if form.validate_on_submit():
        genre = Genres.query.filter_by(name = form.genre.data).first()
        if not genre:
            flash("This Genre does not exist")
            return render_template("admin/edit-book.html", form = form, book = book)
        
        book.name = form.name.data
        book.author = form.author.data
        book.genre = genre.id
        book.price = form.price.data
        book.description = form.description.data

        db.session.commit()
        flash("Successfully Edited Book")
        return redirect(url_for('admin.manage_books'))
    return render_template("admin/edit-book.html", form = form, book = book)
    
@admin.route("/admin/books/delete/<int:book_id>/", methods = ['GET', 'POST'])
def delete_book(book_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    book = Books.query.filter_by(id = book_id).first()
    if not book:
        flash("Book with this ID does not exist")
        return redirect(url_for('admin.manage_books'))
    
    reviews = Reviews.query.filter_by(book_id = book_id).all()
    for review in reviews:
        db.session.delete(review)
    
    borrowings = Borrowings.query.filter_by(book_id = book_id).all()
    for borrowing in borrowings:
        db.session.delete(borrowing)
    
    purchases = Purchases.query.filter_by(book_id = book_id).all()
    for purchase in purchases:
        db.session.delete(purchase)
    
    requests = Requests.query.filter_by(book_id = book_id).all()
    for request in requests:
        db.session.delete(request)

    file_path = os.path.join("static/books", book.file)
    cover_pic_path = os.path.join("static/covers", book.cover_pic)
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(cover_pic_path):
        os.remove(cover_pic_path)

    db.session.delete(book)
    db.session.commit()
    flash("Successfully Deleted Book")
    return redirect(url_for('admin.manage_books'))

@admin.route("/admin/genres/", methods = ['GET', 'POST'])
def manage_genres():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    genres = Genres.query.all()
    return render_template("admin/manage-genres.html", genres = genres)

@admin.route("/admin/genres/add/", methods = ['GET', 'POST'])
def add_genre():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))

    form = AddGenreForm()
    if form.validate_on_submit():
        genre_exists = Genres.query.filter_by(name = form.name.data).first()
        if genre_exists:
            flash("A genre with this name already exists")
            return render_template("admin/add-genre.html", form = form)
        
        new_genre = Genres(
            name = form.name.data,
            description = form.description.data,
            date_added = datetime.now()
        )

        db.session.add(new_genre)
        db.session.commit()
        flash("Successfully Added Genre")
        return redirect(url_for('admin.manage_genres'))
    return render_template("admin/add-genre.html", form = form)

@admin.route("/admin/genres/edit/<int:genre_id>/", methods = ['GET', 'POST'])
def edit_genre(genre_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))

    form = EditGenreForm()
    genre = Genres.query.filter_by(id = genre_id).first()
    if not genre:
        flash("Genre with this ID does not exist")
        return redirect(url_for('admin.manage_genres'))
    if form.validate_on_submit():
        genre.name = form.name.data
        genre.description = form.description.data
        db.session.commit()
        flash("Successfully Edited Genre")
        return redirect(url_for('admin.manage_genres'))
    return render_template("admin/edit-genre.html", form = form, genre = genre)

@admin.route("/admin/genres/delete/<int:genre_id>/", methods = ['GET', 'POST'])
def delete_genre(genre_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    genre = Genres.query.filter_by(id = genre_id).first()
    if not genre:
        flash("Genre with this ID does not exist")
        return redirect(url_for('admin.manage_genres'))
    if genre.books:
        flash("This genre has books associated with it. Please delete those books first")
        return redirect(url_for('admin.manage_genres'))

    db.session.delete(genre)
    db.session.commit()
    flash("Successfully Deleted Genre")
    return redirect(url_for('admin.manage_genres'))

@admin.route("/admin/pending-requests/", methods = ['GET', 'POST'])
def pending_requests():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))

    pending_requests = Requests.query.all()
    return render_template("admin/pending-requests.html", pending_requests = pending_requests)

@admin.route("/admin/pending-requests/<int:book_id>/<int:user_id>/approve/", methods = ['GET', 'POST'])
def approve_request(book_id, user_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    request = Requests.query.filter_by(book_id = book_id, user_id = user_id).first()
    if not request:
        flash("Request with these credentials does not exist")
        return redirect(url_for('admin.pending_requests'))
    
    new_borrowing = Borrowings(
        user_id = user_id,
        book_id = book_id,
        time = datetime.now()
    )

    db.session.add(new_borrowing)
    db.session.delete(request)
    db.session.commit()
    flash("Successfully Approved Request")
    return redirect(url_for('admin.pending_requests'))

@admin.route("/admin/pending-requests/<int:book_id>/<int:user_id>/reject/", methods = ['GET', 'POST'])
def reject_request(book_id, user_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    request = Requests.query.filter_by(book_id = book_id, user_id = user_id).first()
    if not request:
        flash("Request with these credentials does not exist")
        return redirect(url_for('admin.pending_requests'))
    
    db.session.delete(request)
    db.session.commit()
    flash("Successfully Rejected Request")
    return redirect(url_for('admin.pending_requests'))

@admin.route("/admin/current-borrowings/", methods = ['GET', 'POST'])
def current_borrowings():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    borrowings = []
    for borrowing in Borrowings.query.all():
        expiry = borrowing.time + timedelta(days = 7)
        expired = False
        if expiry < datetime.now():
            expired = True  
        borrowings.append((borrowing.id, borrowing.book_id, borrowing.user_id, borrowing.time, expired))
    return render_template("admin/current-borrowings.html", borrowings = borrowings)

@admin.route("/admin/current-borrowings/<int:borrowing_id>/revoke/", methods = ['GET', 'POST'])
def revoke_access(borrowing_id):
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))

    borrowing = Borrowings.query.filter_by(id = borrowing_id).first()
    if not borrowing:
        flash("Borrowing with this ID does not exist")
        return redirect(url_for('admin.current_borrowings'))
    
    new_return = PastBorrowings(
        book_name = Books.query.filter_by(id = borrowing.book_id).first().name,
        genre = Genres.query.filter_by(id = Books.query.filter_by(id = borrowing.book_id).first().genre).first().name
    )
    
    db.session.add(new_return)
    db.session.delete(borrowing)
    db.session.commit()
    flash("Successfully Revoked Access")
    return redirect(url_for('admin.current_borrowings'))   

@admin.route("/admin/stats/", methods = ['GET', 'POST'])
def stats():
    if current_user.is_authenticated:
        if current_user.role == 'user':
            flash("You must be an admin to access this page")
            return redirect(url_for('user.home'))
    else:
        return redirect(url_for('admin.login'))
    
    books = []
    genres = []
    for borrowing in PastBorrowings.query.all():
        books.append(borrowing.book_name)
        genres.append(borrowing.genre)
    genre_counts = Counter(genres)
    genre_labels = genre_counts.keys()
    genre_sizes = genre_counts.values()

    plt.clf()
    plt.hist(books)
    plt.title("Borrow Counts of Books")
    plt.savefig("static/stats/books_hist.png")

    plt.clf()
    plt.pie(genre_sizes, labels = genre_labels)
    plt.title("Genre Distribution")
    plt.savefig("static/stats/genres_pie.png")

    return render_template("admin/stats.html")
    
@admin.route("/admin/logout/")
@login_required
def logout():
    logout_user()
    flash("You've been logged out")
    return redirect(url_for('admin.home'))