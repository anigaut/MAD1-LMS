from flask import Flask
from flask_login import LoginManager
from admin_routes import admin
from user_routes import user
from flask_migrate import Migrate
from models import *
import os
from resources import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///LMS_database.sqlite3"
app.config['SECRET_KEY'] = os.urandom(24)
db.init_app(app)
api.init_app(app)
app.app_context().push()
migrate = Migrate(app, db)

app.register_blueprint(user)
app.register_blueprint(admin)

app.config['UPLOAD_FOLDER'] = 'static/covers'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
    
if __name__ == "__main__":
    app.run(debug = True)
