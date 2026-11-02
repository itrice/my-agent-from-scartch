"""Smoke test for agent lesson3.
Validate import chains and function signatures without actually calling the LLM (to avoid network dependencies).
Run independently: `python tests/test_loop.py'
(Zero third-party dependences, standard library only.)
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"..","src"))

from agent import call_llm, agent_loop
from config import BASE_URL, MODEL_NAME, API_KEY, MAX_ITERATIONS

def test_import():
    assert callable(call_llm)
    assert callable(agent_loop)
    print("PASS: agent module imports succeed, call_llm/agent_loop callable.")

def test_config():
    assert BASE_URL, "BASE_URL could not be empty or blank"
    assert API_KEY,""
    assert MODEL_NAME,""
    assert isinstance(MAX_ITERATIONS, int) and MAX_ITERATIONS > 0
    print(f"PASS: config load succeed, (MODEL={MODEL_NAME}, MAX_ITERRATIONS={MAX_ITERATIONS})")

def test_agent_loop_signature():
    import inspect
    sig = inspect.signature(agent_loop)
    params = list(sig.parameters)
    assert params == ["messages"], f"agent_loop only accept message parameter, actully: {params}"
    print("PASS: agent_loop(messages) signature correct.")

if __name__ == "__main__":
    print("Run test ...")
    test_import()
    test_config()
    test_agent_loop_signature()
    print("test end.")