from flask import Flask
from config import Config
from .models import db, User # new with forms
from flask_migrate import Migrate # new with forms
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)  

# new section with forms
migrate = Migrate(app,db)
db.init_app(app) 

login_manager = LoginManager(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
    
# this will take you to the loginpage if you try to go to a route
login_manager.login_view = 'login_page' 

from . import routes
from . import models # new with forms