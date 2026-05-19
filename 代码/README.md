# Python AI 智能体开发教学项目

## 项目结构

```
├── practice01/          # 基础聊天客户端（流式响应）
│   └── llm_client.py    # LLM客户端代码
├── practice02/          # 工具调用（文件操作+网络访问）
│   ├── file_tools.py    # 文件操作和网络访问工具
│   └── tool_chat_client.py  # 支持工具调用的聊天客户端
├── practice03/          # 聊天记录总结（70%压缩+5W提取）
│   └── chat_summary_client.py  # 支持自动总结和5W日志提取
├── practice04/          # AnythingLLM文档仓库集成
│   └── anythingllm_chat_client.py  # 支持查询AnythingLLM数据
├── practice06/          # 技能系统（Skill System）
│   ├── tool_client.py   # 支持技能加载和调用的客户端
│   └── .agents/
│       └── skills/      # 技能目录
│           └── notice/  # 通知撰写技能
│               └── SKILL.md
├── practice07/          # 链式工具调用（Chained Tool Calls）
│   ├── tool_client.py   # 支持链式工具调用的客户端
│   ├── simple_test.py   # 简单测试脚本
│   ├── test_chained_calls.py  # 完整测试套件
│   ├── 1.txt, 2.txt     # 测试数据文件
│   └── result.txt      # 测试结果文件
├── .env                 # 环境配置文件
├── env.example          # 环境配置示例
├── .gitignore           # Git忽略文件
└── README.md            # 项目说明文档
```

## 环境配置

复制 `env.example` 为 `.env` 文件，配置以下内容：

### OpenAI Compatible LLM 配置
```env
BASE_URL=https://openrouter.ai/api/v1
MODEL=qwen/qwen3-coder:free
API_KEY=your_api_key_here
TEMPERATURE=0.7
MAX_TOKENS=1000
```

### AnythingLLM 文档仓库配置
```env
ANYTHING_LLM_API_KEY=your_anythingllm_api_key
ANYTHING_LLM_BASE_URL=http://localhost:3001
ANYTHING_LLM_WORKSPACE=your_workspace_id
```

## 代码功能说明

### practice01/llm_client.py - 基础聊天客户端

**功能用途：**
- 读取项目根目录的 `.env` 配置文件
- 使用 Python 标准 `http.client` 库访问 OpenAI 兼容的 LLM API
- 支持 HTTPS 连接
- 支持现代的聊天完成 API（Chat Completions）
- **流式响应支持**：实时显示AI回复，大幅提升用户体验
- 多轮对话功能：保留聊天历史，支持上下文对话

**实现的教学目标：**
1. **环境配置管理**：学习如何使用 `.env` 文件管理配置信息
2. **HTTP 客户端开发**：掌握 Python 标准库的 HTTP 客户端使用方法
3. **API 调用**：了解如何调用 OpenAI 兼容的 LLM API
4. **流式响应处理**：学习如何处理 Server-Sent Events (SSE) 流式数据
5. **错误处理**：学习如何进行健壮的错误处理
6. **代码结构**：学习如何组织清晰的代码结构

### practice02/tool_chat_client.py - 工具调用客户端

**功能用途：**
- 基于 practice01 的基础架构
- 支持工具调用功能
- 集成了 7 个工具：文件操作（6个）和网络访问（1个）

**可用工具：**
1. `list_files(directory)` - 列出目录文件
2. `rename_file(directory, old_name, new_name)` - 重命名文件
3. `delete_file(directory, filename)` - 删除文件
4. `create_file(directory, filename, content)` - 创建文件
5. `read_file(directory, filename)` - 读取文件
6. `curl(url)` - 访问外部网站
7. `get_current_date()` - 获取当前日期时间

**实现的教学目标：**
1. **工具调用机制**：学习如何实现 LLM 的工具调用能力
2. **系统提示词设计**：掌握如何设计有效的工具调用系统提示词
3. **工具集成**：了解如何集成外部工具到 LLM 系统
4. **JSON 处理**：学习 JSON 数据的序列化和反序列化

### practice03/chat_summary_client.py - 聊天记录总结客户端

**功能用途：**
- 基于 practice02 的功能
- 支持聊天记录自动总结（70%压缩+30%保留）
- 支持 5W 日志提取（每5轮自动提取）
- 完整的错误处理和重试机制

