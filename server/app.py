#!/usr/bin/env python3
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api
import os
from typing import Dict, Any
from models import db, Restaurant, Pizza, RestaurantPizza
from sqlalchemy.orm import Session

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Initialize extensions ---
db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# --- Routes ---
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# ------------------------------
# RESTAURANTS ROUTES
# ------------------------------

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    session: Session = db.session
    restaurants = session.query(Restaurant).all()
    serialized = [r.to_dict(only=("id", "name", "address")) for r in restaurants]
    return make_response(jsonify(serialized), 200)

@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id: int):
    session: Session = db.session
    restaurant = session.get(Restaurant, id)
    if restaurant:
        return make_response(jsonify(restaurant.to_dict()), 200)
    return make_response(jsonify({"error": "Restaurant not found"}), 404)

@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id: int):
    session: Session = db.session
    restaurant = session.get(Restaurant, id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    try:
        session.delete(restaurant)
        session.commit()
        return make_response("", 204)
    except Exception as e:
        session.rollback()
        return make_response(jsonify({"error": "Failed to delete restaurant", "details": str(e)}), 500)
    finally:
        session.close()

# ------------------------------
# PIZZAS ROUTE
# ------------------------------

@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    session: Session = db.session
    pizzas = session.query(Pizza).all()
    serialized = [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas]
    return make_response(jsonify(serialized), 200)

# ------------------------------
# RESTAURANT_PIZZAS ROUTE
# ------------------------------

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    session: Session = db.session
    data: Dict[str, Any] = request.get_json() or {}

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Validate required fields
    if price is None or pizza_id is None or restaurant_id is None:
        return make_response(jsonify({"errors": ["Missing required fields"]}), 400)

    # Validate price
    if not (1 <= price <= 30):
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    pizza = session.get(Pizza, pizza_id)
    restaurant = session.get(Restaurant, restaurant_id)
    if not pizza:
        return make_response(jsonify({"errors": ["Pizza not found"]}), 404)
    if not restaurant:
        return make_response(jsonify({"errors": ["Restaurant not found"]}), 404)

    # Create RestaurantPizza
    new_rp = RestaurantPizza(price=price, pizza_id=pizza.id, restaurant_id=restaurant.id)
    try:
        session.add(new_rp)
        session.commit()

        # Explicit nested serialization
        rp_dict = {
            "id": new_rp.id,
            "price": new_rp.price,
            "pizza_id": new_rp.pizza_id,
            "restaurant_id": new_rp.restaurant_id,
            "pizza": pizza.to_dict(only=("id", "name", "ingredients")),
            "restaurant": restaurant.to_dict(only=("id", "name", "address")),
        }
        return make_response(jsonify(rp_dict), 201)

    except Exception as e:
        session.rollback()
        return make_response(jsonify({"error": "Failed to create restaurant pizza", "details": str(e)}), 500)
    finally:
        session.close()


# --- Run server ---
if __name__ == "__main__":
    app.run(port=5555, debug=True)
    