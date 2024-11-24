from os import getenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# app setup
app = Flask(__name__)   
app.secret_key = getenv("SECRET_KEY")

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

# routes setup
import routes.global_routes
from routes import blueprints
for blueprint in blueprints:
    app.register_blueprint(blueprint)
