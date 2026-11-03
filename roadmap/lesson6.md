## Target
Change multiple `tool_calls` within the same turn from serial execution to concurrent execution via `ThreadPoolExecutor`. When the LLM triggers several independent tool calls in one go, concurrent execution greatly reduces waiting time.

### Changes
```bash
 src/
 └── agent.py            # Refactor `tool_calls` execution inside `agent_loop`: switch from serial for-loop to concurrent execution using `ThreadPoolExecutor`.
```
本课只改 agent.py 一个文件，且只改 agent_loop 里的 tool_calls 执行部分。

### 核心概念
串行 vs 并发
串行：同一轮的 N 个 tool_calls 用 for 循环逐个执行，总耗时 = Σ(每个工具耗时)。
```ptyhon
for tc in msg["tool_calls"]:
    result = executor.execute(name, args)   # 第 2 个等第 1 个跑完才开始
```
并发：用 ThreadPoolExecutor 把 N 个 tool_calls 丢进线程池同时执行，总耗时 ≈ max(每个工具耗时)。
```python
with ThreadPoolExecutor(max_workers=len(tool_calls)) as pool:
    results = list(pool.map(_run, tool_calls))
```

### LLM 何时发多个 tool_calls
LLM 在一轮回复里可以返回多个 tool_calls，通常是无依赖的独立调用。例如：
```python
用户："同时读取 a.txt 和 b.txt"

LLM 回复（一轮 2 个 tool_calls）:
  tool_calls[0]: read_file({"path": "a.txt"})
  tool_calls[1]: read_file({"path": "b.txt"})
```
这两个 read_file 互不依赖——a.txt 的读取不需要等 b.txt 的结果。串行执行浪费时间，并发执行同时跑完。

### ThreadPoolExecutor 实现（src/mini_agent/agent.py:95）
```python
tool_calls = msg["tool_calls"]

def _run(tc):
    name = tc["function"]["name"]
    args = json.loads(tc["function"]["arguments"])
    result = executor.execute(name, args)
    print(f"  执行 {name} -> {result}")
    return tc["id"], str(result)

with ThreadPoolExecutor(max_workers=len(tool_calls)) as pool:
    results = list(pool.map(_run, tool_calls))

for tool_call_id, content in results:
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": content,
    })
```

### 关键点：

- max_workers=len(tool_calls)：线程数 = 本轮 tool_calls 数量，不多不少。
- pool.map：按 tool_calls 的原始顺序提交，结果也按原始顺序返回——results[0] 对应 tool_calls[0]。
- with 语句：ThreadPoolExecutor 的上下文管理器会在退出时自动 join()——等所有线程跑完才继续。
- 回灌顺序：pool.map 保证结果顺序与输入顺序一致，role=tool 消息按原序 append。

### 为什么这样设计

**为什么用线程而不是协程**

read_file/write_file 是 IO 密集型（磁盘读写），ThreadPoolExecutor 能在 IO 等待时切换到其他线程。 协程（asyncio）也能做，但需要把整个调用链改成 async——从 call_llm 到 executor.execute 全部 async 化，改动太大。 线程池是"最小改动 + 足够好的并发"的选择。

**为什么 max_workers = len(tool_calls)**

每轮的 tool_calls 数量通常很少（2-5 个），直接开对应数量的线程。 不需要复用线程池（每轮新建一个），因为 agent loop 本身是串行的——一轮跑完才进下一轮。

**为什么 pool.map 而不是 submit +**

pool.map 保证结果顺序与输入顺序一致。as_completed 是谁先完成谁先返回——顺序乱。 tool_calls 的回灌需要按原序（LLM 发的 tool_calls[0] 对应的 tool 消息要在前面），用 map 更安全。

**为什么权限闸门的 _ask_lock 在这里起作用**

v0.4 的 PermissionGate 里有 self._ask_lock = threading.Lock()。 并发执行时，如果两个 write_file 同时触发 ASK，没有锁会导致两个权限提示交错（终端乱码）。 锁保证同一时刻只有一个 ASK 交互在终端进行——v0.4 埋的伏笔在 v0.6 生效。