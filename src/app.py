"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# --- API endpoints ---

# People endpoints
@app.route('/people', methods=['GET'])
def get_people():
    people = Character.query.all()
    return jsonify([p.serialize() for p in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    person = Character.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200

# Planets endpoints
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# Users endpoints
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

# Simulación de usuario autenticado
CURRENT_USER_ID = 1

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    favorites = Favorite.query.filter_by(user_id=CURRENT_USER_ID).all()
    return jsonify([fav.serialize() for fav in favorites]), 200

# Añadir favorito planeta
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planet not found"}), 404

    existing = Favorite.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if existing:
        return jsonify({"msg": "Favorite already exists"}), 400

    fav = Favorite(user_id=CURRENT_USER_ID, planet_id=planet_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet added"}), 201

# Añadir favorito persona
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "Person not found"}), 404

    existing = Favorite.query.filter_by(user_id=CURRENT_USER_ID, character_id=people_id).first()
    if existing:
        return jsonify({"msg": "Favorite already exists"}), 400

    fav = Favorite(user_id=CURRENT_USER_ID, character_id=people_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite person added"}), 201

# Eliminar favorito planeta
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    fav = Favorite.query.filter_by(user_id=CURRENT_USER_ID, planet_id=planet_id).first()
    if not fav:
        return jsonify({"msg": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet removed"}), 200

# Eliminar favorito persona
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    fav = Favorite.query.filter_by(user_id=CURRENT_USER_ID, character_id=people_id).first()
    if not fav:
        return jsonify({"msg": "Favorite not found"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite person removed"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

