""" backend project setup """
from flask import Flask
from common.config import Config
from common.extensions import db, jwt, socketio,mail,redis_client
from api.user import user_bp
from api.disease import disease_bp
from api.patient import patient_bp
from api.LLM import llm_bp
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
    redis_client.init_app(app)
    
    app.config['db'] = db
    app.config['jwt'] = jwt
    app.config['socketio'] = socketio
    app.config['mail'] = mail
    app.config['redis_client'] = redis_client

    # Register Blueprints
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(disease_bp, url_prefix='/api/disease')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(llm_bp, url_prefix='/api/llm')
    with app.app_context():
        db.create_all()


    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080","http://localhost:8081"]}},supports_credentials=True)
    # CORS(app, resources={r"/*": {"origins": "http://100.78.9.135:8080"}}, supports_credentials=True) # 测试使用100.78.9.135是自己电脑的ip
    return app
