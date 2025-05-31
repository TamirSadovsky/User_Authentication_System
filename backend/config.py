from datetime import timedelta

class Config:
    SECRET_KEY = 'Drivenets-task'
    JWT_SECRET_KEY = 'Drivenets-task'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=10)
    CORS_SUPPORTS_CREDENTIALS = True