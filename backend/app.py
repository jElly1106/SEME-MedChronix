""" backend project setup """
from flask import Flask
from common.config import Config
from common.extensions import db, jwt, socketio,mail
from api.user import user_bp
from flask_cors import CORS
# from models import Restaurant, User, Order# group_init


def create_app():
    """backend project creation
    
    returns: app object
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    mail.init_app(app)
    
    # Register Blueprints
    app.register_blueprint(user_bp, url_prefix='/api/user')
    with app.app_context():
        db.create_all()


    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080","http://localhost:8081"]}},supports_credentials=True)
    # CORS(app, resources={r"/*": {"origins": "http://100.78.9.135:8080"}}, supports_credentials=True) # 测试使用100.78.9.135是自己电脑的ip
    return app
