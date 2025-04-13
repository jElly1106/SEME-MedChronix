"""Configuration file for the application"""
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mysecretkey')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123zxc@127.0.0.1:3306/roomorder?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'supersecretjwt')
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif','webp'}
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    # 邮箱配置
    MAIL_SERVER = 'smtp.qq.com'  # SMTP 邮件服务器（例如 Gmail，QQ 邮箱等）
    MAIL_PORT = 465  # 邮件端口
    MAIL_USE_SSL = True  # 使用 SSL 加密
    MAIL_USE_TLS = False  
    MAIL_USERNAME = '1697170250@qq.com'  # 发件人邮箱
    MAIL_PASSWORD = 'xqvgtcuaabukbeae'  # 发件人邮箱密码
    MAIL_DEFAULT_SENDER = '1697170250@qq.com'  # 发件人地址，可选
    # Redis 配置
    REDIS_URL = 'redis://localhost:6379/0'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
