import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 1. 验证码生成
def test_generate_captcha_text():
    from api.user import generate_captcha_text
    assert generate_captcha_text(6).isdigit() and len(generate_captcha_text(6)) == 6
    assert generate_captcha_text(4).isdigit() and len(generate_captcha_text(4)) == 4

# 2. 邮件发送
@patch("api.user.current_app")
def test_send_email_success(mock_app):
    from api.user import send_email
    mock_mail = MagicMock()
    mock_app.config = {'mail': mock_mail}
    send_email("to@test.com", "123456")
    mock_mail.send.assert_called_once()

# 3. 发送验证码
@patch("api.user.current_app")
@patch("api.user.send_email")
def test_send_captcha_success(mock_send_email, mock_app):
    from api.user import send_captcha
    mock_redis = MagicMock()
    mock_app.config = {"redis_client": mock_redis, "mail": MagicMock()}
    with patch("api.user.request") as req:
        req.get_json.return_value = {"email": "test@demo.com"}
        resp, code = send_captcha()
        assert code == 200
        mock_send_email.assert_called_once()

@patch("api.user.current_app")
def test_send_captcha_no_email(mock_app):
    from api.user import send_captcha
    with patch("api.user.request") as req:
        req.get_json.return_value = {}
        resp, code = send_captcha()
        assert code == 400

# 4. 注册
@patch("api.user.current_app")
def test_register_success(mock_app):
    from api.user import register
    redis = MagicMock()
    redis.get.return_value = b'{"email":"test@a.com","captcha":"666666","expires_at":"2099-12-31T12:00:00"}'
    redis.delete.return_value = None
    db = MagicMock()
    mock_app.config = {"redis_client": redis, "db": db}
    # 用户未注册
    with patch("api.user.User.query") as uquery:
        uquery.filter_by.return_value.first.return_value = None
        with patch("api.user.request") as req:
            req.get_json.return_value = {
                "email":"test@a.com", "captcha":"666666", "captcha_id":"cid",
                "nickname":"nick", "password":"pw"
            }
            resp, code = register()
            assert code == 201

@patch("api.user.current_app")
def test_register_already_exists(mock_app):
    from api.user import register
    redis = MagicMock()
    redis.get.return_value = b'{"email":"test@a.com","captcha":"666666","expires_at":"2099-12-31T12:00:00"}'
    db = MagicMock()
    mock_app.config = {"redis_client": redis, "db": db}
    # 用户已存在
    with patch("api.user.User.query") as uquery:
        uquery.filter_by.return_value.first.return_value = MagicMock()
        with patch("api.user.request") as req:
            req.get_json.return_value = {
                "email":"test@a.com", "captcha":"666666", "captcha_id":"cid",
                "nickname":"nick", "password":"pw"
            }
            resp, code = register()
            assert code == 400

@patch("api.user.current_app")
def test_register_captcha_error(mock_app):
    from api.user import register
    redis = MagicMock()
    redis.get.return_value = b'{"email":"test@a.com","captcha":"888888","expires_at":"2099-12-31T12:00:00"}'
    db = MagicMock()
    mock_app.config = {"redis_client": redis, "db": db}
    with patch("api.user.User.query") as uquery:
        uquery.filter_by.return_value.first.return_value = None
        with patch("api.user.request") as req:
            req.get_json.return_value = {
                "email":"test@a.com", "captcha":"666666", "captcha_id":"cid",
                "nickname":"nick", "password":"pw"
            }
            resp, code = register()
            assert code == 400

@patch("api.user.current_app")
def test_register_expired_captcha(mock_app):
    from api.user import register
    past_time = (datetime.now() - timedelta(days=1)).isoformat()
    redis = MagicMock()
    redis.get.return_value = bytes(
        '{"email":"test@a.com","captcha":"666666","expires_at":"%s"}' % past_time,
        encoding="utf-8")
    db = MagicMock()
    mock_app.config = {"redis_client": redis, "db": db}
    with patch("api.user.User.query") as uquery:
        uquery.filter_by.return_value.first.return_value = None
        with patch("api.user.request") as req:
            req.get_json.return_value = {
                "email":"test@a.com", "captcha":"666666", "captcha_id":"cid",
                "nickname":"nick", "password":"pw"
            }
            resp, code = register()
            assert code == 400

# 5. 登录
@patch("api.user.User")
@patch("api.user.request")
@patch("api.user.current_app")
def test_login_success(mock_app, mock_req, mock_User):
    from api.user import login
    mock_user = MagicMock()
    mock_user.check_password.return_value = True
    mock_user.generate_token.return_value = "jwt"
    mock_user.is_admin = False
    mock_user.qualificationStatus = "approved"
    mock_user.id = 1
    mock_User.query.filter_by.return_value.first.return_value = mock_user
    mock_req.get_json.return_value = {"email":"test@a.com", "password":"pw"}
    resp, code = login()
    assert code == 200
    assert "token" in resp

@patch("api.user.User")
@patch("api.user.request")
def test_login_fail(mock_req, mock_User):
    from api.user import login
    mock_User.query.filter_by.return_value.first.return_value = None
    mock_req.get_json.return_value = {"email":"notfound@a.com", "password":"pw"}
    resp, code = login()
    assert code == 400

# 6. change_password
@patch("api.user.User")
@patch("api.user.request")
@patch("api.user.get_jwt_identity")
@patch("api.user.current_app")
def test_change_password_success(mock_app, mock_get_jwt, mock_req, mock_User):
    from api.user import change_password
    db = MagicMock()
    mock_app.config = {"db": db}
    user_obj = MagicMock()
    user_obj.check_password_hash = True
    user_obj.set_password.return_value = None
    mock_User.query.get_or_404.return_value = user_obj
    mock_get_jwt.return_value = '{"id": 1}'
    mock_req.get_json.return_value = {"old_password":"pw", "new_password":"newpw"}
    resp, code = change_password()
    assert code == 200

@patch("api.user.User")
@patch("api.user.request")
@patch("api.user.get_jwt_identity")
@patch("api.user.current_app")
def test_change_password_fail(mock_app, mock_get_jwt, mock_req, mock_User):
    from api.user import change_password
    db = MagicMock()
    mock_app.config = {"db": db}
    user_obj = MagicMock()
    user_obj.check_password_hash = False
    mock_User.query.get_or_404.return_value = user_obj
    mock_get_jwt.return_value = '{"id": 1}'
    mock_req.get_json.return_value = {"old_password":"pw", "new_password":"newpw"}
    resp, code = change_password()
    assert code == 400

# 7. 权限检查 admin_required
@patch("api.user.get_jwt_identity")
def test_admin_required_true(mock_get_jwt):
    from api.user import admin_required
    mock_get_jwt.return_value = '{"id": 1, "is_admin": true}'
    # 伪装成装饰器模式
    def fake_func():
        return "ok"
    wrapped = admin_required(fake_func)
    assert callable(wrapped)
