# 链式工具调用完整测试
import os
from dotenv import load_dotenv
from tool_client import execute_chained_tool_call

def run_test():
    """运行链式工具调用测试"""
    load_dotenv()
    
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:1234/v1")
    model = os.getenv("MODEL", "qwen/qwen3.5-2b")
    api_key = os.getenv("API_KEY", "local")
    temperature = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("MAX_TOKENS", 2000))
    
    print("=== 链式工具调用测试 ===")
    print(f"模型: {model}")
    print(f"接口: {base_url}")
    print()
    
    # 测试用例1：文件搜索
    print("="*60)
    print("测试1：查找包含 def 的文件")
    print("="*60)
    request1 = "查找当前目录下包含 'def' 关键词的所有Python文件，并说明它们的作用"
    print(f"请求: {request1}")
    print("-"*60)
    result1 = execute_chained_tool_call(
        request1, base_url, model, api_key, temperature, max_tokens,
        max_iterations=5, debug=True
    )
    print("\n结果:")
    print(result1)
    print()
    
    # 测试用例2：文件运算
    print("="*60)
    print("测试2：读取文件并求和")
    print("="*60)
    request2 = f"读取 {os.path.join(os.getcwd(), '1.txt')} 和 {os.path.join(os.getcwd(), '2.txt')} 中的数字，求和后写入到 {os.path.join(os.getcwd(), 'result.txt')}"
    print(f"请求: {request2}")
    print("-"*60)
    result2 = execute_chained_tool_call(
        request2, base_url, model, api_key, temperature, max_tokens,
        max_iterations=5, debug=True
    )
    print("\n结果:")
    print(result2)
    
    # 验证结果
    result_file = os.path.join(os.getcwd(), 'result.txt')
    if os.path.exists(result_file):
        with open(result_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            print(f"\n验证结果文件: {content}")
    print()

if __name__ == "__main__":
    run_test()