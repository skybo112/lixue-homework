import os
import json
import http.client
from urllib.parse import urlparse

def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    return env_vars

def test_stream():
    env = load_env()
    base_url = env.get("BASE_URL", "http://127.0.0.1:1234/v1")
    model = env.get("MODEL", "qwen/qwen3.5-9b")
    api_key = env.get("API_KEY", "any")
    temperature = float(env.get("TEMPERATURE", 0.7))
    max_tokens = int(env.get("MAX_TOKENS", 1000))

    print(f"测试流式响应...")
    print(f"模型: {model}")
    print(f"URL: {base_url}")

    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path

    messages = [{"role": "user", "content": "你好"}]

    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print("发送请求...")
        conn = http.client.HTTPConnection(host, timeout=60)
        conn.request("POST", f"{path}/chat/completions", body=json.dumps(data), headers=headers)
        resp = conn.getresponse()
        print(f"状态码: {resp.status}")
        print(f"响应头: {resp.getheaders()}")
        
        print("\n开始接收流式响应...")
        full_response = ""
        while True:
            chunk = resp.read(1024)
            if not chunk:
                break
            print(f"收到数据: {chunk}")
            chunk_str = chunk.decode('utf-8')
            full_response += chunk_str
        
        conn.close()
        print("\n完整响应:")
        print(full_response)
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_stream()
