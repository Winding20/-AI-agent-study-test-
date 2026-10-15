import requests
import sqlite3
import os
import json
import datetime

# ============ ① 配置 ============
API_KEY = os.environ.get("ZHIPU_API_KEY")
if not API_KEY:
    raise ValueError("❌ 请设置环境变量 ZHIPU_API_KEY")

URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# ============ ② 定义工具函数（本地） ============
def tool_calculator(expr):
    """计算器"""
    try:
        result = eval(expr)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"

def tool_get_time():
    """获取当前时间"""
    return f"🕐 当前时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

def tool_memo_query(keyword=None):
    conn = sqlite3.connect('memo.db')
    cursor = conn.cursor()
    if keyword:
        cursor.execute("SELECT content, created_at FROM memo WHERE content LIKE ?", (f'%{keyword}%',))
    else:
        cursor.execute("SELECT content, created_at FROM memo LIMIT 10")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "📭 暂无相关备忘录"
    return "\n".join([f"📝 {row[1]} - {row[0]}" for row in rows])
def tool_memo_add(content):
    """添加备忘录"""
    conn = sqlite3.connect('memo.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS memo (id INTEGER PRIMARY KEY, content TEXT, created_at TEXT)")
    cursor.execute("INSERT INTO memo (content, created_at) VALUES (?, ?)",
                   (content, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    return f"✅ 已添加备忘录：{content}"

# ============ ③ 工具字典（本地） ============
TOOL_MAP = {
    "tool_calculator": tool_calculator,
    "tool_get_time": tool_get_time,
    "tool_memo_query": tool_memo_query,
    "tool_memo_add": tool_memo_add,       
}

# ============ ④ 工具描述（发给模型的“说明书”） ============
tools = [
    {
        "type": "function",
        "function": {
            "name": "tool_calculator",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expr": {"type": "string", "description": "数学表达式，如 1+2"}
                },
                "required": ["expr"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_get_time",
            "description": "获取当前系统时间",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_memo_query",
            "description": "查询备忘录",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "tool_memo_add",
            "description": "添加一条备忘录",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "备忘录内容"}
                },
                "required": ["content"]
            }
        }
    }
]

# ============ ⑤ 主程序 ============

def main():
    messages = []  # 对话历史

    while True:
        try:
            user_input = input("\n👤 你: ").strip()
        except UnicodeDecodeError:
            print("⚠️ 输入编码错误，请重试")
            continue

        if user_input.lower() in ["exit", "quit", "退出"]:
            break
        if not user_input:
            continue        # 把用户输入加到历史
        messages.append({"role": "user", "content": user_input})

        # ---- 第一次请求 ----
        resp = requests.post(
            url=URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "glm-4-flash",
                "messages": messages,
                "tools": tools
            }
        )

        data = resp.json()
        msg = data["choices"][0]["message"]

        # ---- 判断：调工具还是直接回答 ----
        if msg.get("tool_calls"):
            # 模型要调工具
            tool_call = msg["tool_calls"][0]
            func_name = tool_call["function"]["name"]
            args = json.loads(tool_call["function"]["arguments"])

            # 本地执行
            func = TOOL_MAP[func_name]
            result = func(**args)
            print(f"🔧 调用工具：{func_name}，结果：{result}")

            # 结果回传
            messages.append(msg)
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })

            # ---- 第二次请求 ----
            resp2 = requests.post(
                url=URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "glm-4-flash",
                    "messages": messages,
                    "tools": tools
                }
            )

            data2 = resp2.json()
            final_msg = data2["choices"][0]["message"]
            final_answer = final_msg["content"]
            messages.append(final_msg)

        else:
            # 模型直接回答
            final_answer = msg["content"]
            messages.append(msg)

        print(f"🤖 Agent: {final_answer}")

if __name__ == "__main__":
    main()
