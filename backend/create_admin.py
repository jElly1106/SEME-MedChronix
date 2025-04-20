"""创建管理员账号的脚本"""
import argparse
import re
from app import create_app
from database.models import User, db

def is_valid_email(email):
    """验证邮箱格式是否正确"""
    pattern = r'^[\w\.-]+@([\w\-]+\.)+[A-Za-z]{2,}$'
    return re.match(pattern, email) is not None

def create_admin(email, password, nickname="管理员"):
    """创建管理员账号"""
    app = create_app()
    with app.app_context():
        # 检查邮箱格式
        if not is_valid_email(email):
            print("错误：邮箱格式不正确！")
            return False
            
        # 检查是否已存在该邮箱的账号
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"错误：邮箱 {email} 已被注册！")
            return False
            
        # 创建管理员账号
        admin_user = User(
            nickname=nickname,
            email=email,
            is_admin=True,
            qualificationStatus='approved'
        )
        admin_user.set_password(password)
        db.session.add(admin_user)
        db.session.commit()
        print(f"管理员账号创建成功！\n邮箱: {email}\n昵称: {nickname}")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='创建MedChronix系统管理员账号')
    parser.add_argument('-e', '--email', required=True, help='管理员邮箱地址')
    parser.add_argument('-p', '--password', required=True, help='管理员密码')
    parser.add_argument('-n', '--nickname', default="管理员", help='管理员昵称（可选，默认为"管理员"）')
    
    args = parser.parse_args()
    create_admin(args.email, args.password, args.nickname)
