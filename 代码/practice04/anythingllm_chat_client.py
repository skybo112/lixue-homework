import os
import json
import subprocess
from dotenv import load_dotenv

# 加载.env配置
load_dotenv()

# ====================== 本地大模型配置 ======================
BASE_URL = os.getenv("BASE_URL")
MODEL = os.getenv("MODEL")
LLM_API_KEY = os.getenv("API_KEY")

# ====================== 🔥 修复：兜底配置，绝对不会为None ======================
ANY_API_KEY = os.getenv("ANYTHING_LLM_API_KEY", "62EZ9X2-1J0M2FJ-M0Y2MEV-90MEYE9")
ANY_BASE_URL = os.getenv("ANYTHING_LLM_BASE_URL", "http://localhost:3001")
ANY_WORKSPACE = os.getenv("ANYTHING_LLM_WORKSPACE", "default")
ANY_API = f"{ANY_BASE_URL}/api/v1/workspace/{ANY_WORKSPACE}/chat"

# ====================== 核心工具 ======================
def anythingllm_query(message: str) -> str:
    print("\n🔍 【调试】正在调用AnythingLLM API...")

    try:
        payload = json.dumps({"message": message}, ensure_ascii=False)
        curl_cmd = [
            "curl", "-s", "--connect-timeout", "10",
            "-X", "POST", ANY_API,
            "-H", f"Authorization: Bearer {ANY_API_KEY}",
            "-H", "Content-Type: application/json",
            "-d", payload
        ]

        print(f"【调试】请求地址: {ANY_API}")
        print(f"【调试】请求payload: {payload}")

        result = subprocess.run(
            curl_cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace'
        )

        print(f"【调试】curl返回码: {result.returncode}")
        print(f"【调试】原始响应: {result.stdout}")

        if result.returncode != 0:
            return f"❌ curl错误码{result.returncode}：网络/地址错误"
        stdout = result.stdout or ""
        if not stdout.strip():
            return "⚠️ 工作区无文档 或 文档未嵌入"

        api_data = json.loads(stdout)
        return api_data.get("textResponse", "✅ API调用成功，但无内容返回")

    except Exception as e:
        return f"❌ 异常：{str(e)}"

# ====================== 主程序 ======================
def main():
    print("=== 文档仓库助手（最终修复版）===")
    print("输入 exit 退出\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() == "exit":
            break
        
        # 只要问文档/仓库，直接调用
        print("AI：正在读取文档仓库...")
        res = anythingllm_query(user_input)
        print(f"AI：{res}\n")

if __name__ == "__main__":
    main()