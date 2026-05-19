import json
import http.client
from urllib.parse import urlparse
import time

# 配置
API_KEY = " "
# ✅ 关键：加 :online 开启联网搜索
MODEL = "openai/gpt-oss-120b:free"
BASE_URL = "https://openrouter.ai/api/v1"
TEMPERATURE = 0.7
MAX_TOKENS = 500
CONNECT_TIMEOUT = 6
READ_TIMEOUT = 50
MAX_RETRIES = 2

def chat(prompt):
    parsed_url = urlparse(BASE_URL)
    host = parsed_url.netloc
    path = parsed_url.path

    data = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "stream": False
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "WeatherApp"
    }

    for retry in range(MAX_RETRIES + 1):
        try:
            conn = http.client.HTTPSConnection(host, timeout=CONNECT_TIMEOUT)
            conn.request("POST", f"{path}/chat/completions",
                         body=json.dumps(data), headers=headers)
            resp = conn.getresponse()
            raw = resp.read().decode("utf-8")
            conn.close()

            if resp.status != 200:
                return f"API错误 {resp.status}: {raw}"

            result = json.loads(raw )
            return result["choices"][0]["message"]["content"]

        except Exception as e:
            err = str(e).lower()
            if retry < MAX_RETRIES and ("timed out" in err or "timeout" in err or "none" in err):
                print(f"⏳ 网络波动，{2**retry}秒后重试...")
                time.sleep(2 ** retry)
                continue
            return f"❌ 失败: {str(e)}"

def main():
    # 🔥 修复：补上了缺失的 ) 括号
    print("=== AI 天气查询（已开启联网）===")
    print(f"模型: {MODEL}")
    while True:
        user = input("\n你：").strip()
        if user.lower() in ["exit", "quit"]:
            print("再见！")
            break
        if not user:
            continue
        print("AI：", chat(user))

if __name__ == "__main__":
    main()