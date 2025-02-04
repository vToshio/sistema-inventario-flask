import os

SECRET_KEY = os.urandom(12)
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'
SQLALCHEMY_TRACK_MODIFICATIONS = False
CORS_HEADERS = 'Content-Type'