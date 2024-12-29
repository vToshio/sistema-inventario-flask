from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model): 
    __tablename__ = 'users'
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True, nullable=False, unique=True)
    role = db.Column('role', db.String(6), nullable=False)
    name = db.Column('name', db.String(30), nullable=False)
    username = db.Column('username', db.String(20), nullable=False, unique=True)
    password = db.Column('password', db.String(100), nullable=False)
    email = db.Column('email', db.String(50), unique=True)
    date_created = db.Column('date_created', db.Date, default=datetime.now(), nullable=False)

    def __repr__(self):
        return f'<User: {self.username}>'