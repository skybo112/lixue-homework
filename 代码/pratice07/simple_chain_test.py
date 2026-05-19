# 简单链式工具调用测试
import os
from dotenv import load_dotenv
from tool_client import execute_chained_tool_call

def test_simple():
    """简单测试链式工具调用"""
    load_dotenv()
    
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:1234/v1")
    model = os.getenv("MODEL", "qwen/qwen3.5-2b")
    api_key = os.getenv("API_KEY", "local")
    temperature = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("MAX_TOKENS", 2000))
    
    print("=== 简单链式工具调用测试 ===")
    print(f"模型: {model}")
    print(f"接口: {base_url}")
    print()
    
    # 简单测试请求
    request = "读取当前目录下的 1.txt 文件内容"
    print(f"请求: {request}")
    print("-"*50)
    
    result = execute_chained_tool_call(
        request, base_url, model, api_key, temperature, max_tokens,
        max_iterations=3, debug=True
    )
    
    print("\n结果:")
    print(result)

if __name__ == "__main__":
    test_simple()