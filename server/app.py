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

@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    # Get all restaurants from the database
    restaurants = Restaurant.query.all()
    
    # Convert each restaurant object to a dictionary
    restaurants_serialized = [r.to_dict() for r in restaurants]
    
    # Return JSON response with HTTP status 200
    return make_response(restaurants_serialized, 200)

# --- Run server ---
if __name__ == "__main__":
    app.run(port=5555, debug=True)
    