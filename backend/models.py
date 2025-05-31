from flask_sqlalchemy import SQLAlchemy # pip install Flask-SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(40), primary_key=True, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    # For profile information
    full_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)

