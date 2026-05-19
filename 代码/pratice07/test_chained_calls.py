import os
import sys
from dotenv import load_dotenv
from tool_client import execute_chained_tool_call

def run_test(test_name, user_request):
    """
    运行单个测试用例
    """
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print(f"{'='*60}")
    print(f"用户请求: {user_request}")
    print(f"{'-'*60}")
    
    # 加载环境变量
    load_dotenv()
    base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free")
    api_key = os.getenv("API_KEY", "")
    temperature = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("MAX_TOKENS", 2000))
    
    if not api_key:
        print("错误：未设置 API_KEY")
        return False
    
    # 执行链式工具调用
    result = execute_chained_tool_call(
        user_request, base_url, model, api_key, temperature, max_tokens,
        max_iterations=10, debug=True
    )
    
    print(f"\n{'-'*60}")
    print(f"最终结果:")
    print(result)
    print(f"{'='*60}\n")
    
    return True

def main():
    """
    运行所有测试用例
    """
    print("\n" + "="*60)
    print("链式工具调用测试套件")
    print("="*60)
    
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 测试用例1：检索 practice06 下包含 def 关键词的所有文件，汇总说明文件作用
    test1_request = f"检索 {os.path.join(project_root, '..', 'practice06')} 目录下包含 'def' 关键词的所有文件，并汇总说明这些文件的作用"
    run_test("测试1：文件搜索与汇总", test1_request)
    
    # 测试用例2：读取 practice07 中 1.txt、2.txt 内整数，求和并写入 result.txt
    test2_request = f"读取 {os.path.join(project_root, '1.txt')} 和 {os.path.join(project_root, '2.txt')} 中的正整数，求和后写入到 {os.path.join(project_root, 'result.txt')}"
    run_test("测试2：多文件运算", test2_request)
    
    # 验证测试2的结果
    result_file = os.path.join(project_root, 'result.txt')
    if os.path.exists(result_file):
        with open(result_file, 'r', encoding='utf-8') as f:
            print(f"\n✅ 测试2验证：result.txt 内容为: {f.read()}")
    else:
        print(f"\n❌ 测试2验证：result.txt 未生成")
    
    # 测试用例3：访问指定校园官网新闻链接，抓取内容总结并保存到 practice07/summary.txt
    test3_url = "https://www.pku.edu.cn"  # 使用北京大学官网作为示例
    test3_request = f"访问 {test3_url}，抓取页面内容并总结，保存到 {os.path.join(project_root, 'summary.txt')}"
    run_test("测试3：网页抓取总结", test3_request)
    
    # 验证测试3的结果
    summary_file = os.path.join(project_root, 'summary.txt')
    if os.path.exists(summary_file):
        with open(summary_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n✅ 测试3验证：summary.txt 已生成，内容长度: {len(content)} 字符")
    else:
        print(f"\n❌ 测试3验证：summary.txt 未生成")
    
    print("\n" + "="*60)
    print("所有测试完成")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
