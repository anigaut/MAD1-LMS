from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SubmitField, BooleanField, FileField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Email
from models import Users, Genres

class UserRegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators = [DataRequired()])
    last_name = StringField("Last Name")
    email = EmailField("Email", validators = [DataRequired(), Email()], render_kw = {"placeholder":"username@example.com"})
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired()])
    submit = SubmitField("Register")

    def validate_user(self, email):
        user = Users.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("A user with this email already exists. Please choose a different one")
    
    def validate_passwords(self, password, confirm_password):
        if password.data != confirm_password.data:
            raise ValidationError("The passwords do not match")

class UserLoginForm(FlaskForm):
    email = EmailField("Email", validators = [DataRequired()])
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Login")

class AdminRegisterForm(FlaskForm):
    first_name = StringField("First Name", validators = [DataRequired()])
    last_name = StringField("Last Name")
    email = EmailField(
        "Username for Email (Please fill this out as 'username@opus.com')",          
        validators = [DataRequired(), Email()], render_kw = {"placeholder":"username@opus.com"})
    password = PasswordField("Password", validators = [DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators = [DataRequired()])
    submit = SubmitField("Register")
    
class AdminLoginForm(FlaskForm):
    email = EmailField("Opus Email ID", validators = [DataRequired()], render_kw = {"placeholder":"username@opus.com"})
    password = PasswordField("Password", validators = [DataRequired()])
    submit = SubmitField("Login")

class AddBookForm(FlaskForm):
    name = StringField("Book Name", validators = [DataRequired()])
    author = StringField("Author", validators = [DataRequired()])
    genre = StringField("Genre", validators = [DataRequired()])
    description = TextAreaField("Description")
    price = IntegerField("Price (in INR)", validators = [DataRequired()])
    file = FileField("Book File", validators = [DataRequired()])
    cover_pic = FileField("Cover Picture", validators = [DataRequired()])
    submit = SubmitField("Add Book")

class EditBookForm(FlaskForm):
    name = StringField("Book Name")
    author = StringField("Author")
    genre = StringField("Genre")
    price = IntegerField("Price (in INR)")
    description = TextAreaField("Description")
    submit = SubmitField("Submit Edit")

class AddGenreForm(FlaskForm):
    name = StringField("Genre Name", validators = [DataRequired()])
    description = StringField("Description")
    submit = SubmitField("Add Genre")

class EditGenreForm(FlaskForm):
    name = StringField("Genre Name", validators = [DataRequired()])
    description = StringField("Description")
    submit = SubmitField("Submit Edit")

class SearchForm(FlaskForm):
    searched = StringField("Search by Book, Genre or Author", validators = [DataRequired()])
    submit = SubmitField("Search")

class BookReviewForm(FlaskForm):
    review = TextAreaField("Review", validators = [DataRequired()])
    submit = SubmitField("Submit Review")




