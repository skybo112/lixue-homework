import os
import json
import requests
from urllib.parse import urlparse
from datetime import datetime
from dotenv import load_dotenv

# ====================== 工具函数 ======================
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
        # 确保有协议
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        resp = requests.get(url, timeout=10)
        status_code = resp.status_code
        content = resp.text
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
    }, ensure_ascii=False)

# ====================== 系统提示 ======================
def get_system_prompt():
    return f"""
你是一个可以调用工具的AI助手。
当前系统日期：{datetime.now().strftime('%Y年%m月%d日 %A')}

可用工具：
1. list_files(directory)
2. rename_file(directory, old_name, new_name)
3. delete_file(directory, filename)
4. create_file(directory, filename, content)
5. read_file(directory, filename)
6. curl(url)
7. get_current_date()

需要调用工具时，只返回如下严格JSON，不要加任何其他文字：
{{
  "tool_call": {{
    "function": "函数名",
    "params": {{
      "参数名": "值"
    }}
  }}
}}

不需要工具就直接自然回答。
"""

# ====================== LLM 请求（使用 requests）======================
def chat_with_tools(messages, base_url, model, api_key, temperature, max_tokens, debug=False):
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Python-ToolChatClient/1.0"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    try:
        resp = requests.post(url, json=data, headers=headers, timeout=30)
        if debug:
            print(f"\n[调试] HTTP状态码: {resp.status_code}")
            print(f"[调试] 响应前500字符: {resp.text[:500]}\n")
        
        if resp.status_code != 200:
            return f"API错误 (HTTP {resp.status_code}): {resp.text[:300]}"
        
        j = resp.json()
        if "choices" in j and len(j["choices"]) > 0:
            return j["choices"][0]["message"]["content"].strip()
        else:
            return f"API返回格式异常: {j}"
    except requests.exceptions.RequestException as e:
        return f"请求失败: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON解析失败: {str(e)}\n原始响应: {resp.text[:200]}"

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
        return json.dumps({"error": str(e)})

# ====================== 主程序 ======================
def main():
    # 加载 .env 文件
    load_dotenv()
    base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free")
    api_key = os.getenv("API_KEY", "")
    temperature = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("MAX_TOKENS", 1000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    if not api_key:
        print("错误：未设置 API_KEY，请在 .env 文件中配置。")
        return

    print("=== AI 终端对话（工具调用版）===")
    print(f"模型: {model}")
    print(f"接口: {base_url}")
    print("输入 exit 退出\n")

    history = [{"role": "system", "content": get_system_prompt()}]

    while True:
        user = input("\n你：").strip()
        if user.lower() == "exit":
            break
        if not user:
            continue

        history.append({"role": "user", "content": user})
        res = chat_with_tools(history, base_url, model, api_key, temperature, max_tokens, debug)
        print("AI：" + res)

        # 尝试解析工具调用
        try:
            res_json = json.loads(res)
            if "tool_call" in res_json:
                print("\n执行工具中...")
                tool_ret = execute_tool(res_json["tool_call"])
                print("工具结果：" + tool_ret)
                history.append({"role": "assistant", "content": res})
                history.append({"role": "tool", "content": tool_ret})
                summary = chat_with_tools(history, base_url, model, api_key, temperature, max_tokens, debug)
                print("AI：" + summary)
                history.append({"role": "assistant", "content": summary})
            else:
                history.append({"role": "assistant", "content": res})
        except json.JSONDecodeError:
            # 不是 JSON，直接作为普通回复
            history.append({"role": "assistant", "content": res})

if __name__ == "__main__":
    main()