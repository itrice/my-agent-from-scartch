import http.client
import json
import os
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
        {"model": model_name, "messages": messages},
        ensure_ascii=False,
    ).encode()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept-Encoding": "identity",
    }
    conn.request("POST", f"{p.path.rstrip('/')}/chat/completions", body=body, headers=headers)
    resp = conn.getresponse()
   
    data = json.loads(resp.read().decode("utf-8"))
    conn.close()
    return data["choices"][0]["message"]

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
    return "Reach the maximum number of iterations"
