import pytest
from unittest.mock import patch, MagicMock

@patch("api.LLM.get_bot_response")
@patch("api.LLM.request")
def test_chat_success(mock_req, mock_bot):
    from api.LLM import chat
    mock_req.json.get.return_value = "你好"
    mock_bot.return_value = "你好，我是AI"
    resp = chat()
    assert "response" in resp.json

@patch("api.LLM.encode_image")
@patch("api.LLM.OpenAI")
@patch("api.LLM.request")
def test_image_analysis_success(mock_req, mock_openai, mock_encode):
    from api.LLM import image_analysis
    fake_file = MagicMock()
    mock_req.files = {"image": fake_file}
    mock_encode.return_value = "base64string"
    mock_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="图像文本"))]
    resp = image_analysis()
    assert "result" in resp.json

@patch("api.LLM.encode_image")
@patch("api.LLM.OpenAI")
@patch("api.LLM.request")
def test_image_analysis_no_file(mock_req, mock_openai, mock_encode):
    from api.LLM import image_analysis
    mock_req.files = {}
    resp, code = image_analysis()
    assert code == 400

@patch("api.LLM.encode_image")
@patch("api.LLM.OpenAI")
@patch("api.LLM.request")
def test_image_analysis_exception(mock_req, mock_openai, mock_encode):
    from api.LLM import image_analysis
    mock_req.files = {"image": MagicMock()}
    mock_encode.side_effect = Exception("file error")
    resp, code = image_analysis()
    assert code == 500

@patch("api.LLM.encode_image")
@patch("api.LLM.OpenAI")
@patch("api.LLM.request")
def test_multimodal_conversation_call_success(mock_req, mock_openai, mock_encode):
    from api.LLM import multimodal_conversation_call
    fake_file = MagicMock()
    mock_req.files.get.return_value = fake_file
    mock_req.form.get.return_value = "请描述"
    mock_encode.return_value = "base64img"
    mock_openai.return_value.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="描述结果"))]
    resp = multimodal_conversation_call()
    assert "result" in resp.json

@patch("api.LLM.request")
def test_multimodal_conversation_call_no_file(mock_req):
    from api.LLM import multimodal_conversation_call
    mock_req.files.get.return_value = None
    resp, code = multimodal_conversation_call()
    assert code == 400
