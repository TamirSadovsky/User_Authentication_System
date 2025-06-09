from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db, bcrypt, jwt, limiter
from routes import app_routes

jwt_blacklist = set()

app = Flask(__name__)
app.config.from_object(Config)

# 🟢 את כל ההרחבות מאתחלים כאן פעם אחת
limiter.init_app(app)
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)

CORS(app, supports_credentials=True)
app.register_blueprint(app_routes)
app.jwt_blacklist = jwt_blacklist

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    return jwt_payload["jti"] in jwt_blacklist

@app.route("/test-limit")
@limiter.limit("2 per minute")
def test_limit():
    return "OK"

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
