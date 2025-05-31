from flask import Blueprint, request, jsonify
from models import User, db
from validators import is_valid_email, is_valid_password
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, jwt_required, JWTManager #pip install Flask-JWT-Extended
import uuid
import bcrypt

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/', methods=['GET'])
def home():
    return "Drivenets - Assignment", 200

@app_routes.route('/signup', methods = ['POST'])
def signup():
    try:
        email = request.json.get('email')
        password = request.json.get('password')
        if not email or not password:
            return jsonify({"error": "Missing credentials"}), 400
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Email already exists"}), 400
        if not is_valid_email(email):
            return jsonify({"error": "Invalid email"}), 400
        if not is_valid_password(password):
            return jsonify({"error": "Invalid password"}), 400
        # Generate a unique user ID
        user_id = str(uuid.uuid4())
        # Hash the password using bcrypt
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode(), salt).decode()

        # Create a new user instance
        user = User(
            id=user_id,
            email=email,
            password=hashed_password,
        )

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered"}), 201
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Internal server error"}), 500


@app_routes.route("/logintoken", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email is None or password is None:
        return jsonify({"error": "Missing Credentials"}), 401
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404

    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({"error": "Invalid Credentials"}), 401

    access_token = create_access_token(identity=user.id, expires_delta=timedelta(minutes=7))

    return jsonify({
        "email": email,
        "access_token": access_token
    }), 200