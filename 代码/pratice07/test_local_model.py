# 测试本地千问模型连接
import os
from dotenv import load_dotenv
from tool_client import chat_with_llm

def test_local_model():
    """测试本地千问模型是否正常工作"""
    load_dotenv()
    
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:1234/v1")
    model = os.getenv("MODEL", "qwen/qwen3.5-2b")
    api_key = os.getenv("API_KEY", "local")
    
    print("=== 测试本地千问模型 ===")
    print(f"模型: {model}")
    print(f"接口: {base_url}")
    print()
    
    # 构建简单测试消息
    messages = [
        {"role": "system", "content": "你是一个有用的AI助手，回答要简洁明了"},
        {"role": "user", "content": "你好，请问你是谁？"}
    ]
    
    print("发送请求到本地模型...")
    result = chat_with_llm(messages, base_url, model, api_key, 0.7, 500, debug=True)
    print()
    print("=== 响应结果 ===")
    print(result)
    
    # 验证是否成功
    if "API错误" not in result and "请求失败" not in result and "JSON解析失败" not in result and "API返回格式异常" not in result:
        print("\n[OK] 本地模型连接成功！")
        return True
    else:
        print(f"\n[FAIL] 连接失败: {result}")
        return False

if __name__ == "__main__":
    try:
        test_local_model()
    except Exception as e:
        print(f"测试异常: {str(e)}")