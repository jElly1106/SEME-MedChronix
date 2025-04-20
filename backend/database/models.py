"""The models for database."""
from common.extensions import db
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
import json

# User Model
class User(db.Model):
    """User model wrapper."""
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    avatar = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    is_forbidden = db.Column(db.Boolean, default=False)
    
    def set_password(self, password: str):
        """Set the password.

        Args:
            password (str): The string for the password.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        """The validation for the password.

        Args:
            password (str): The string for the password.
        """
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self):
        """Generate JWT for user authentication
        
        Returns:
            token (str): The JWT string.
        """
        identity_data = json.dumps({'id': self.id, 'is_admin': self.is_admin})
        return create_access_token(identity=identity_data)
    

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'email': self.email,
            'avatar': self.avatar,
            'is_admin': self.is_admin,
            'is_forbidden': self.is_forbidden,
        }

