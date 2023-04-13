from flask import Flask
from config import Config
from .models import db # new with forms
from flask_migrate import Migrate # new with forms

app = Flask(__name__)
app.config.from_object(Config)  

# new section with forms
migrate = Migrate(app,db)
db.init_app(app) 

from . import routes
from . import models # new with forms