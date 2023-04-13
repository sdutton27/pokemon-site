from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Pokemon(db.Model):
    name = db.Column(db.String(30), primary_key=True, nullable=False)
    base_hp = db.Column(db.Integer, nullable=False)
    base_defense = db.Column(db.Integer, nullable=False)
    base_attack = db.Column(db.Integer, nullable=False)
    front_shiny_sprite = db.Column(db.String, nullable=False, unique=True)
    abilities = db.Column(db.String(100), nullable=False) # multiple abilities

    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable = True)

    def __init__(self, name, base_hp, base_defense, base_attack, front_shiny_sprite, abilities):
        self.name = name
        self.base_hp = base_hp
        self.base_defense = base_defense
        self.base_attack = base_attack
        self.front_shiny_sprite = front_shiny_sprite
        self.abilities = abilities

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

# this name is actually lowercase
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    profile_pic = db.Column(db.String, nullable=True)
    
    pokemon = db.relationship('Pokemon', backref='trainer', lazy = True)

    def __init__(self, first_name, last_name, email, password, profile_pic=''):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email
        self.password = password

        self.profile_pic = profile_pic

    def save_to_db(self):
        db.session.add(self)
        db.session.commit() # actually commits things
