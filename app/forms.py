from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField #import whatever datatypes we need

from wtforms import FileField
from wtforms.validators import DataRequired, EqualTo, Length #import whatever validators that we need

from wtforms.widgets import ColorInput

class PokemonForm(FlaskForm):
    # behind the scenes, this converts this into fields for HTML
    # specify the type, create instances of those types
    pokemon_name = StringField('Pokemon Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class UpdateUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])               
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    profile_pic = FileField('Select a Profile Picture')
    delete_profile_pic = BooleanField('Delete your profile picture?')
    bio = StringField('Bio', validators=[Length(max=100)])

    color = StringField('Select a color', widget=ColorInput())

    submit = SubmitField('Submit')