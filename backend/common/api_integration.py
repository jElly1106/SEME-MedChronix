import os
from openai import OpenAI
import base64
# import requests  # 用于上传文件
# from common.config import get_config

# 获取 API 密钥
api_key = "sk-743310c7aba34b97b9ce13cca22eb31c"  # 你可以从配置文件中获取API Key

# 创建 OpenAI 客户端
client = OpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def get_bot_response(user_message):
    try:
        # 调用 Qwen API 发送消息并获取响应
        completion = client.chat.completions.create(
            model="qwen-plus",  # 使用的模型
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': user_message}
            ]
        )
        
        return completion.choices[0].message.content

    except Exception as e:
        # 捕获并返回异常信息
        return f"Error: {str(e)}"
    

# 读取本地文件并编码为 BASE64 格式
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode("utf-8")