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

def test_non_stream():
    env = load_env()
    base_url = env.get("BASE_URL", "http://127.0.0.1:1234/v1")
    model = env.get("MODEL", "qwen/qwen3.5-9b")
    api_key = env.get("API_KEY", "any")
    temperature = float(env.get("TEMPERATURE", 0.7))
    max_tokens = int(env.get("MAX_TOKENS", 1000))

    print(f"测试非流式响应...")
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
        "stream": False
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
        data = resp.read().decode()
        conn.close()
        print("响应内容:")
        print(data)
        j = json.loads(data)
        if 'choices' in j:
            print("\n解析成功:")
            print(j["choices"][0]["message"]["content"])
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_non_stream()
