from flask import Blueprint, request, jsonify
from models import User, db
from utils.validators import is_valid_email, is_valid_password
from datetime import datetime, timedelta
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    unset_jwt_cookies,
    jwt_required,
    JWTManager,
)  # pip install Flask-JWT-Extended
import uuid
import bcrypt
from utils.email_utils import send_verification_email, generate_verification_code
from flask import render_template


app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/", methods=["GET"])
def home():
    return "User Authentication System - Assignment", 200


@app_routes.route("/signup", methods=["POST"])
def signup():
    try:
        email = request.json.get("email")
        password = request.json.get("password")
        if not email or not password:
            return jsonify({"error": "Missing credentials"}), 400
        # Check if the email already exists
        existing_user = User.query.filter_by(email=email.lower()).first()
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
        verification_token = str(uuid.uuid4())
        send_verification_email(email, verification_token)

        # Create a new user instance
        user = User(
            id=user_id,
            email=email.lower(),
            password=hashed_password,
            verification_token=verification_token,
            verification_token_expiry=datetime.utcnow() + timedelta(hours=1),
        )

        db.session.add(user)
        db.session.commit()
        return jsonify({"message": "User registered"}), 200
    except Exception as e:
        print("Unexpected error:", e)
        return jsonify({"error": "Internal server error"}), 500


@app_routes.route("/logintoken", methods=["POST"])
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    remember = request.json.get("remember", False)  # ⬅️ חדש

    if email is None or password is None:
        return jsonify({"error": "Missing Credentials"}), 401

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return jsonify({"error": "Invalid Credentials"}), 401

    expires = timedelta(days=30) if remember else timedelta(minutes=7)
    access_token = create_access_token(identity=user.id, expires_delta=expires)

    return jsonify({"email": email, "access_token": access_token}), 200


@app_routes.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    # Invalidate the token by adding it to the blacklist
    jwt.blacklist.add(jti)
    response = jsonify({"message": "Successfully logged out"})
    unset_jwt_cookies(response)
    return response, 200


@app_routes.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    profile_data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "address": user.address,
    }
    return jsonify(profile_data), 200


@app_routes.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Update user profile information
    user.full_name = request.json.get("full_name", user.full_name)
    user.phone_number = request.json.get("phone_number", user.phone_number)
    user.address = request.json.get("address", user.address)

    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200


@app_routes.route("/resend_verification", methods=["POST"])
def resend_verification():
    email = request.json.get("email")
    if email is None:
        return jsonify({"error": "Missing email"}), 400
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if user.is_verified:
        return jsonify({"message": "Email already verified"}), 200

    verification_code = generate_verification_code()
    send_verification_email(email, verification_code)

    user.verification_token = verification_code
    user.verification_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    return jsonify({"message": "Verification email resent"}), 200


@app_routes.route("/password_reset", methods=["POST"])
def password_reset():
    email = request.json.get("email")
    if email is None:
        return jsonify({"error": "Missing email"}), 400
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if not user.is_verified:
        return jsonify({"error": "Email not verified"}), 403
    # Generate a password reset token
    reset_token = generate_verification_code()
    send_verification_email(email, reset_token)

    user.verification_token = reset_token
    user.verification_token_expiry = datetime.utcnow() + timedelta(hours=1)
    db.session.commit()

    return jsonify({"message": "Password reset email sent"}), 200


@app_routes.route("/reset_password", methods=["POST"])
def reset_password():
    email = request.json.get("email")
    new_password = request.json.get("new_password")
    code = request.json.get("code")

    if email is None or new_password is None or code is None:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    if code != user.verification_token:
        return jsonify({"error": "Invalid verification code"}), 400

    # Hash the new password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(new_password.encode(), salt).decode()

    user.password = hashed_password
    user.verification_token = None
    user.verification_token_expiry = None
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200


@app_routes.route("/verify", methods=["GET"])
def verify_email():
    token = request.args.get("token")
    if not token:
        return jsonify({"error": "Missing token"}), 400

    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({"error": "Invalid token"}), 404

    user.is_verified = True
    user.verification_token = None
    user.verification_token_expiry = None
    db.session.commit()

    return render_template("verify_success.html", email=user.email)
