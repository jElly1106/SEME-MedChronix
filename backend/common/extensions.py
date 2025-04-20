""" Extensions """
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_mail import Mail

db = SQLAlchemy()
jwt = JWTManager()
socketio = SocketIO()
mail = Mail()

