import os
from dotenv import load_dotenv
from tool_client import chat_with_llm

def test_api_call():
    """测试 API 调用是否正常"""
    load_dotenv()
    base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free")
    api_key = os.getenv("API_KEY", "")
    
    if not api_key:
        print("错误：未设置 API_KEY")
        return
    
    # 构建简单的测试消息
    messages = [
        {"role": "system", "content": "你是一个有用的助手"},
        {"role": "user", "content": "你好，测试一下"}
    ]
    
    print("测试 API 调用...")
    result = chat_with_llm(messages, base_url, model, api_key, 0.7, 1000, debug=True)
    print(f"结果: {result}")
    
    if "API错误" not in result and "JSON解析失败" not in result:
        print("\n✅ API 调用成功！")
    else:
        print(f"\n❌ API 调用失败: {result}")

if __name__ == "__main__":
    test_api_call()