**核心功能：**

1. **自动总结**：
   - 当聊天轮数超过 5 轮或上下文超过 3000 字符时自动触发
   - 前 70% 的对话进行总结压缩
   - 后 30% 的对话保留原文

2. **5W 日志提取**：
   - 每 5 轮自动提取关键信息
   - 包含 Who、What、When、Where、Why
   - 保存到 `D:/chat-log/log.txt`

3. **超时重试机制**：
   - 超时时间 30 秒
   - 自动重试 2 次
   - 失败时记录错误到日志

**实现的教学目标：**
1. **聊天历史管理**：学习如何管理和优化聊天历史
2. **上下文压缩**：了解如何在保持对话连贯性的同时压缩上下文
3. **自动触发机制**：学习如何实现基于条件的自动触发功能
4. **总结生成**：掌握如何使用 LLM 进行内容总结
5. **错误处理和重试**：学习健壮的错误处理策略

### practice04/anythingllm_chat_client.py - AnythingLLM集成客户端

**功能用途：**
- 基于 practice03 的功能
- 支持查询 AnythingLLM 文档仓库
- 使用 subprocess 调用 curl 命令访问 API
- 当用户提到"文档仓库"、"文件仓库"、"仓库"时自动触发

**核心功能：**

1. **anythingllm_query 工具**：
   - 使用 subprocess 模块调用 curl 命令
   - 访问 `http://localhost:3001/api/v1/workspace/AI/chat` 接口
   - 使用 API 密钥进行认证

2. **智能触发规则**：
   - 检测"文档仓库"、"文件仓库"、"仓库"等关键词
   - 自动调用 AnythingLLM 查询

**实现的教学目标：**
1. **subprocess 模块使用**：学习如何调用外部命令
2. **curl 命令集成**：掌握如何使用 curl 访问 API
3. **AnythingLLM 集成**：了解如何与文档仓库系统交互
4. **API 认证**：学习如何使用 API 密钥进行认证

### practice06/tool_client.py - 技能系统客户端

**功能用途：**
- 基于 practice02 的架构
- 支持技能系统（Skill System）
- 自动读取 `.agents/skills` 目录下的技能
- 支持动态加载技能内容

**核心功能：**

1. **list_available_skills()**：
   - 读取 `.agents/skills` 目录下所有一级子目录
   - 解析每个技能的 `SKILL.md` 文件的 YAML front matter
   - 提取 `name` 和 `description` 字段
   - 返回技能列表供 LLM 使用

2. **load_skill_content(skill_name)**：
   - 根据技能名称加载技能正文内容
   - 提取 YAML front matter 之后的部分
   - 将技能内容通过 system prompt 发送给 LLM

3. **技能使用流程**：
   - 用户输入请求
   - LLM 判断是否需要使用技能，输出 `USE_SKILL:技能名称`
   - 系统加载技能内容
   - LLM 根据技能内容生成最终回复

**内置技能示例 - notice（通知撰写技能）：**
- 用于撰写、修改、润色通知文档
- 通知必须以"XX部"开头
- 如果用户未指定部门，使用"XX部"代替

**实现的教学目标：**
1. **技能系统设计**：学习如何设计可扩展的技能系统
2. **YAML 解析**：掌握如何解析 Markdown 文件的 YAML front matter
3. **动态配置**：了解如何实现动态加载配置
4. **技能调用机制**：学习如何实现 LLM 与外部技能的交互

### practice07/tool_client.py - 链式工具调用客户端

**功能用途：**
- 基于 practice02 的架构
- 支持链式工具调用（Chained Tool Calls）
- LLM 自主决策多步骤任务执行
- 自动管理调用历史和中间结果

**核心功能：**

1. **ChainedCallContext 类**：
   - 保存每一步工具调用记录
   - 存储中间结果供后续使用
   - 限制最大迭代次数，防止无限循环
   - 提供调用历史摘要

2. **build_analysis_prompt() 函数**：
   - 整合用户原始请求
   - 包含已执行工具调用历史
   - 定义决策规则和输出格式
   - 生成给 LLM 的分析提示

