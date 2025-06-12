from flask import Blueprint, request, jsonify
from common.api_integration import get_bot_response, encode_image
from openai import OpenAI

llm_bp = Blueprint('llm', __name__)

@llm_bp.route('/chat', methods=['POST'])
def chat():
    # 获取用户消息
    user_message = request.json.get('message')

    # 调用 Qwen API 获取响应
    bot_response = get_bot_response(user_message)

    # 返回聊天响应
    return jsonify({'response': bot_response})

@llm_bp.route('/image-analysis', methods=['POST'])
def image_analysis():
    try:
        # 获取上传的图片文件
        file = request.files['image']  # 'image' 是上传文件的字段名
        if not file:
            return jsonify({"error": "No image file provided"}), 400
        
        # 将图片文件编码为 Base64
        base64_image = encode_image(file)

        # 创建 OpenAI 客户端
        client = OpenAI(
            api_key='sk-743310c7aba34b97b9ce13cca22eb31c',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        # 调用 Qwen API 进行图像分析
        completion = client.chat.completions.create(
            model="qwen-vl-ocr",  # 使用 OCR 模型
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                            "min_pixels": 28 * 28 * 4,
                            "max_pixels": 28 * 28 * 1280
                        },
                        {"type": "text", "text": "Read all the text in the image."},
                    ],
                }
            ],
        )
        
        # 返回解读结果
        return jsonify({"result": completion.choices[0].message.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@llm_bp.route('/multimodal', methods=['POST'])
def multimodal_conversation_call():
    try:
        # 获取上传的图片文件
        print(f"Received file: {request.files.get('image')}")
        file = request.files.get('image')    
        if not file:
            return jsonify({"error": "没有提供图片文件"}), 400
        
        # 获取问题文本
        question = request.form.get('question', "请描述这张图片")
        print(f"Received question: {question}")
        # 将图片文件编码为 Base64
        base64_image = encode_image(file)
        
        client = OpenAI(
            api_key='sk-743310c7aba34b97b9ce13cca22eb31c',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": question},
                {"type": "image_url", 
                 "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}]
        )
        
        # 返回解读结果
        return jsonify({"result": completion.choices[0].message.content})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500