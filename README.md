# Function-Calling Agent

## 项目简介
纯 Python 手写的 Function-Calling Agent。

## 技术栈
- Python 3.8+
- requests
- 大模型API

## 功能
- 计算器
- 获取时间
- 查询备忘录
- 添加备忘录

## 运行方式
1. `pip install -r requirements.txt`
2. `export ZHIPU_API_KEY="你的Key"`
3. `python3 Function-Calling_Agent.py`

##运行示例
```
👤 你: 3+5
🔧 调用工具：tool_calculator，结果：计算结果：8
🤖 Agent: 根据计算，3+5等于8。

👤 你: 现在几点了
🔧 调用工具：tool_get_time，结果：🕐 当前时间：2026-10-15 22:30:00
🤖 Agent: 现在是2026年10月15日22点30分。

👤 你: 添加备忘录 明天下午开会
🔧 调用工具：tool_memo_add，结果：✅ 已添加备忘录：明天下午开会
🤖 Agent: 好的，已经帮您添加了备忘录。
```
