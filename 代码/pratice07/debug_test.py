# 简单测试脚本
import os
from dotenv import load_dotenv

load_dotenv()

# 打印配置信息
print("=== 配置信息 ===")
print(f"BASE_URL: {os.getenv('BASE_URL')}")
print(f"MODEL: {os.getenv('MODEL')}")
print(f"API_KEY: {'已设置' if os.getenv('API_KEY') else '未设置'}")
print()

# 测试消息格式
messages = [
    {"role": "system", "content": "你是一个有用的助手"},
    {"role": "user", "content": "你好"}
]

print("=== 消息格式 ===")
print(f"消息数量: {len(messages)}")
for i, msg in enumerate(messages):
    print(f"消息{i+1}: role={msg['role']}, content长度={len(msg['content'])}")
print()

print("测试完成！")
