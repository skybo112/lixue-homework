import os
import json
import requests
import re
from datetime import datetime
from dotenv import load_dotenv

# ====================== 技能管理函数 ======================

def list_available_skills(skills_dir=".agents/skills"):
    """
    读取技能列表，返回所有可用技能的名称和描述
    """
    skills = []
    
    # 确保技能目录存在
    if not os.path.isdir(skills_dir):
        return {"skills": []}
    
    # 遍历所有一级子目录
    for skill_name in os.listdir(skills_dir):
        skill_path = os.path.join(skills_dir, skill_name)
        if os.path.isdir(skill_path):
            skill_md_path = os.path.join(skill_path, "SKILL.md")
            if os.path.isfile(skill_md_path):
                try:
                    with open(skill_md_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # 提取 YAML front matter（--- 标记之间的内容）
                    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
                    if match:
                        front_matter = match.group(1)
                        # 解析 YAML 字段（简单解析，只处理 name 和 description）
                        name = None
                        description = None
                        for line in front_matter.split('\n'):
                            line = line.strip()
                            if line.startswith('name:'):
                                name = line[5:].strip()
                            elif line.startswith('description:'):
                                description = line[12:].strip()
                        
                        if name and description:
                            skills.append({
                                "name": name,
                                "description": description
                            })
                except Exception as e:
                    print(f"读取技能 {skill_name} 失败: {str(e)}")
    
    return {"skills": skills}

def load_skill_content(skill_name, skills_dir=".agents/skills"):
    """
    加载指定技能的正文内容（YAML front matter 之后的部分）
    """
    skill_path = os.path.join(skills_dir, skill_name)
    skill_md_path = os.path.join(skill_path, "SKILL.md")
    
    if not os.path.isfile(skill_md_path):
        return None
    
    try:
        with open(skill_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取 YAML front matter 之后的内容
        match = re.match(r'^---\n.*?\n---\n(.*)', content, re.DOTALL)
        if match:
            return match.group(1).strip()
        else:
            return content.strip()
    except Exception as e:
        print(f"加载技能 {skill_name} 内容失败: {str(e)}")
        return None

# ====================== 系统提示生成器 ======================

def get_system_prompt():
    """
    生成包含技能列表的系统提示
    """
    skills_data = list_available_skills()
    
    # 构建技能列表描述
    skills_desc = ""
    if skills_data["skills"]:
        skills_desc = "\n可用技能列表：\n"
        for skill in skills_data["skills"]:
            skills_desc += f"- {skill['name']}: {skill['description']}\n"
    
    return f"""
你是一个可以使用技能的AI助手。
当前系统日期：{datetime.now().strftime('%Y年%m月%d日 %A')}

{skills_desc}

## 技能使用规则：
1. 分析用户请求，如果需要使用某个技能，先输出：USE_SKILL:技能名称
2. 系统会加载该技能的详细内容后，你再根据技能要求进行回答
3. 如果不需要使用任何技能，直接回答用户即可

注意：不要输出任何JSON格式，直接使用自然语言回答或输出USE_SKILL指令。
"""

# ====================== LLM 请求函数 ======================

def chat_with_llm(messages, base_url, model, api_key, temperature, max_tokens, debug=False):
    """
    调用 LLM API
    """
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "Python-SkillClient/1.0"
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

# ====================== 主程序 ======================

def main():
    # 加载 .env 文件
    load_dotenv()
    base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("MODEL", "google/gemini-2.0-flash-lite-preview-02-05:free")
    api_key = os.getenv("API_KEY", "")
    temperature = float(os.getenv("TEMPERATURE", 0.7))
    max_tokens = int(os.getenv("MAX_TOKENS", 2000))
    debug = os.getenv("DEBUG", "false").lower() == "true"

    if not api_key:
        print("错误：未设置 API_KEY，请在 .env 文件中配置。")
        return

    print("=== AI 技能助手 ===")
    print(f"模型: {model}")
    print(f"接口: {base_url}")
    print("输入 exit 退出\n")

    # 获取技能列表
    skills_data = list_available_skills()
    print(f"已加载 {len(skills_data['skills'])} 个技能:")
    for skill in skills_data["skills"]:
        print(f"  - {skill['name']}: {skill['description'][:30]}...")
    print()

    # 初始化对话历史
    system_prompt = get_system_prompt()
    history = [{"role": "system", "content": system_prompt}]

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        history.append({"role": "user", "content": user_input})
        
        # 第一次调用：判断是否需要使用技能
        response = chat_with_llm(history, base_url, model, api_key, temperature, max_tokens, debug)
        print("AI：" + response)

        # 检查是否需要使用技能
        if response.startswith("USE_SKILL:"):
            skill_name = response[10:].strip()
            print(f"\n🔧 正在加载技能: {skill_name}")
            
            # 加载技能内容
            skill_content = load_skill_content(skill_name)
            if skill_content:
                print("技能内容已加载")
                # 将技能内容添加到对话历史
                history.append({"role": "assistant", "content": response})
                history.append({"role": "system", "content": f"技能 {skill_name} 内容：\n{skill_content}"})
                
                # 第二次调用：根据技能内容回答
                final_response = chat_with_llm(history, base_url, model, api_key, temperature, max_tokens, debug)
                print("AI：" + final_response)
                history.append({"role": "assistant", "content": final_response})
            else:
                print(f"❌ 无法加载技能 {skill_name}")
                history.append({"role": "assistant", "content": f"抱歉，无法加载技能 {skill_name}"})
        else:
            # 不需要技能，直接回答
            history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
