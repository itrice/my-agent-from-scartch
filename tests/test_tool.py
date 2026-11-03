"""Smoke tests for mini_agent v0.3 tools.

Validate Tool/ToolRegistry/ToolExecutor and calculate/read_file/write_file.
Run independently with: python tests/test_tools.py
"""

import os, sys, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__),"..","src"))

from tools import registry, executor
from tools.base import ToolRegistry, Tool, ToolExecutor
from tools.permission import ALLOW, DENY, ASK, PermissionPolicy, PermissionGate

def test_registry():
    names = [t.name for t in registry.list_tools()]
    assert names == ["calculate", "read_file", "write_file"], names
    print("PASS: registry includes calculate/read_file/write_file")

def test_calculate():
    result = executor.execute("calculate", {"expression":"3+3*2"})
    assert result == "9", result
    print("PASS: calculate 3+3*2 == 9")

def test_calculate_invalid():
    result = executor.execute("calculate", {"expression":"import os"})
    assert "failed" in result, result
    print("PASS: calculate rejects illegal characters")

def test_read_file():
    content = "test string"
    # Use a temporary file.
    with tempfile.NamedTemporaryFile(mode="w+", encoding="utf-8", delete=True) as temp_file:
        temp_file.write(content)
        temp_file.flush()
        path = temp_file.name        
        result = executor.execute("read_file",{"path":path})
        assert isinstance(result, str) and result.strip(), result
        print("PASS: read_file read examples/test_input.txt succeed")

def test_write_file():
    with tempfile.TemporaryDirectory() as tmp:
        target = os.path.join(tmp, "out.txt")
        result = executor.execute("write_file", {"path":target, "content":"Hi"})
        assert "succeed" in result, result
        with open(target, "r", ecoding="utf-8") as f:
            assert f.read() == "Hi"
    print("PASS: wirite_file succeed")

def test_registry_duplicate():
    reg = ToolRegistry()
    reg.register(Tool("dummy","dummy description", {}, None))
    try:
        reg.register(Tool("dummy","dummy description", {}, None))
        assert False, "Throw ValueError"
    except ValueError:
        pass
    print("PASS: registry reject duiplicate registion")

def test_executor_unknow():
    try:
        executor.execute("nonexist",{})
        assert False, "Jaja failed"
    except ValueError:
        pass
    print("PASS: executor thorw exception with unknow tool")

def test_permission_deny():
    # Verify that a DENY policy rejects write_file.
    gate = PermissionGate(PermissionPolicy({"write_file": DENY}))
    exec_deny = ToolExecutor(registry, gate=gate)
    result = exec_deny.execute("write_file", {"path": "/tmp/x.txt", "context": "X"})
    assert "Permission reject" in result, result
    print("PASS: write_file rejected by DENY policy")

if __name__ == "__main__":
    test_calculate()
    test_calculate_invalid()
    test_read_file()
    #test_write_file()
    test_registry_duplicate()
    test_executor_unknow()
    # test_permission_deny()