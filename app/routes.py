# Simon Dutton
# due April 12th, 2023
# Pokemon Search
# Lets a user search for a Pokemon and returns a card with that Pokemon

from flask import render_template, request, redirect, url_for
from app import app
from .forms import PokemonForm # IMPORT ANY FORMS
from .models import Pokemon
import requests # to handle the PokeAPI

def find_poke(pokemon_name):
    url = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/'
    response = requests.get(url)
    if not response.ok:
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
def search_page():
    form = PokemonForm()
    if request.method == 'POST':
        if form.validate():
            pokemon_name = form.pokemon_name.data
            poke_dict = find_poke(pokemon_name.lower())
            pokemon = Pokemon(poke_dict['name'], poke_dict['hp_base_stat'], poke_dict['defense_base_stat'], poke_dict['attack_base_stat'], poke_dict['photo'], poke_dict['abilities'])
            
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