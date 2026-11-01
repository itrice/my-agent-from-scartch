import http.client
import json
import os

from tools import registry, executor
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
# === load value from env ===
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")  # 可选，不设置则用 OpenAI 官方
model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # 可选，给个默认值
max_iterations = int(os.getenv("MAX_ITERATIONS"))

def call_llm(messages):
    """ none stream invoce LLM, retrun assistant message dict.
    using http.client + Accept-Encoding: identity avoid gateway 502.
    """

    p = urlparse(base_url)
    conn = http.client.HTTPSConnection(p.hostname, p.port or 443, timeout=120)
    body = json.dumps(
        {"model": model_name, "messages": messages,"tools": registry.schema(),},
        ensure_ascii=False,
    ).encode()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
    }
    try:
        conn.request("POST", f"{p.path.rstrip('/')}/chat/completions", body=body, headers=headers)
        resp = conn.getresponse()
        response_body = resp.read().decode("utf-8")
    finally:
        conn.close()

    try:
        data = json.loads(response_body)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            f"LLM API returned a non-JSON response (HTTP {resp.status} {resp.reason})"
        ) from error

    if not isinstance(data, dict):
        raise RuntimeError("LLM API returned an unexpected response format")

    if resp.status >= 400 or "error" in data:
        error = data.get("error", data)
        if isinstance(error, dict):
            error = error.get("message", error)
        raise RuntimeError(f"LLM API request failed (HTTP {resp.status}): {error}")

    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise RuntimeError(
            f"LLM API response is missing choices (HTTP {resp.status}); "
            f"response keys: {', '.join(data.keys())}"
        )

    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise RuntimeError("LLM API response is missing the assistant message")
    return message

def agent_loop(messages):
    """Loop: Call LLM -> Print response -> No tool_calls end.
    The caller maintains and supports the messages, and current function only appends message.
    """
    for i in range(max_iterations):
        msg = call_llm(messages)
        messages.append(msg)

        print(f"\n=== [{i+1}] LLM Response ===")
        print(msg.get("content",""))

        # no tool_calls = response's finally, over.
        if not msg.get("tool_calls"):
            return msg.get("content","")

        for tc in msg["tool_calls"]:
            name=tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"])
            print(f" 决策调用:{name}({args})")

            result = executor.execute(name, args)
            print(f"Execute result: {result}")
            messages.append({
                "role": "tool",
                "tool_call_id": tc["id"],
                "content": str(result),
            })

    return "Reach the maximum number of iterations"
