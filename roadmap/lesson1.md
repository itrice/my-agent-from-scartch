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

##### Run
```bash
python .src/single/lesson1.py
```

#### === LLM怎么会出现幻觉式建议呢 ===

答案恰恰能帮你更准确地理解 LLM 的本质。

### 幻觉不是 bug，是 LLM 工作原理的必然产物

LLM 的核心训练目标是**"根据上文预测下一个最可能的词"**，它不是在"查数据库"或"回忆事实"。所以只要某个输出在**语言上看起来合理**，模型就有动力生成它——哪怕它在事实上是错的。

你那次的情况，模型面对的是：
- 用户问"查 5471"
- 工具返回"未找到该订单"

它要做的是"生成一段有帮助的回复"。而"未找到订单"这种场景下，**人类客服最自然的反应就是"您是不是记错号码了？比如是不是 4471？"**。模型从训练数据里见过大量这种对话模式，于是生成了类似的话术。它并不是"记得 4471"，而是**这个号码在语言上是一个合理的举例**。

### 幻觉产生的几个具体机制

**1. 训练目标是"像"，不是"对"**
模型被优化的方向是"生成人类会说的话"，而不是"生成真实的话"。这两者在大多数时候重合，但在边界情况下就会分叉。比如"给出一个可能正确的订单号"在语言上很自然，但事实上是编的。

**2. 模型没有"我不知道"的强激励**
面对"未找到"的结果，模型可以选择说"我无法确认其他号码"，但这在训练数据里出现的频率远低于"您是不是记错了，比如 XXX"。所以它倾向于生成更"有帮助"、更"像客服"的话，而不是更谨慎的话。

**3. 举例是一种高频语言模式**
"如果实际是 XXX 等其他号码"——这是中文里非常常见的句式。模型在生成这句话时，需要填一个号码进去，它会从**当前上下文 + 训练分布**里挑一个"看起来合理"的。4471 这种四位数订单号格式，正好符合它的分布。它甚至可能只是随机采样了一个常见数字组合。

**4. 上下文里的数字会"污染"采样**
虽然这次 4471 不在上下文里，但模型对数字的生成有很强的**格式惯性**。它见过太多"订单号是四位数字"的模式，所以会自然地生成一个四位数字，而不是说"我不该猜"。

### 为什么"工具调用"能减少但不能消除幻觉

你用了 Function Calling，模型在**需要事实**的时候会去调工具，这比纯聊天靠谱得多。但要注意：**工具只负责提供事实，不负责约束模型的措辞**。模型拿到"未找到"这个事实后，怎么组织语言、要不要举例、举什么例，仍然是它自由生成的部分。幻觉就藏在这个"自由生成"的缝隙里。

### 怎么抑制这类幻觉

**1. System prompt 明确约束**
```python
{"role": "system", "content": "只能依据工具返回结果回答。工具说未找到，就只说未找到，不要猜测、举例或建议其他订单号。"}
```
这是最直接的手段。你之前没加 system prompt，模型就按"默认客服人格"自由发挥了。

**2. 降低 temperature**
`temperature=0` 会让模型更倾向于高概率输出，减少"随机举例"的倾向。但注意它不能根除幻觉，只是让输出更保守、更可复现。

**3. 让工具返回更"结构化"的结果**
比如返回 `{"found": false, "message": "未找到"}`，而不是纯文本"未找到该订单"。模型拿到结构化数据后，更不容易自由发挥。

**4. 后处理校验**
对关键字段（如订单号）做正则提取，检查是否出现在工具返回里。不在就拦截或改写。这在生产环境很常见。

### 一个有用的心智模型

把 LLM 想象成一个**极度博学但从不查证、且非常想讨好你的实习生**：
- 你问它事实，它可能凭"印象"回答，而且答得很自信；
- 你给它工具，它会去查，但查完之后**怎么汇报**仍然靠它自己组织语言；
- 它不会说"我不确定"，因为训练数据里"不确定"往往不是最"有帮助"的回答。

所以工程上的原则是：**事实交给工具，措辞交给模型，但措辞要用 prompt 和校验兜底**。你这次遇到的"4471 举例"，正是"措辞自由发挥"的典型表现，加个 system prompt 就能明显改善。
