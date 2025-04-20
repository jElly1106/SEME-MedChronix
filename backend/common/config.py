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
    MAIL_PORT = 587  # 邮件端口
    MAIL_USE_TLS = True  # 使用 TLS 加密
    MAIL_USERNAME = '169717025.@qq.com'  # 发件人邮箱
    MAIL_PASSWORD = 'vqnjevvgjvgbbhdf'  # 发件人邮箱密码
    MAIL_DEFAULT_SENDER = '169717025.@qq.com'  # 发件人地址
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
