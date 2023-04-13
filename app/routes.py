# Simon Dutton
# due April 12th, 2023
# Pokemon Search
# Lets a user search for a Pokemon and returns a card with that Pokemon

from flask import render_template, request, redirect, url_for
from app import app
from .forms import PokemonForm, SignUpForm, LoginForm # IMPORT ANY FORMS
from .models import Pokemon, User
from flask_login import login_user, logout_user, login_required, current_user
from email_validator import validate_email
from flask_uploads import configure_uploads, IMAGES, UploadSet

import requests # to handle the PokeAPI

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

def find_poke(pokemon_name):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/'
    response = requests.get(url)
    if not response.ok:
            #return render_template('search.html', form = SignUpForm())
            return "Try again?"
    data = response.json()
    poke_dict={
        "poke_id": data['id'],
        "name": data['name'].title(),
        "abilities" : [ability['ability']['name'] for ability in data['abilities']], # lc to get all abilities
        "base_experience":data['base_experience'],
        "photo":data['sprites']['front_shiny'], # i changed this to be front shiny
        "attack_base_stat": data['stats'][1]['base_stat'],
        "hp_base_stat":data['stats'][0]['base_stat'],
        "defense_base_stat":data['stats'][2]["base_stat"]
    }
    return poke_dict

@app.route('/', methods=["GET"])
def home_page():
    return render_template('index.html')   

@app.route('/search', methods=["GET","POST"])
@login_required # a user cannot use the database without making an account now
def search_page():

    print(f"Current prof pic: {current_user.profile_pic}")

    form = PokemonForm()
    if request.method == 'POST':
        if form.validate():
            try:
                pokemon_name = form.pokemon_name.data
                poke_dict = find_poke(pokemon_name.lower())
                pokemon = Pokemon(poke_dict['name'], poke_dict['hp_base_stat'], poke_dict['defense_base_stat'], poke_dict['attack_base_stat'], poke_dict['photo'], poke_dict['abilities'])
            except: # if pokemon isnt in api
                return render_template('search.html', not_in_list=pokemon_name, form = form)
            #ADDED THIS SO THAT USER CAN ONLY INPUT ITEM ONCE INTO THE DB
            pokemon_already_in_db = Pokemon.query.filter_by(name=pokemon_name.title()).first()
            if not pokemon_already_in_db:
                # only add to the db if not already in there
                pokemon.save_to_db()

            properties = {
                'name' : pokemon_name,
                'hp_base_stat' : poke_dict['hp_base_stat'],
                'defense_base_stat' : poke_dict['defense_base_stat'],
                'attack_base_stat' : poke_dict['attack_base_stat'],
                'photo' : poke_dict['photo'],
                'abilities' : poke_dict['abilities']
            } 
            properties = properties
            return render_template('search.html', form = form, len = len(properties['abilities']),properties=properties)
    return render_template('search.html', form = form)   

@app.route('/signup', methods=["GET", "POST"])
def signup_page():
    # instantiate the form
    form = SignUpForm()

    if request.method == 'POST':
        if form.validate(): 
            first_name = form.first_name.data
            last_name = form.last_name.data
            email = form.email.data
            password = form.password.data

            is_new_account = True

            # Make sure the user is not in the db yet
            try:
                validation = validate_email(email, check_deliverability=is_new_account)
                email = validation.email
            except: 
                #invalid email
                return render_template('signup.html', invalid_email=email, form = form)
            
            #ADDED THIS SO THAT USER CAN ONLY INPUT ITEM ONCE INTO THE DB
            user_already_exists = User.query.filter_by(email=email).first()
            if not user_already_exists:
                try:
                    filename = images.save(form.profile_pic.data)
                    image_file = url_for('static', filename=filename)
                    # only add to the db if not already in there
                    user = User(first_name, last_name, email, password, image_file)
                except:
                    # create a user without a profile pic
                    user = User(first_name, last_name, email, password)
                user.save_to_db() 
                login_user(user)
                return redirect(url_for('home_page'))
            else:
                # user already has an account
                # they are trying to remake an account so tell them instead an email exists
                return render_template('signup.html', used_email=email, form = form)
    
    # if password does not equal confirm password data:
    if form.password.data != form.confirm_password.data:
        print('invalid password')
        return render_template('signup.html', invalid_password=True, form = form)        

    return render_template('signup.html', form = form)


@app.route('/login', methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate(): # if form is valid
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user: # user was found
                # verify password
                # looks at the password in the database = the password you sent in the form
            if user.password == password:
                    # log in
                login_user(user) #login the user
                    # take the user back to the homepage
                return redirect(url_for('home_page'))
            else:
                    # invalid password
                    print('incorrect username(for security) or password(true)')
                    return render_template('login.html', incorrect_login=True, form = form)
        else: # user was not found
            print('incorrect username(true) or password(just for security)')
            return render_template('login.html', incorrect_login=True, form = form)

    return render_template('login.html', form = form)

@app.route('/logout')
def log_me_out():
    logout_user()
    return redirect(url_for('login_page'))