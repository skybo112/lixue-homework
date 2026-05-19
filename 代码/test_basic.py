import os
import json
import http.client
from urllib.parse import urlparse

def test_basic():
    base_url = "http://127.0.0.1:1234/v1"
    model = "qwen/qwen3.5-9b"
    api_key = "any"

    print(f"测试基本连接...")
    print(f"URL: {base_url}")

    parsed_url = urlparse(base_url)
    host = parsed_url.netloc
    path = parsed_url.path

    data = {
        "model": model,
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False,
        "max_tokens": 100
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    try:
        print("发送请求...")
        conn = http.client.HTTPConnection(host, timeout=30)
        conn.request("POST", f"{path}/chat/completions", body=json.dumps(data), headers=headers)
        print("请求已发送，等待响应...")
        resp = conn.getresponse()
        print(f"状态码: {resp.status}")
        
        data = resp.read().decode()
        conn.close()
        
        print("响应内容:")
        print(data)
        
    except Exception as e:
        print(f"错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic()
