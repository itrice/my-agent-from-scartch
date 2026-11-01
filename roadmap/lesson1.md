### Lesson 1. (lesson1.py)
.env file could include the environtment parameters. Useful.

这里，我测试出了AI的幻觉。
步骤：
1. 先运行脚本，使用工具中已经存在的订单号。让LLM使用工具，并且给出答案。
2. 我重新再次运行脚本，使用一个错误的订单号。LLM没有找到对应的数据，但是竟然记得我之前的正确单号，并且提示给出正确提示。
3. 为了避免模型幻觉，我使用了系统约束。后来再次执行，模型没有给出“盲猜”建议。

```python
TOOLS_SCHEMA [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "查询订单状态。当用户询问某个订单的物流或发货情况时使用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "订单号，例如 4471"}
                },
                "required": ["order_id"],
            },
        },
    }
]
```
```python

TOOL_MAP = {
    "get_order_status": get_order_status,
    "calculate": calculate,
}
```
```python
def execute_tool(name: str, args: dict) -> str:
    func = TOOL_MAP.get(name)
    if not func:
        return f"未知工具: {name}"
    return func(**args)
```

In lession1 case appeared 模型幻觉式建议. 
- I asked a property order_id at first, then I restart my program and changed a not existed order_id. The LLM suggest that I should to change my order_id into the orginal id.

```text
vscode ➜ /workspaces/agent1 (main) $ python ./coding_agent_from_scratch/lession1.py 
当前 model: deepseek-chat
当前 base_url: https://api.deepseek.com
直接调用工具: 已发货，UPS承运，预计2天送达
直接调用工具: 未找到该订单
直接调用工具: 28.0
execute tool: 已发货，UPS承运，预计2天送达
execute tool: 未知工具: get_name
===send to LLM===
 [{'role': 'user', 'content': '帮我查下5471号订单状态，并算下 99 乘以 8 是多少'}]
===send to LLM===
 [{'role': 'user', 'content': '帮我查下5471号订单状态，并算下 99 乘以 8 是多少'}, ChatCompletionMessage(content='我来帮您查询订单状态和计算乘积。', refusal=None, role='assistant', annotations=None, audio=None, function_call=None, tool_calls=[ChatCompletionMessageFunctionToolCall(id='call_00_s2b864uLXAc0h7fkROZa8201', function=Function(arguments='{"order_id": "5471"}', name='get_order_status'), type='function', index=0), ChatCompletionMessageFunctionToolCall(id='call_01_H7PXvfpl5Q2vymKkhPQN0172', function=Function(arguments='{"expression": "99*8"}', name='calculate'), type='function', index=1)]), {'role': 'tool', 'content': '未找到该订单', 'tool_call_id': 'call_00_s2b864uLXAc0h7fkROZa8201'}, {'role': 'tool', 'content': '792', 'tool_call_id': 'call_01_H7PXvfpl5Q2vymKkhPQN0172'}]
结果如下：

**订单查询**：未找到 5471 号订单。麻烦您确认一下订单号是否正确（您提到的是 5471，如果实际是 4471 等其他号码，我可以再帮您查一次）。

**计算结果**：99 × 8 = **792**
```

#### 所以完整的调用链是这样的
client = OpenAI(...)              # 创建连接器

↓

client.chat.completions.create(   # 真正发请求给 LLM
    model=model_name,             # 用哪个模型（从环境变量读的）
    messages=messages,            # 对话历史
    tools=TOOLS_SCHEMA,           # 告诉模型有哪些工具可用
)

↓

response.tool_calls               # 模型说“我要调工具”
response.content                  # 或模型直接给最终答案

### Run
```bash
python .src/single/lesson1.py
```
