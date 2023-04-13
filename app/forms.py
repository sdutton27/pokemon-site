from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField #import whatever datatypes we need
from wtforms.validators import DataRequired #import whatever validators that we need

class PokemonForm(FlaskForm):
    # behind the scenes, this converts this into fields for HTML
    # specify the type, create instances of those types
    # for example:
        # <Type>(<the-label-that-will-show-up>, validators)
    pokemon_name = StringField('Pokemon Name', validators=[DataRequired()])
    submit = SubmitField('Submit')