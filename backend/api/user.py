"""The route functions for the instance of user table."""
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from database.models import User, db
from werkzeug.security import check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.utils import upload_images
from common.extensions import mail
import os
from captcha.image import ImageCaptcha
from datetime import datetime, timedelta
import uuid
import random
import string
import base64
import json
user_bp = Blueprint('user', __name__)


# 简单存储验证码的字典（生产环境请用 Redis 或数据库替代）


# 存储邮箱验证码
captcha_storage = {}  # 格式: {captcha_id: {"email": "邮箱", "captcha": "验证码", "expires_at": 过期时间}}

# 生成随机验证码
def generate_captcha_text(length=6):
    """生成随机数字验证码"""
    return ''.join(random.choices(string.digits, k=length))

# 发送邮箱验证码
def send_email(to, captcha_text):
    """发送验证码到用户邮箱"""
    msg = Message("您的验证码", recipients=[to])
    msg.body = f"您的验证码是: {captcha_text}. 请在 5 分钟内使用该验证码完成注册。"
    try:
        mail.send(msg)
    except Exception as e:
        print(f"发送邮件失败: {e}")

@user_bp.route('/send-captcha', methods=['POST'])
def send_captcha():
    """发送邮箱验证码"""
    data = request.get_json()
    email = data['email']

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # 生成验证码
    captcha_text = "111111"#generate_captcha_text()

    # 生成验证码 ID
    captcha_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(minutes=5)  # 设置 5 分钟过期时间

    # 存储验证码和过期时间
    captcha_storage[captcha_id] = {"email": email, "captcha": captcha_text, "expires_at": expires_at}

    # 发送验证码邮件
    send_email(email, captcha_text)

    return jsonify({"captcha_id": captcha_id, "message": "验证码已发送至邮箱"}), 200

@user_bp.route('/register', methods=['POST'])
def register():
    """注册用户并验证邮箱验证码"""
    data = request.get_json()
    email = data['email']
    input_captcha = data['captcha']
    captcha_id = data['captcha_id']

    if not email or not input_captcha or not captcha_id:
        return jsonify({'error': 'email, captcha, and captcha_id are required'}), 400

    stored_captcha = captcha_storage.get(captcha_id)
    if not stored_captcha:
        return jsonify({'error': 'Captcha expired or invalid'}), 400
    if datetime.now() > stored_captcha["expires_at"]:
        captcha_storage.pop(captcha_id, None)
        return jsonify({'error': 'Captcha expired'}), 400
    if input_captcha != stored_captcha["captcha"]:
        return jsonify({'error': 'Incorrect captcha'}), 400
    # 验证通过后删除验证码
    captcha_storage.pop(captcha_id, None)
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 401

    new_user = User(
        nickname=email,
        email=email,
        avatar=data.get('avatar', ''),
        is_admin=data.get('is_admin', False),
        is_forbidden=data.get('is_forbidden', False),
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201

@user_bp.route('/login', methods=['POST'])
def login():
    """Log in the user.

    Returns:
        A json object consists of message.
    """
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        if user.is_forbidden:
            return jsonify({'error': 'User is forbidden'}), 403
        if user.is_admin:
            return jsonify({'error': 'User is an admin, please register a user account'}), 403
        token = user.generate_token()
        return jsonify({'token': token, 
                        'role': 'user',
                        'user_id':user.id,
                        "message":"Login successful",
                        }), 200
    return jsonify({'error': 'Invalid email or password'}), 400

@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Log out the user and invalidate the JWT token.
    
    Returns:
        A json object consists of message.
    """
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    user = User.query.get(user_data['id'])
    if user:
        return jsonify({'message': 'Logout successful'}), 200
    else:
        return jsonify({'error': 'User not found'}), 404
    
@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取用户的个人资料，包括头像 URL"""
    # print(f"Authorization Header: {request.headers.get('Authorization')}")  # 打印 JWT
    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    user = User.query.get_or_404(user_data['id'])

    if user.avatar:
        avatar_url = f"{request.host_url}{user.avatar}"
    else:
        avatar_url = f"{request.host_url}static/default/default_avatar.png"

    return jsonify({
        'id': user.id,
        'nickname': user.nickname,
        'email': user.email,
        'avatar': avatar_url,  
        'role': 'user' if not user.is_admin else 'admin',
    }), 200

@user_bp.route('/get_info_by_user_id/<int:user_id>', methods=['GET'])
@jwt_required()
def get_info_by_user_id(user_id):
    """获取用户的个人资料，包括头像 URL"""
    # print(f"Authorization Header: {request.headers.get('Authorization')}")  # 打印 JWT
    user = User.query.get_or_404(user_id)

    if user.avatar:
        avatar_url = f"{request.host_url}{user.avatar}"
    else:
        avatar_url = f"{request.host_url}static/default/default_avatar.png"

    return jsonify({
        'id': user.id,
        'nickname': user.nickname,
        'email': user.email,
        'avatar': avatar_url,  
        'role': 'user' if not user.is_admin else 'admin'
    }), 200

@user_bp.route('/profile/change_password', methods=['PUT'])
@jwt_required()
def change_password():
    """Change the user's password.

    Returns:
        A json object consists of message.
    """
    data = request.get_json()

    user_data = get_jwt_identity()
    user_data = json.loads(user_data)
    user = User.query.get_or_404(user_data['id'])
    # print(data)
    if not check_password_hash(user.password_hash, data['old_password']):
        return jsonify({'error': 'Old password is incorrect'}), 400

    user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'}), 200


@user_bp.route('/profile/edit_profile', methods=['POST'])
@jwt_required()
def edit_profile():
    """Edit the user's profile information such as nickname, and avatar.

    Returns:
        A json object consists of message.
    """
    user_data = get_jwt_identity()  # 获取用户 ID
    user_data = json.loads(user_data)
    user = User.query.get_or_404(user_data['id'])

    data = request.form  # 从请求体中获取前端提交的 form data
    # print("接收到的数据:", data)  # 打印接收到的数据，调试用

    if 'nickname' in data:
        user.nickname = data['nickname']
    
    if 'avatar' in request.files:
        file = request.files['avatar']
        file_path = upload_images(file, user.id, upload_type="avatars")
        if not file_path:
            return jsonify({'error': '图像上传失败'}), 400
        if user.avatar and os.path.exists(user.avatar):
            os.remove(user.avatar)
        user.avatar = file_path  # 更新数据库中的头像路径

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

