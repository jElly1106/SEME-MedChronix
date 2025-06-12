""" backend project setup """
from flask import Flask
from database.models import AuditLog
from common.config import Config
from common.extensions import db, jwt, socketio,mail,redis_client
from api.user import user_bp
from api.disease import disease_bp
from api.patient import patient_bp
from api.LLM import llm_bp
from api.certification import certification_bp
from api.ct_scan import ct_scan_bp
from api.event import event_bp
from api.predict import predict_bp
from api.rule import rule_bp
from api.precondition import precondition_bp
from api.audit_log import audit_log_bp
from flask_cors import CORS
from sqlalchemy.engine import Engine
from sqlalchemy import event
from dotenv import load_dotenv
import os


load_dotenv()
DB_PASSWORD = os.getenv('DB_PASSWORD')

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



    # 配置 SQLCipher
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///instance/medchronix.db?cipher=sqlcipher&key={DB_PASSWORD}"
    app.config['db'] = db
    app.config['jwt'] = jwt
    # app.config['socketio'] = socketio
    app.config['mail'] = mail
    app.config['redis_client'] = redis_client

    # 初始化数据库连接时执行 PRAGMA key
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"PRAGMA key='{DB_PASSWORD}'")
        cursor.close()

    # Register Blueprints
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(disease_bp, url_prefix='/api/disease')
    app.register_blueprint(patient_bp, url_prefix='/api/patient')
    app.register_blueprint(llm_bp, url_prefix='/api/llm')
    app.register_blueprint(certification_bp, url_prefix='/api/certification')
    app.register_blueprint(ct_scan_bp,url_prefix='/api/ct')
    app.register_blueprint(event_bp,url_prefix='/api/event')
    app.register_blueprint(predict_bp,url_prefix='/api/predict')
    app.register_blueprint(rule_bp,url_prefix='/api/rule')
    app.register_blueprint(precondition_bp,url_prefix='/api/precondition')
    app.register_blueprint(audit_log_bp, url_prefix='/api/audit_log')
    with app.app_context():
        db.create_all()


    CORS(app, resources={r"/*": {"origins": ["http://localhost:8080","http://localhost:8081"]}},supports_credentials=True)
    # CORS(app, resources={r"/*": {"origins": "http://100.78.9.135:8080"}}, supports_credentials=True) # 测试使用100.78.9.135是自己电脑的ip
    return app
