# Simon Dutton

from flask import render_template, request, redirect, url_for
from app import app
from .forms import PokemonForm, UpdateUserForm # IMPORT ANY FORMS
from .models import Pokemon, User, PokemonCaughtBy
from flask_login import login_required, current_user
from flask_uploads import configure_uploads, IMAGES, UploadSet
from flask import flash, get_flashed_messages
#import ast # to get list from string of list
#from flask_optional_routes import OptionalRoutes
# let's get this undownloaded from requirements.txt
#optional = OptionalRoutes(app)

from sqlalchemy import desc, func 

import requests # to handle the PokeAPI

images = UploadSet('images', IMAGES)
configure_uploads(app, images)

def find_poke(pokemon_name):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/'

    print(url)

    response = requests.get(url)
    if not response.ok:
            #return render_template('search.html', form = SignUpForm())
            return "Try again?"
    data = response.json()

    # to get pokemon type:
    id = data['id']
    type_url = f'https://pokeapi.co/api/v2/pokemon-form/{id}/'
    
    print(type_url)
    type_response = requests.get(type_url)
    type_data = type_response.json()

    poke_dict={
        "poke_id": data['id'],
        "name": data['name'].title(),
        "abilities" : [ability['ability']['name'] for ability in data['abilities']], # lc to get all abilities
        "base_experience":data['base_experience'],
        "photo":data['sprites']['front_shiny'], # i changed this to be front shiny
        "attack_base_stat": data['stats'][1]['base_stat'],
        "hp_base_stat":data['stats'][0]['base_stat'],
        "defense_base_stat":data['stats'][2]["base_stat"],
        #"type":type_data['types'][0]['type']['name'] # just getting
        "types": [type['type']['name'] for type in type_data['types']]
    }
    print(f"Type is: {poke_dict['types']}")
    return poke_dict

@app.route('/', methods=["GET"])
def home_page():
    return render_template('index.html')   

#@app.route('/search', methods=["GET","POST"], defaults={'pokemon': None})
#@app.route('/search/<string:pokemon>')
                            #pokemon is the pokemon name
#@optional.routes('/search/<string:pokemon_name>?/', methods=["GET","POST"], defaults={'pokemon_name': ""})
@app.route('/search/', methods=["GET","POST"], defaults={'pokemon_name': None})
@app.route('/search/<string:pokemon_name>', methods=["GET","POST"])
@login_required # a user cannot use the database without making an account now
def search_page(pokemon_name):
    #print(f"Current prof pic: {current_user.profile_pic}")

    form = PokemonForm()
    if request.method == 'POST':
        if form.validate():
            try:
                poke_dict = find_poke(form.pokemon_name.data.lower())
                pokemon_name = poke_dict['name']
                pokemon = Pokemon(poke_dict['name'], poke_dict['hp_base_stat'], poke_dict['defense_base_stat'], poke_dict['attack_base_stat'], poke_dict['photo'], poke_dict['abilities'], poke_dict['types'])
            except: # if pokemon isnt in api
                return render_template('search.html', not_in_list=form.pokemon_name.data, form = form)
            #ADDED THIS SO THAT USER CAN ONLY INPUT ITEM ONCE INTO THE DB
            pokemon_already_in_db = Pokemon.query.filter_by(pokemon_name=pokemon_name.title()).first()
            if not pokemon_already_in_db:
                # only add to the db if not already in there
                pokemon.save_to_db()

            properties = {
                'name' : pokemon_name,
                'hp_base_stat' : poke_dict['hp_base_stat'],
                'defense_base_stat' : poke_dict['defense_base_stat'],
                'attack_base_stat' : poke_dict['attack_base_stat'],
                'photo' : poke_dict['photo'],
                'abilities' : poke_dict['abilities'],
                'types' : poke_dict['types']
            } 
            properties = properties
            return render_template('search.html', form = form, len = len(properties['abilities']),properties=properties, main_type = properties['types'][0], pokemon=pokemon)
    else:
        # if pokemon
        # make sure that it goes back to the right info and passes it along
        #pokemon = args[0] 
        pokemon = Pokemon.query.get(pokemon_name)

        if pokemon:
            try:
                print(f'pokemon is {pokemon_name}')
                poke_dict = find_poke(pokemon_name.lower())
                print(f"poke_dict is {poke_dict}")
            except: # if pokemon isnt in api
                # we will want to flast that the pokemon was not in the aPI - though this wouldn't happen, still good practice
                return render_template('search.html', not_in_list=form.pokemon_name.data, form = form)

            properties = {
                'name' : pokemon_name,
                'hp_base_stat' : poke_dict['hp_base_stat'],
                'defense_base_stat' : poke_dict['defense_base_stat'],
                'attack_base_stat' : poke_dict['attack_base_stat'],
                'photo' : poke_dict['photo'],
                'abilities' : poke_dict['abilities'],
                'types' : poke_dict['types']
            } 
            return render_template('search.html', form = form, len = len(properties['abilities']),properties=properties, main_type = properties['types'][0], pokemon=pokemon)
        else:
            return render_template('search.html', form = form)   


