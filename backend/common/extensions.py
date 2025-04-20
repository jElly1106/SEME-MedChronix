""" Extensions """
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail
from flask_redis import FlaskRedis

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()
redis_client = FlaskRedis()

