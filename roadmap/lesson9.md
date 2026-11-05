# 第 9 课：权限系统升级

## 本课目标
把权限从一维 tool_name -> action 升级为二维 (tool_name, pattern) -> action，支持按文件路径模式（或命令模式）细粒度控制权限。为 v0.10 run_shell 的命令模式权限铺路。

## 核心概念
### 1. Rule 三元组：从嵌套 dict 到扁平 list

lesson4 的规则是嵌套 dict：`{"write_file": "ask"}`，只能按工具名控制。

lesson9 内部存扁平 `list[dict]`，每条规则是三元组：

```python
[
    {"permission": "read_file", "pattern": "*", "action": "allow"},
    {"permission": "write_file", "pattern": "*", "action": "ask"},
    {"permission": "read_file", "pattern": "*.env", "action": "deny"},
]
```

构造函数 `_from_config()` 兼容两种格式：

```python
# 简单格式（一维兼容，pattern 默认 "*"）
PermissionPolicy({"write_file": "ask"})

# 复杂格式（二维，按 pattern 细控）
PermissionPolicy({"read_file": {"*": "allow", "*.env": "deny"}})
```

### 2. check()：fnmatch + findLast

```python
def check(self, tool_name: str, pattern: str = "*") -> str:
    merged = self._rules + self._approved
    for rule in reversed(merged):
        if fnmatch.fnmatch(tool_name, rule["permission"]) and fnmatch.fnmatch(pattern, rule["pattern"]):
            return rule["action"]
    return ASK  # 未匹配默认 ask
```

**关键设计**：
- `fnmatch.fnmatch()` 做 wildcard 匹配（`*` 匹配任意字符，`?` 匹配单字符）
- `reversed()` 从后往前找，`findLast` 语义——后出现的规则优先级更高
- 未匹配任何规则时默认 `ask`（安全优先）

**为什么用 findLast？** 运行时 `approved` 规则追加在 `self._approved` 末尾，`merged = rules + approved`，`reversed` 先扫 approved，自然覆盖前面的 `ask` 规则。无需显式删除旧规则。

### 3. approve()：存 (tool_name, pattern)

```python
# lesson4：只存工具名
def approve(self, tool_name: str):
    self._approved.add(tool_name)

# lesson9：存 (tool_name, pattern)
def approve(self, tool_name: str, pattern: str = "*"):
    self._approved.append({
        "permission": tool_name, "pattern": pattern, "action": "allow"
    })
```

效果：用户对 `write_file` + `*.txt` 选 `always` 后，后续写 `.txt` 文件免问，但写 `.py` 文件仍会问。

### 4. _extract_pattern()：从 args 提取 pattern

```python
@staticmethod
def _extract_pattern(tool_name: str, args: dict) -> str:
    if tool_name == "run_shell":
        return args.get("command", "*")  # v0.10 接入 BashArity 后改为泛化模式
    if tool_name in ("read_file", "write_file", "edit_file"):
        return args.get("path", "*")
    return "*"
```

`PermissionGate.guard()` 调 `_extract_pattern()` 从工具参数提取 pattern，传给 `check()`。对非 shell 工具，pattern 是文件路径，`fnmatch` 用 `*.env` 等模式匹配文件名。