# 运行实际的 API 测试
import os
from dotenv import load_dotenv
from tool_client import chat_with_llm

load_dotenv()

base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
model = os.getenv("MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free")
api_key = os.getenv("API_KEY", "")

if not api_key:
    print("错误：未设置 API_KEY")
    exit(1)

print("=== 测试 API 调用 ===")
print(f"模型: {model}")
print(f"接口: {base_url}")
print()

# 构建测试消息
messages = [
    {"role": "system", "content": "你是一个有用的助手，回答要简洁"},
    {"role": "user", "content": "你好，测试一下"}
]

print("发送请求...")
result = chat_with_llm(messages, base_url, model, api_key, 0.7, 500, debug=True)
print()
print("=== 响应结果 ===")
print(result)
