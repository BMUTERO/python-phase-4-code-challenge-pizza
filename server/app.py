#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_restful import Api
from flask_migrate import Migrate
from models import db, Restaurant, Pizza, RestaurantPizza
import os

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Initialize extensions ---
migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)

# --- Routes ---

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    serialized = [r.to_dict(only=("id", "name", "address")) for r in restaurants]
    return make_response(jsonify(serialized), 200)

# GET /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    serialized = restaurant.to_dict()
    # Include restaurant_pizzas with nested pizza info
    serialized["restaurant_pizzas"] = [
        rp.to_dict() | {"pizza": rp.pizza.to_dict()} for rp in restaurant.restaurant_pizzas
    ]
    return make_response(jsonify(serialized), 200)

# DELETE /restaurants/<id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    
    db.session.delete(restaurant)
    db.session.commit()
    return make_response("", 204)

# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    serialized = [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas]
    return make_response(jsonify(serialized), 200)

# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        rp = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(rp)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return make_response(jsonify({"errors": ["validation errors"]}), 400)
    
    # Return nested pizza and restaurant info
    serialized = rp.to_dict() | {
        "pizza": rp.pizza.to_dict(),
        "restaurant": rp.restaurant.to_dict()
    }
    return make_response(jsonify(serialized), 201)

# --- Run server ---
if __name__ == "__main__":
    app.run(port=5555, debug=True)
    