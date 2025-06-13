import pytest
from common.utils import encode_filename
from unittest.mock import patch, MagicMock

def test_encode_filename_cases():
    # 测试普通、特殊、空文件名
    for s in ["a.png", "文件.txt", "", "!@#￥%……"]:
        encoded = encode_filename(s)
        assert isinstance(encoded, str)
        assert encoded != s or s == ""  # 空字符串例外

@patch("common.utils.allowed_file", lambda x: x.endswith(".jpg"))
@patch("common.utils.current_app")
def test_upload_images_success(mock_app):
    mock_app.config = {"UPLOAD_FOLDER": "/tmp"}
    class FakeFile:
        filename = "t.jpg"
        def save(self, save_path):
            # 检查保存路径是字符串（模拟IO）
            assert isinstance(save_path, str)
            return None
    from common.utils import upload_images
    res = upload_images(FakeFile(), "1", "avatars")
    assert res is not None
    assert isinstance(res, str)

@patch("common.utils.allowed_file", lambda x: False)
@patch("common.utils.current_app")
def test_upload_images_invalid(mock_app):
    mock_app.config = {"UPLOAD_FOLDER": "/tmp"}
    class FakeFile:
        filename = "bad.exe"
        def save(self, save_path):
            return None
    from common.utils import upload_images
    res = upload_images(FakeFile(), "2", "comments")
    assert res is None
