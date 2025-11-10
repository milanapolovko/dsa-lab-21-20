from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False) 
    name = db.Column(db.String(100), nullable=False)
    
    def __init__(self, email, password, name):
        self.email = email
        self.password_hash = generate_password_hash(password) 
        self.name = name
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password) 
    
