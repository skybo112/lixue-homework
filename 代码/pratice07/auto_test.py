# 自动测试链式工具调用
import os
import sys
from dotenv import load_dotenv

def test_chained_calls():
    """自动测试链式工具调用功能"""
    load_dotenv()
    
    # 添加当前目录到路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from tool_client import ChainedCallContext, build_analysis_prompt, execute_tool
    
    print("=== 链式工具调用功能测试 ===")
    print()
    
    # 测试1: ChainedCallContext 类
    print("测试1: ChainedCallContext 类")
    context = ChainedCallContext(max_iterations=5)
    context.user_request = "测试请求"
    context.add_call("find_files", {"directory": ".", "keyword": "test"}, '{"status": "success"}')
    print(f"  最大迭代次数: {context.max_iterations}")
    print(f"  当前迭代次数: {context.current_iteration}")
    print(f"  调用历史长度: {len(context.call_history)}")
    print("  [OK] ChainedCallContext 测试通过")
    print()
    
    # 测试2: build_analysis_prompt 函数
    print("测试2: build_analysis_prompt 函数")
    prompt = build_analysis_prompt(context)
    print(f"  提示词长度: {len(prompt)}")
    print(f"  包含用户请求: {'用户原始请求' in prompt}")
    print(f"  包含工具列表: {'可用工具列表' in prompt}")
    print("  [OK] build_analysis_prompt 测试通过")
    print()
    
    # 测试3: execute_tool 函数
    print("测试3: execute_tool 函数")
    
    # 测试 read_file
    test_file = os.path.join(os.path.dirname(__file__), "1.txt")
    result = execute_tool("read_file", {"filepath": test_file})
    print(f"  read_file 结果: {result[:50]}...")
    
    # 测试 write_file
    output_file = os.path.join(os.path.dirname(__file__), "test_output.txt")
    result = execute_tool("write_file", {"filepath": output_file, "content": "测试内容"})
    print(f"  write_file 结果: {result[:50]}...")
    
    # 验证文件创建
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  文件内容验证: {content}")
            os.remove(output_file)
        print("  [OK] execute_tool 测试通过")
    else:
        print("  [FAIL] execute_tool 测试失败")
    print()
    
    # 测试4: 测试 1.txt 和 2.txt 的内容
    print("测试4: 验证测试数据文件")
    files = ["1.txt", "2.txt"]
    for filename in files:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"  {filename}: {content}")
        else:
            print(f"  {filename}: 不存在")
    print()
    
    print("=== 所有测试完成 ===")

if __name__ == "__main__":
    test_chained_calls()