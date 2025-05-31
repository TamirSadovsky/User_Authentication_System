from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from routes import app_routes
from models import db
from config import Config


 
app = Flask(__name__)
app.register_blueprint(app_routes)

app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

with app.app_context():
   db.create_all()

if __name__ == "__main__":
    app.run(debug=True)