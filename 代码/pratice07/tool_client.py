import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# ====================== 链式调用上下文类 ======================
class ChainedCallContext:
    def __init__(self, max_iterations=10):
        self.max_iterations = max_iterations
        self.current_iteration = 0
        self.call_history = []
        self.intermediate_results = {}
        self.user_request = ""
        
    def add_call(self, tool_name, arguments, result):
        self.call_history.append({
            "step": len(self.call_history) + 1,
            "tool_name": tool_name,
            "arguments": arguments,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_intermediate_result(self, key, value):
        self.intermediate_results[key] = value
        
    def increment_iteration(self):
        self.current_iteration += 1
        
    def is_max_reached(self):
        return self.current_iteration >= self.max_iterations
        
    def get_history_summary(self):
        summary = []
        for call in self.call_history:
            summary.append(f"步骤{call['step']}: 调用 {call['tool_name']}")
        return "\n".join(summary)

# ====================== 工具函数 ======================
def find_files(directory, keyword):
    try:
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                if filename.endswith(('.py','.txt','.md')):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            if keyword in f.read():
                                files.append({"path": filepath})
                    except:
                        pass
        return json.dumps({"status":"success","files":files}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status":"error","message":str(e)}, ensure_ascii=False)

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return json.dumps({"status":"success","content":content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status":"error","message":str(e)}, ensure_ascii=False)

def write_file(filepath, content):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return json.dumps({"status":"success","message":f"已写入：{filepath}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status":"error","message":str(e)}, ensure_ascii=False)

def fetch_web(url):
    try:
        if not url.startswith(('http://','https://')):
            url = 'https://'+url
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return json.dumps({"status":"success","content":resp.text[:5000]}, ensure_ascii=False)
        else:
            return json.dumps({"status":"error","code":resp.status_code}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status":"error","message":str(e)}, ensure_ascii=False)

# ====================== 提示词构建函数 ======================
def build_analysis_prompt(context):
    prompt = f"""你是一个智能工具调用助手，必须按照以下规则执行：

用户请求：{context.user_request}

已执行的调用历史：{context.get_history_summary() or '无'}

可用工具列表（必须使用这些工具）：
- read_file(filepath): 读取指定文件的内容
- write_file(filepath, content): 将内容写入指定文件
- find_files(directory, keyword): 在指定目录搜索包含关键词的文件
- fetch_web(url): 获取网页内容

思考：
1. 如果需要读取文件内容，使用 read_file
2. 如果需要保存结果，使用 write_file  
3. 如果需要搜索文件，使用 find_files
4. 如果需要获取网页内容，使用 fetch_web
5. 如果已经有足够信息可以回答，直接回答

输出格式（严格JSON格式，不要输出任何其他文字）：
- 需要调用工具时输出：{{"done":false,"tool_call":{{"name":"工具名称","arguments":{{"参数名":"参数值"}}}}}}
- 任务完成时输出：{{"done":true,"answer":"最终答案"}}

现在分析用户请求，决定下一步操作：
"""
    return prompt

# ====================== LLM 调用 ======================
def chat_with_llm(messages, base_url, model, api_key, temperature, max_tokens, debug=False):
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        if debug:
            print(f"[调试] 状态码: {resp.status_code}")
            print(f"[调试] 响应: {resp.text[:500]}")
        if resp.status_code != 200:
            return f"API错误 {resp.status_code}"
        j = resp.json()
        return j["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"请求失败: {str(e)}"

# ====================== 工具执行 ======================
def execute_tool(tool_name, args):
    if tool_name == "find_files":
        return find_files(args.get("directory"), args.get("keyword"))
    elif tool_name == "read_file":
        return read_file(args.get("filepath"))
    elif tool_name == "write_file":
        return write_file(args.get("filepath"), args.get("content"))
    elif tool_name == "fetch_web":
        return fetch_web(args.get("url"))
    return json.dumps({"status":"error","message":"未知工具"}, ensure_ascii=False)

# ====================== 链式执行 ======================
def execute_chained_tool_call(user_request, base_url, model, api_key, temperature=0.7, max_tokens=2000, max_iterations=10, debug=False):
    context = ChainedCallContext(max_iterations)
    context.user_request = user_request
    messages = [
        {"role": "system", "content": build_analysis_prompt(context)},
        {"role": "user", "content": user_request}
    ]
    while not context.is_max_reached():
        context.increment_iteration()
        response = chat_with_llm(messages, base_url, model, api_key, temperature, max_tokens, debug)
        try:
            decision = json.loads(response)
            if decision.get("done"):
                return decision["answer"]
            tool = decision.get("tool_call")
            if tool is None:
                return f"错误：模型返回了空的工具调用，请重新描述你的需求"
            if not isinstance(tool, dict) or "name" not in tool:
                return f"错误：工具调用格式不正确: {tool}"
            res = execute_tool(tool["name"], tool.get("arguments", {}))
            context.add_call(tool["name"], tool.get("arguments", {}), res)
            messages.append({"role":"assistant","content":response})
            messages.append({"role":"user","content":f"执行结果：{res}"})
            messages[0]["content"] = build_analysis_prompt(context)
        except Exception as e:
            return f"错误：{str(e)}，响应：{response[:200]}"
    return "达到最大迭代次数"

# ====================== 主程序（强制本地千问） ======================
def main():
    # ✅ 强制锁定本地 LLM Anything 千问
    base_url = "http://127.0.0.1:1234/v1"
    model = "qwen/qwen3.5-2b"
    api_key = "local"
    temperature = 0.7
    max_tokens = 2000
    debug = True

    print("=== 本地千问 链式工具调用 ===")
    print(f"模型：{model}")
    print(f"接口：{base_url}")
    print("输入 exit 退出\n")

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue
        print("\n🔍 处理中...")
        result = execute_chained_tool_call(
            user_input, base_url, model, api_key, temperature, max_tokens, debug=debug
        )
        print(f"\nAI：{result}")

if __name__ == "__main__":
    main()