# What about /users? Make sure that redirects
@app.route('/user/<int:user_id>')
@login_required # we need to be logged in to view other users
def user_page(user_id):
    # make sure valid user id
    user = User.query.get(user_id)

    session = PokemonCaughtBy.get_session()
    query = session.query(Pokemon).join(PokemonCaughtBy).join(User).filter(PokemonCaughtBy.user_id == user.user_id).all()
    #print(f"Query is {query}")
    #items = [r[0] for r in query]
    #print(items)
    for pokemon in query:
        print(pokemon.pokemon_name)
    
    pokemon_list = [pokemon for pokemon in query]

    # abilities = string-split at , and also .strip of {}

    # what things do we need?
    # list of pokemon, length of said list
    # the properties for each pokemon
    # user = user
    # main_type for each pokemon
    #return render_template('search.html', form = form, len = len(properties['abilities']),properties=properties, main_type = properties['types'][0], pokemon=pokemon)


    if user:
        #print(f"Pokemon Types: {pokemon_list[0].types[0]}")
        return render_template('user.html', user=user, pokemon_list = pokemon_list, len_pokemon_list = len(pokemon_list))
        #return render_template('user.html', user=user)
    else:
        # go to your own user profile page 
        return redirect(url_for('user_page', user_id=current_user.user_id))
    
