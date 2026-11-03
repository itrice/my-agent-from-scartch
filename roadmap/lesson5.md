## Lesson5 Streaming Mode
### Target
Change `call_llm` from non-streaming to streaming: render LLM response incrementally with a typewriter effect in the terminal. Also handle cross-chunk assembly of `tool_calls` under streaming mode.

### Changes
```bash
 src/
 └── agent.py            # call_llm changes into streaming mode (stream=True + SSE + chunk)
```

### Core Concepts
v0.4 Non-streaming: The LLM returns a complete JSON after finishing generation. `call_llm` parses it and returns the message. The terminal waits until the LLM finishes generating everything before showing the response — noticeable lag for long outputs.

v0.5 Streaming: The LLM sends chunks incrementally via Server-Sent Events (SSE), with each chunk containing a small piece of content. `call_llm` reads and assembles chunks one by one, printing in real time — text appears character by character in the terminal for a snappier feel.

### SSE (Server-Sent Events)
The streaming response is a text stream, with one `data:` event per line:
```bash
data: {"choices":[{"delta":{"content":"你"}}]}
data: {"choices":[{"delta":{"content":"好"}}]}
data: {"choices":[{"delta":{"content":"！"}}]}
data: [DONE]
```

The `delta` within each chunk can include:

- `content`: partial text, printed incrementally
- `tool_calls`: fragmented tool call data, requiring cross-chunk assembly
- `data: [DONE]`: stream termination signal

Streaming implementation for `call_llm` (src/mini_agent/agent.py:12)
Request changes:
```bash
body = json.dumps({
    "model": MODEL,
    "messages": messages,
    "stream": True,              # ← 新增：开启流式
    "tools": registry.schemas(),
}, ensure_ascii=False).encode()

headers = {
    ...
    "Accept": "text/event-stream",  # ← 新增：声明接收 SSE
}
```

Parsing changes: read the response line by line and parse each `data:` event.
```bash
content_parts = []
tool_calls_acc = {}

for raw in resp:
    line = raw.decode("utf-8").strip()
    if not line or not line.startswith("data:"):
        continue
    if line == "data: [DONE]":
        break
    chunk = json.loads(line[6:])
    delta = chunk["choices"][0].get("delta", {})

    # content 边收边打印（打字机效果）
    if delta.get("content"):
        content_parts.append(delta["content"])
        print(delta["content"], end="", flush=True)

    # tool_calls 的 arguments 跨 chunk 拼接
    for tc in delta.get("tool_calls", []):
        idx = tc.get("index", 0)
        slot = tool_calls_acc.setdefault(idx, {
            "id": "", "type": "function",
            "function": {"name": "", "arguments": ""},
        })
        if tc.get("id"):
            slot["id"] = tc["id"]
        fn = tc.get("function", {})
        if fn.get("name"):
            slot["function"]["name"] = fn["name"]
        if fn.get("arguments"):
            slot["function"]["arguments"] += fn["arguments"]
```