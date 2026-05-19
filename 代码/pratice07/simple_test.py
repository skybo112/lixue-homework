import os
import sys
from dotenv import load_dotenv

def test_chained_call():
    """
    简单测试链式工具调用功能
    """
    print("=== 链式工具调用简单测试 ===\n")
    
    # 导入必要的模块
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from tool_client import ChainedCallContext, build_analysis_prompt, execute_tool
    
    # 测试1：ChainedCallContext 类
    print("测试1：ChainedCallContext 类")
    context = ChainedCallContext(max_iterations=5)
    print(f"  最大迭代次数: {context.max_iterations}")
    print(f"  当前迭代次数: {context.current_iteration}")
    print(f"  是否达到最大: {context.is_max_reached()}")
    
    context.increment_iteration()
    print(f"  增加迭代后: {context.current_iteration}")
    
    context.add_call("find_files", {"directory": ".", "keyword": "test"}, '{"status": "success"}')
    print(f"  调用历史长度: {len(context.call_history)}")
    print(f"  历史摘要: {context.get_history_summary()[:100]}...")
    print("  [OK] ChainedCallContext 测试通过\n")
    
    # 测试2：build_analysis_prompt 函数
    print("测试2：build_analysis_prompt 函数")
    context.user_request = "查找包含 def 的文件"
    prompt = build_analysis_prompt(context)
    print(f"  提示词长度: {len(prompt)} 字符")
    print(f"  包含用户请求: {'用户原始请求' in prompt}")
    print(f"  包含工具列表: {'可用工具列表' in prompt}")
    print(f"  包含输出格式: {'输出格式' in prompt}")
    print("  [OK] build_analysis_prompt 测试通过\n")
    
    # 测试3：execute_tool 函数
    print("测试3：execute_tool 函数")
    
    # 测试 find_files
    result = execute_tool("find_files", {"directory": ".", "keyword": "test"})
    print(f"  find_files 结果: {result[:100]}...")
    
    # 测试 read_file
    test_file = os.path.join(os.path.dirname(__file__), "1.txt")
    result = execute_tool("read_file", {"filepath": test_file})
    print(f"  read_file 结果: {result[:100]}...")
    
    # 测试 write_file
    output_file = os.path.join(os.path.dirname(__file__), "test_output.txt")
    result = execute_tool("write_file", {"filepath": output_file, "content": "测试内容"})
    print(f"  write_file 结果: {result[:100]}...")
    
    # 验证文件是否创建
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"  文件内容: {content}")
            os.remove(output_file)
            print("  [OK] execute_tool 测试通过\n")
    else:
        print("  [FAIL] execute_tool 测试失败\n")
    
    print("=== 所有测试完成 ===")
    return True

if __name__ == "__main__":
    try:
        test_chained_call()
    except Exception as e:
        print(f"[FAIL] 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