@app.route('/user/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    # find the user to be deleted
    user = User.query.get(user_id)
    if user:
        # make sure it's the current user
        if user.id == current_user.id:
            user.delete_from_db()
        else:
            # CHANGE THIS
            print('You cannot delete another user')
    else:
        print('The user you are trying to delete does not exist')
    # return to the home page
    # make sure that the user logs out
    return redirect(url_for('login_page'))

@app.route('/user/update/<int:user_id>', methods = ['GET', 'POST'])
@login_required
def update_user(user_id):
    # find this user
    user = User.query.get(user_id)
    if user:
        # make sure you are the user so the wrong user doesn't update stuff
        if user.user_id == current_user.user_id:
            form = UpdateUserForm()
            if request.method == 'POST':
                if form.validate():
                    first_name = form.first_name.data
                    last_name = form.last_name.data
                    email = form.email.data
                    password = form.password.data
                    #image_file = images.save(form.profile_pic.data)
                    
                    # if the image was deleted
                    remove = form.delete_profile_pic.data
                    if remove:
                        user.profile_pic = ''

                    print(form.profile_pic.data)
                 
                    try:
                    #if 'image' in request.form:
                        print('requested an image')
                        filename = images.save(form.profile_pic.data)
                        image_file = url_for('static', filename=f'img/user_img/{filename}')
                        user.profile_pic = image_file
                    except:
                        pass
                    
                    bio = form.bio.data
                    color = form.color.data

                    print(f"color is {color}")

                    # update the user
                    user.first_name = first_name
                    user.last_name = last_name
                    user.email = email
                    user.password = password
                    # profile_pic is already set above, so no need to set it again here
                    #user.profile_pic = image_file
                    user.bio = bio
                    user.color = color
                    # commit changes
                    user.save_changes_to_db()

                    # put a little flash message here saying Successfully updated the user
                    flash('Successfully updated your profile', 'success')

                    return redirect(url_for('user_page', user_id = user.user_id))
                
            return render_template('update-user.html', form = form, user = user)
        else:
            flash('You cannot update another user\'s profile.', 'danger')
    else:
        flash('The user you are trying to update does not exist.', 'danger')
    return redirect(url_for('home_page'))

@app.route('/catch/<string:pokemon_name>/<int:user_id>')
@login_required
def catch_pokemon(user_id, pokemon_name):
    # find the user 
    user = User.query.get(user_id)
    # find the pokemon
    #pokemon_name2 = Pokemon.query.get(pokemon.pokemon_name)
    pokemon = Pokemon.query.get(pokemon_name)
    # if the user exists
    if user:
        # make sure it's the current user
        if user.user_id == current_user.user_id:
            #user.delete_from_db()
            if pokemon:
                session = PokemonCaughtBy.get_session()
                
                # To backref items
                #pokemon_caught_list.pokemon_caught
                #pokemon_caught_list.trainer

                num_caught_pokemon = session.query(PokemonCaughtBy.pokemon_name).filter_by(user_id=user.user_id).count()
                print(f"NUMBER OF PREVIOUSLY CAUGHT POKEMON : {num_caught_pokemon}")
                #pokemon_caught_list = session.query(PokemonCaughtBy).filter_by(user_id=user.user_id)
                
                #pokemon_caught_list = PokemonCaughtBy.query.filter_by(user_id = user.user_id)
                
                #pokemon_caught_list = session.query(func.array(PokemonCaughtBy.pokemon_name, PokemonCaughtBy.user_id).label('pokemon_from_user')).filter(PokemonCaughtBy.user_id == user.user_id)
                
                #for var in pokemon_caught_list:
                    #print(var.pokemon_name)
                
                #flash(pokemon_caught_list, 'success')

                if num_caught_pokemon < 5:
                
                    #pokemon_caught_by = PokemonCaughtBy(user.user_id, pokemon.pokemon_name)
                    pokemon_caught_by = PokemonCaughtBy(user.user_id, pokemon_name)
                    pokemon_caught_by.save_to_db() 
                    print(f'You have sucessfully caught {pokemon_name}')
                    flash(f'You have successfully caught {pokemon_name}', 'success''')
                    pokemon_caught = session.query(PokemonCaughtBy.pokemon_name).filter_by(user_id=user.user_id)
                    #  This works we are just trying a different way
                    pokemon_caught_list = [r[0] for r in pokemon_caught]
                    print(f"Pokemon Caught List: {pokemon_caught_list}")
                    #pokemon_caught_list = pokemon_caught.statement.execute().fetchall()
                    #print(f"Pokemon Caught List: {pokemon_caught_list}")
                else:
                    flash(f'You have run out of pokeballs and cannot catch any more pokemon. You can release some from your user page.', 'danger')

            else:
                print('The pokemon you are trying to catch does not exist')
        else:
            print('You cannot catch a pokemon for another user')
    else:
        print('The user you are trying to catch a pokemon with does does not exist')
    # return to the home page
    # make sure that the user logs out
    print('redirecting using pokemon')
    #print(f'pokemon name is {pokemon.pokemon_name}')
    return redirect(url_for('search_page', pokemon_name=pokemon_name))
    #return redirect(url_for('search_page'))

@app.route('/user/remove/<int:user_id>/<string:pokemon_name>')
@login_required
def remove_pokemon(user_id, pokemon_name):
    # find the user to be deleted
    user = User.query.get(user_id)
    #find the pokemon to be deleted 
    pokemon = Pokemon.query.get(pokemon_name)
    if user:
        # make sure it's the current user
        if user.user_id == current_user.user_id:
            #make sure the pokemon exists
            if pokemon:
                pokemon_caught_by_user = PokemonCaughtBy.query.filter_by(pokemon_name=pokemon.pokemon_name, user_id=user.user_id).first()
                # make sure that the pokemon was caught by that user
                if pokemon_caught_by_user:
                    # delete from the database
                    pokemon_caught_by_user.delete_from_db()
                else:
                    print('The pokemon was not caught by that specific user')
            else:
                print('The pokemon you are looking for does not exist')
        else:
            # CHANGE THIS
            print('You cannot delete another user\'s pokemon')
    else:
        print('The user you are trying to delete a pokemon from does not exist')
    # return to the user's page
    return redirect(url_for('user_page', user_id=user.user_id))

@app.route('/users')
@login_required
def full_users_page():
    # testing
    friend_requests = current_user.followers.all()
    print(f"These users friend requested me: {friend_requests}")
    sent_friend_requests = current_user.followed.all()
    print(f"Sent these users friend requests: {sent_friend_requests}")


    users = User.query.order_by(desc('date_created')).all() # gives a list of all users
    return render_template('full-users.html', users=users)

@app.route('/friend/<int:user_id>')
@login_required
def friend_user(user_id):
    user = User.query.get(user_id)
    if user:
        current_user.friend(user)

    friends = current_user.followers.all()
    print(friends)
    return redirect(url_for('friend_requests_page'))

@app.route('/unfriend/<int:user_id>')
@login_required
def unfriend_user(user_id):
    user = User.query.get(user_id)
    if user:
        current_user.unfriend(user)
    return redirect(url_for('friend_requests_page'))

@app.route('/deny/<int:user_id>')
@login_required
def deny_user(user_id):
    user = User.query.get(user_id)
    if user:
        current_user.deny(user)
    return redirect(url_for('friend_requests_page'))

@app.route('/friend+requests')
@login_required
def friend_requests_page():
    # We should only have things on this page if it's NOT a mutual friendship

    # Ash sent Brock a friend request
    # Brock Sent Misty a friend request

    # Brock sent Mike a friend request
    # if Mike accepts, then this should be removed from the page

    # Right now sending a friend request will always take us to the friends request page
    # Based on the above methods. Let's find a way to fix that

    friend_requests = current_user.followers.all()
    print(f"These users friend requested me: {friend_requests}")
    sent_friend_requests = current_user.followed.all()
    print(f"Sent these users friend requests: {sent_friend_requests}")

    # if user in current_user.followers.all() and user in current_user.followed.all()
        # Message should read "unfriend"
    # elif user in current_user.followers.all() and user not in current_user.followed.all()
        # Message should read "Accept Friend Request (blue)"
    # elif user not in current_user.followers.all() and user in current_user.followed.all()
        # Message should read "remove friend request"
    # else 
        # Message should read "Friend" (Blue)

    return render_template('friend-requests.html', friend_requests=friend_requests, sent_friend_requests=sent_friend_requests)

@app.route('/friends')
@login_required
def friends_page():
    friend_requests = current_user.followers.all()
    print(f"These users friend requested me: {friend_requests}")
    sent_friend_requests = current_user.followed.all()
    print(f"Sent these users friend requests: {sent_friend_requests}")

    friends = [fr for fr in friend_requests if fr in sent_friend_requests]

    return render_template('friends.html', friends=friends)