from flask_sqlalchemy import SQLAlchemy # pip install Flask-SQLAlchemy
from datetime import datetime 
from extensions import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(40), primary_key=True, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

    # email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(150), nullable=True, unique=True)
    verification_token_expiry = db.Column(db.DateTime, nullable=True)

    
    # For profile information
    full_name = db.Column(db.String(150), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)