3. **execute_chained_tool_call() 函数**：
   - 循环调用 LLM 获取决策
   - 解析返回的 JSON 决策
   - 自动执行工具并回填上下文
   - 直到任务完成或达到最大迭代次数

4. **可用工具**：
   - `find_files(directory, keyword)` - 搜索包含关键词的文件
   - `read_file(filepath)` - 读取文件内容
   - `write_file(filepath, content)` - 写入文件内容
   - `fetch_web(url)` - 抓取网页内容

**链式调用流程：**
1. 用户输入请求
2. LLM 分析并决定是否需要调用工具
3. 执行工具并获取结果
4. 将结果反馈给 LLM
5. LLM 基于结果决定下一步操作
6. 重复步骤2-5，直到任务完成

**输出格式：**
任务完成：`{"done": true, "answer": "最终回答内容"}`
继续调用：`{"done": false, "tool_call": {"name": "工具名", "arguments": {"参数名": "参数值"}}}`

**实现的教学目标：**
1. **链式调用设计**：学习如何设计多步骤任务执行流程
2. **上下文管理**：掌握如何维护和管理调用历史
3. **决策机制**：了解如何实现 LLM 自主决策
4. **循环控制**：学习如何防止无限循环
5. **结果回填**：掌握如何将工具结果反馈给 LLM

## 运行方法

### 基础聊天
```bash
python practice01/llm_client.py
```

### 工具调用聊天
```bash
cd practice02
python tool_chat_client.py
```

### 聊天总结和5W提取
```bash
cd practice03
python chat_summary_client.py
```

### AnythingLLM文档查询
```bash
cd practice04
python anythingllm_chat_client.py
```

### 技能系统
```bash
cd practice06
python tool_client.py
```

**测试示例：**
1. 输入："写一个五一节放假的通知" → 输出以"XX部通知"开头
2. 输入："我是销售部的，写一个五一节放假的通知" → 输出以"销售部通知"开头

### 链式工具调用
```bash
cd practice07
python tool_client.py
```

**测试示例：**
1. 输入："检索 practice06 目录下包含 def 关键词的所有文件，并汇总说明文件作用"
2. 输入："读取 1.txt 和 2.txt 中的正整数，求和后写入到 result.txt"
3. 输入："访问 https://www.pku.edu.cn，抓取页面内容并总结，保存到 summary.txt"

**简单测试：**
```bash
cd practice07
python simple_test.py
```

## 日志输出

聊天记录日志保存在 `D:/chat-log/log.txt`，格式如下：

```
[2026-04-22 14:34:37]
【第 5 轮5W提取】
Who: 用户名称
What: 询问内容
When: 2026年4月22日
Where: AI终端对话系统
Why: 学习/开发需求
--------------------------------------------------

[2026-04-22 14:35:12]
【错误记录】
用户输入：xxx
错误：timeout
--------------------------------------------------
```

## 教学建议

### 基础阶段
1. 学习 HTTP 客户端和 API 调用
2. 了解 `.env` 配置文件管理
3. 掌握基础的多轮对话实现

### 进阶阶段
1. 学习工具调用机制
2. 掌握系统提示词设计
3. 实现文件操作和网络访问工具

### 高级阶段
1. 学习聊天历史管理和上下文压缩
2. 掌握自动总结和日志提取
3. 实现条件触发的自动功能

### 集成阶段
1. 集成第三方服务（如 AnythingLLM）
2. 学习 subprocess 调用外部命令
3. 实现复杂的多工具协同

## 常见问题解决

### 连接超时
- 检查 API 服务是否可用
- 确认网络连接正常
- 程序已自动配置 30 秒超时和 2 次重试

### API 认证失败
- 检查 API_KEY 是否正确
- 确认 API 服务提供商设置

### AnythingLLM 连接失败
- 确保 AnythingLLM 服务在 `http://localhost:3001` 运行
- 检查 `ANYTHING_LLM_API_KEY` 和 `ANYTHING_LLM_WORKSPACE` 配置

## 未来扩展方向

- 支持更多 LLM 提供商（Claude、Gemini 等）
- 添加对话历史保存和加载功能
- 实现更复杂的工具调用链
- 集成向量数据库
- 添加语音输入输出功能
- 支持多模态交互（图片、文件等）
- 实现多智能体协作
