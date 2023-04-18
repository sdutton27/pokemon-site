from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class Pokemon(db.Model):
    #name = db.Column(db.String(30), primary_key=True, nullable=False)
    pokemon_name = db.Column(db.String(30), primary_key=True, nullable=False)
    base_hp = db.Column(db.Integer, nullable=False)
    base_defense = db.Column(db.Integer, nullable=False)
    base_attack = db.Column(db.Integer, nullable=False)
    front_shiny_sprite = db.Column(db.String, nullable=False, unique=True)
    abilities = db.Column(db.ARRAY(db.String(20)), nullable=False) # multiple abilities
    types = db.Column(db.ARRAY(db.String(20)), nullable=True) # multiple types, keeping nullable True 

    #trainer_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = True)

    # will delete a pokemon/user relationship if that pokemon is deleted
    trainer = db.relationship('PokemonCaughtBy', cascade='all,delete',backref='pokemon_caught', lazy = True)

    def __init__(self, name, base_hp, base_defense, base_attack, front_shiny_sprite, abilities, types):
        self.pokemon_name = name
        self.base_hp = base_hp
        self.base_defense = base_defense
        self.base_attack = base_attack
        self.front_shiny_sprite = front_shiny_sprite
        self.abilities = abilities
        self.types = types

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    # We might just be able to use save_to_db()
    #def update_user(self, user_id):
        #db.session.add(self)
        #db.session.commit()

# this name is actually lowercase
class User(db.Model, UserMixin):
    #id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    date_created = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)
    profile_pic = db.Column(db.String, nullable=True)
    
    bio = db.Column(db.String(100), nullable=True)

    color = db.Column(db.Text, nullable=True)

    # will delete a pokemon that belongs to a user if that user is deleted
    pokemon_caught = db.relationship('PokemonCaughtBy', cascade='all,delete',backref='trainer', lazy = True)

    def __init__(self, first_name, last_name, email, password, profile_pic=''):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email
        self.password = password

        self.profile_pic = profile_pic

        self.color = "#ffffff"

    def save_to_db(self):
        db.session.add(self)
        db.session.commit() # actually commits things

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_changes_to_db(self):
        db.session.commit()

    def get_id(self):
        return self.user_id    

class PokemonCaughtBy(db.Model):
    __tablename__ = "pokemon_caught_by"

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False, primary_key=True)
    pokemon_name = db.Column(db.String(30), db.ForeignKey('pokemon.pokemon_name'), nullable=False, primary_key=True)

    def __init__(self, user_id, pokemon_name):
        self.user_id = user_id
        self.pokemon_name = pokemon_name

    def save_to_db(self):
        db.session.add(self)
        db.session.commit() # actually commits things

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
    # @property
    # def serialized(self):
    #     """Return object data in serializeable format"""
    #     return {
    #         'user_id': self.user_id,
    #         'pokemon_name': self.pokemon_name
    # }

    def get_session():
        return db.session