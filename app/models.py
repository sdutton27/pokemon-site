from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pokemon(db.Model):
    name = db.Column(db.String(30), primary_key=True, nullable=False)
    base_hp = db.Column(db.Integer, nullable=False)
    base_defense = db.Column(db.Integer, nullable=False)
    base_attack = db.Column(db.Integer, nullable=False)
    front_shiny_sprite = db.Column(db.String, nullable=False, unique=True)
    abilities = db.Column(db.String(100), nullable=False) # multiple abilities

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