"""The route functions for the instance of user table."""
from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message
from database.models import User
from werkzeug.security import check_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity
from common.utils import upload_images
import os
from datetime import datetime, timedelta
import uuid
import random
import string
import json
user_bp = Blueprint('user', __name__)



# 生成随机验证码
def generate_captcha_text(length=6):
    """生成随机数字验证码"""
    return ''.join(random.choices(string.digits, k=length))

# 发送邮箱验证码
def send_email(to, captcha_text):
    """发送验证码到用户邮箱"""
    msg = Message("您的验证码", recipients=[to])
    msg.body = f"您的验证码是: {captcha_text}. 请在 5 分钟内使用该验证码完成注册。" 
    mail = current_app.config['mail']
    mail.send(msg)

@user_bp.route('/send-captcha', methods=['POST'])
def send_captcha():
    """发送邮箱验证码"""
    data = request.get_json()
    email = data['email']

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # 生成验证码
    captcha_text = generate_captcha_text()  # "111111"可以测试用
    captcha_id = str(uuid.uuid4())
    expires_at = datetime.now() + timedelta(minutes=5)  # 设置 5 分钟过期时间

    # Redis 存储验证码信息
    redis_client = current_app.config['redis_client']
    captcha_data = {
        "email": email,
        "captcha": captcha_text,
        "expires_at": expires_at.isoformat(),  # 使用 ISO 格式存储时间
    }
    redis_client.setex(captcha_id, timedelta(minutes=5), json.dumps(captcha_data))  # 设置过期时间

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

    # 从 Redis 获取验证码信息
    redis_client = current_app.config['redis_client']
    captcha_data = redis_client.get(captcha_id)
    if not captcha_data:
        return jsonify({'error': 'Captcha expired or invalid'}), 400

    captcha_data = json.loads(captcha_data)  # 反序列化 JSON 数据
    if datetime.now() > datetime.fromisoformat(captcha_data["expires_at"]):
        redis_client.delete(captcha_id)  # 删除过期验证码
        return jsonify({'error': 'Captcha expired'}), 400

    if input_captcha != captcha_data["captcha"]:
        return jsonify({'error': 'Incorrect captcha'}), 400

    # 验证通过后删除验证码
    redis_client.delete(captcha_id)

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
    db = current_app.config['db']
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
    db = current_app.config['db']
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
    db = current_app.config['db']
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

