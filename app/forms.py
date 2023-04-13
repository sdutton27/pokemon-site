from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField #import whatever datatypes we need

from wtforms import FileField
from wtforms.validators import DataRequired, EqualTo #import whatever validators that we need

class PokemonForm(FlaskForm):
    # behind the scenes, this converts this into fields for HTML
    # specify the type, create instances of those types
    pokemon_name = StringField('Pokemon Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class SignUpForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])               
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    profile_pic = FileField('Select a Profile Picture')

    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])     
    submit = SubmitField('Submit')