#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api
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

# --- Restaurants ---
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    restaurants_serialized = [r.to_dict(only=("id", "name", "address")) for r in restaurants]
    return make_response(restaurants_serialized, 200)

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)

    restaurant_data = restaurant.to_dict()
    restaurant_pizzas = []
    for rp in restaurant.restaurant_pizzas:
        rp_data = rp.to_dict()
        rp_data["pizza"] = rp.pizza.to_dict()
        restaurant_pizzas.append(rp_data)
    restaurant_data["restaurant_pizzas"] = restaurant_pizzas
    return make_response(restaurant_data, 200)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response({"error": "Restaurant not found"}, 404)
    
    # Cascade delete restaurant pizzas
    for rp in restaurant.restaurant_pizzas:
        db.session.delete(rp)

    db.session.delete(restaurant)
    db.session.commit()
    return make_response("", 204)

# --- Pizzas ---
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_serialized = [p.to_dict() for p in pizzas]
    return make_response(pizzas_serialized, 200)

# --- RestaurantPizzas ---
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        new_rp = RestaurantPizza(
            price=data["price"],
            pizza_id=data["pizza_id"],
            restaurant_id=data["restaurant_id"]
        )
        db.session.add(new_rp)
        db.session.commit()
        return make_response(new_rp.to_dict(), 201)
    except ValueError as e:
        return make_response({"errors": [str(e)]}, 400)
    except KeyError as e:
        return make_response({"errors": [f"Missing {str(e)} key in request data"]}, 400)

# --- Run server ---
if __name__ == "__main__":
    app.run(port=5555, debug=True)
    