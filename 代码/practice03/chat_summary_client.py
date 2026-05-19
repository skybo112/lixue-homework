import os
import json
import http.client
from urllib.parse import urlparse
from datetime import datetime

# ====================== 内置工具函数 ======================
def list_files(directory):
    try:
        files = []
        for item in os.listdir(directory):
            path = os.path.join(directory, item)
            size = os.path.getsize(path) if os.path.isfile(path) else 0
            files.append({
                "name": item,
                "path": path,
                "is_file": os.path.isfile(path),
                "size_bytes": size
            })
        return json.dumps({"status": "success", "files": files}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def rename_file(directory, old_name, new_name):
    try:
        old_path = os.path.join(directory, old_name)
        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        return json.dumps({"status": "success", "message": f"已重命名：{old_name} -> {new_name}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def delete_file(directory, filename):
    try:
        path = os.path.join(directory, filename)
        os.remove(path)
        return json.dumps({"status": "success", "message": f"已删除文件：{filename}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def create_file(directory, filename, content):
    try:
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return json.dumps({"status": "success", "message": f"已创建文件：{path}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def read_file(directory, filename):
    try:
        path = os.path.join(directory, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return json.dumps({"status": "success", "content": content}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "message": str(e)})

def curl(url):
    try:
        parsed = urlparse(url)
        if not parsed.scheme:
            url = "https://" + url
            parsed = urlparse(url)

        scheme = parsed.scheme
        host = parsed.netloc
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        if scheme == "https":
            conn = http.client.HTTPSConnection(host, timeout=10)
        else:
            conn = http.client.HTTPConnection(host, timeout=10)

        conn.request("GET", path)
        resp = conn.getresponse()
        status_code = resp.status
        content = resp.read().decode("utf-8", errors="ignore")
        conn.close()

        if len(content) > 2000:
            content = content[:2000] + "...（内容过长已截断）"

        return json.dumps({
            "status": "success",
            "url": url,
            "status_code": status_code,
            "content": content
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"status": "error", "url": url, "message": str(e)}, ensure_ascii=False)

def get_current_date():
    now = datetime.now()
    return json.dumps({
        "status": "success",
        "current_date": now.strftime("%Y年%m月%d日"),
        "weekday": now.strftime("%A"),
        "timestamp": now.timestamp(),
        "iso_format": now.isoformat()
    }, ensure_ascii=False, indent=2)

# ====================== 读取配置 ======================
def load_env():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

# ====================== 系统提示 ======================
def get_system_prompt():
    return f"""
你是一个可以调用工具的智能助手，当前系统日期为：{datetime.now().strftime('%Y年%m月%d日 %A')}

可用工具：
1. list_files(directory) 列出目录文件
2. rename_file(directory, old_name, new_name) 重命名文件
3. delete_file(directory, filename) 删除文件
4. create_file(directory, filename, content) 创建文件
5. read_file(directory, filename) 读取文件
6. curl(url) 访问外部网站，获取网页内容
7. get_current_date() 获取当前系统日期、星期、时间

需要调用工具时，严格返回如下JSON格式，不要加其他文字：
{{
  "tool_call": {{
    "function": "函数名",
    "params": {{
      "参数名": "值"
    }}
  }}
}}

不需要工具时，直接用自然语言回答。
"""

# ====================== LLM 对话（带重试）======================
def chat_with_tools(messages, base_url, model, api_key, temperature, max_tokens, retries=2):
    last_error = ""
    for attempt in range(retries):
        try:
            parsed_url = urlparse(base_url)
            host = parsed_url.netloc
            path = parsed_url.path

            data = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            conn = http.client.HTTPConnection(host, timeout=30)
            conn.request("POST", f"{path}/chat/completions", body=json.dumps(data), headers=headers)
            resp = conn.getresponse()
            response_data = resp.read().decode("utf-8", errors="replace")
            conn.close()

            if not response_data.strip():
                return "模型返回空响应"

            j = json.loads(response_data)
            if 'choices' in j and len(j['choices']) > 0:
                return j['choices'][0]['message']['content']
            elif 'error' in j:
                last_error = j['error'].get('message', str(j['error']))
                return f"API错误：{last_error}"
            else:
                return "模型返回格式错误"

        except Exception as e:
            last_error = str(e)
            if "timed out" in last_error.lower():
                print(f"[警告] 请求超时，第 {attempt + 1} 次重试...")
                continue
            return f"请求失败：{last_error}"

    # 所有重试都失败
    save_5w_log(f"【错误记录】\n用户输入：{messages[-1]['content'] if messages else 'N/A'}\n错误：{last_error}")
    return f"请求失败（已重试 {retries} 次）：{last_error}"

# ====================== 执行工具 ======================
def execute_tool(tool_call):
    try:
        func = tool_call['function']
        p = tool_call['params']

        if func == "list_files":
            return list_files(p['directory'])
        elif func == "rename_file":
            return rename_file(p['directory'], p['old_name'], p['new_name'])
        elif func == "delete_file":
            return delete_file(p['directory'], p['filename'])
        elif func == "create_file":
            return create_file(p['directory'], p['filename'], p['content'])
        elif func == "read_file":
            return read_file(p['directory'], p['filename'])
        elif func == "curl":
            return curl(p['url'])
        elif func == "get_current_date":
            return get_current_date()
        else:
            return json.dumps({"error": "未知工具"})
    except Exception as e:
        return json.dumps({"error": f"工具执行失败：{str(e)}"})

# ====================== 聊天记录总结（70%压缩+30%保留） ======================
def summarize_chat_history(history, base_url, model, api_key, temperature, max_tokens):
    try:
        system_msg = [m for m in history if m['role'] == 'system'][0]
        chat_msgs = [m for m in history if m['role'] in ['user', 'assistant']]

        total = len(chat_msgs)
        if total <= 2:
            return history

        split = int(total * 0.7)
        to_sum = chat_msgs[:split]
        to_keep = chat_msgs[split:]

        prompt = "请总结以下聊天记录，只保留核心关键信息：\n"
        for m in to_sum:
            prompt += f"{'用户' if m['role']=='user' else '助手'}：{m['content']}\n"

        sum_msgs = [
            {"role": "system", "content": "你是专业的聊天记录总结助手，简洁提炼核心内容"},
            {"role": "user", "content": prompt}
        ]
        summary = chat_with_tools(sum_msgs, base_url, model, api_key, temperature, max_tokens)

        new_history = [
            system_msg,
            {"role": "assistant", "content": f"【历史对话总结】{summary}"}
        ]
        new_history.extend(to_keep)
        return new_history
    except Exception as e:
        print(f"[警告] 总结失败：{str(e)}")
        return history

# ====================== 统计上下文长度 ======================
def calculate_context_length(history):
    return sum(len(m['content']) for m in history if 'content' in m)

# ====================== 统计聊天轮数 ======================
def calculate_chat_rounds(history):
    return len([m for m in history if m['role'] == 'user'])

# ====================== 5W 日志写入 ======================
def save_5w_log(content):
    log_dir = "D:/chat-log"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_path = os.path.join(log_dir, "log.txt")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}]\n{content}\n{'-' * 50}\n\n")

# ====================== 主程序 ======================
def main():
    env = load_env()
    base_url = env.get("BASE_URL", "http://127.0.0.1:1234/v1")
    model = env.get("MODEL", "qwen/qwen3.5-2b")
    api_key = env.get("API_KEY", "any")
    temperature = float(env.get("TEMPERATURE", 0.7))
    max_tokens = int(env.get("MAX_TOKENS", 1000))

    print("=== AI 终端对话（自动总结+5W提取）===")
    print(f"模型: {model}")
    print(f"地址: {base_url}")
    print("功能：每5轮自动提取5W关键信息 | 超过5轮或3000字符自动总结")
    print("-" * 50)

    history = [{"role": "system", "content": get_system_prompt()}]

    while True:
        user = input("\n你：").strip()
        if user.lower() == "exit":
            break
        if not user:
            continue

        history.append({"role": "user", "content": user})
        rounds = calculate_chat_rounds(history)
        length = calculate_context_length(history)
        print(f"[统计] 轮数：{rounds} | 总字符：{length}")

        # 每5轮触发5W提取（避免第一轮就触发）
        if rounds > 0 and rounds % 5 == 0:
            try:
                # 构建包含完整对话历史的5W提取提示
                history_text = ""
                for msg in history:
                    if msg['role'] == 'user':
                        history_text += f"用户：{msg['content']}\n"
                    elif msg['role'] == 'assistant' and 'content' in msg:
                        history_text += f"助手：{msg['content']}\n"

                prompt_5w = f"请按5W规则提取以下聊天的关键信息（Who、What、When、Where、Why），简洁回答：\n\n{history_text}"
                msg_5w = [{"role": "user", "content": prompt_5w}]
                info = chat_with_tools(msg_5w, base_url, model, api_key, 0.5, 800)
                save_5w_log(f"【第 {rounds} 轮5W提取】\n{info}")
                print(f"[系统] 已保存5W关键信息到 D:/chat-log/log.txt")
            except Exception as e:
                print(f"[警告] 5W提取失败：{str(e)}")

        # 自动总结
        if rounds > 5 or length > 3000:
            print("\n[系统] 触发自动总结，正在压缩聊天记录...")
            history = summarize_chat_history(history, base_url, model, api_key, temperature, max_tokens)
            print("[系统] 总结完成！继续对话~")

        # AI回复
        res = chat_with_tools(history, base_url, model, api_key, temperature, max_tokens)
        print("AI：", res)

        # 工具调用解析
        try:
            res_json = json.loads(res)
            if "tool_call" in res_json:
                tool_res = execute_tool(res_json["tool_call"])
                history.append({"role": "assistant", "content": res})
                history.append({"role": "tool", "content": tool_res})
                final = chat_with_tools(history, base_url, model, api_key, temperature, max_tokens)
                print("AI最终回复：" + final)
                history.append({"role": "assistant", "content": final})
            else:
                history.append({"role": "assistant", "content": res})
        except Exception as e:
            history.append({"role": "assistant", "content": res})

if __name__ == "__main__":
    main()
