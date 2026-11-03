"""Streaming agent loop: call the LLM, execute tools if requested, feed results back, and repeat until a text response or the iteration limit."""

import http.client
import json
import os

from concurrent.futures import ThreadPoolExecutor
from tools import registry, executor
from urllib.parse import urlparse
from config import BASE_URL, API_KEY, MODEL_NAME, MAX_ITERATIONS


def call_llm(messages):
    """Call the LLM in streaming mode, accumulate chunks, and return a message dict matching the non-streaming format.

    Send Accept-Encoding: identity to avoid gateway issues with compressed responses.
    Print content as it arrives (typewriter effect) and concatenate tool-call arguments across chunks.
    """

    p = urlparse(BASE_URL)
    conn = http.client.HTTPSConnection(p.hostname, p.port or 443, timeout=120)
    body = json.dumps(
        {"model": MODEL_NAME, "messages": messages,
            "stream": True, "tools": registry.schema(), },
        ensure_ascii=False,
    ).encode()
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
        "Accept": "text/event-stream",
    }
    conn.request(
        "POST", f"{p.path.rstrip('/')}/chat/completions", body=body, headers=headers)
    resp = conn.getresponse()

    content_parts = []
    tool_calls_acc = {}

    for raw in resp:
        line = raw.decode("utf-8").strip()
        if not line or not line.startswith("data:"):
            continue
        if line == "data: [DONE]":
            break
        chunk = json.loads(line[6:])  # 'data: '
        choices = chunk.get("choices", [])
        if not choices:
            continue
        delta = choices[0].get("delta", [])

        # Print content as it arrives (typewriter effect).
        #
        # {"delta": {"role": "assistant"}}
        # {"delta": {"content": "Hello"}}
        # {"delta": {"content": ", world!"}}
        #
        if delta.get("content"):
            content_parts.append(delta["content"])
            print(delta["content"], end="", flush=True)

        # Concatenate tool-call arguments across chunks.
        for tc in delta.get("tool_calls", []):
            idx = tc.get("index", 0)
            # slot references tool_calls_acc[idx] and is used below to update this tool call.
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

    conn.close()
    message = {"role": "assistant",
               "content": "".join(content_parts) or None}
    if tool_calls_acc:
        message["tool_calls"] = [
            tool_calls_acc[i] for i in sorted(tool_calls_acc)
        ]
    return message


def agent_loop(messages):
    """循环：调 LLM -> 有 tool_calls 就执行并回灌 -> 无则结束。

    【messages 契约】本函数以副作用方式向传入的 messages 列表追加内容，
    调用方应跨轮复用同一个 list 对象，不要重新构造。每轮会 append：
      1. assistant 消息（含 content 和/或 tool_calls）
      2. 若有 tool_calls：对应每条的 role=tool 结果消息
    返回值是最终 assistant 回复的 content 字符串（仅用于打印），
    真正的上下文状态已写入 messages，调用方无需再手动 append assistant 回复。

    注意：若因达到 MAX_ITERATIONS 提前返回，messages 可能停在
    "有 tool_calls 但无对应 tool 结果"的半截状态，下一轮调用前
    调用方有责任处理该状态（当前实现未做清理，长任务可能触发协议错误）。
    """
    for i in range(MAX_ITERATIONS):
        print(f"\n=== [{i+1}] LLM 回复 ===")
        msg = call_llm(messages)
        messages.append(msg)

        for tc in msg.get("tool_calls", []):
            print(
                f"  决策调用: {tc['function']['name']}({tc['function']['arguments']})")
        # No tool calls means the LLM response is final.
        if not msg.get("tool_calls"):
            return msg.get("content", "")

        # Run this round's tool calls concurrently; pool.map preserves their original order.
        # Feed the results back as role=tool messages.
        tool_calls = msg["tool_calls"]

        def _run(tc):
            name = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            result = executor.execute(name, args)
            print(f" Execute Result:{name}({args})")
            return tc["id"], str(result)

        with ThreadPoolExecutor(max_workers=len(tool_calls)) as pool:
            results = list(pool.map(_run, tool_calls))

        for tc_id, content in results:
            messages.append({
                "role": "tool",
                "tool_call_id": tc_id,
                "content": content,
            })

    return "Reach the maximum number of iterations"
