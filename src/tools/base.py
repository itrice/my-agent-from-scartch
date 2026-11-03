""" Define tool, registry center, executor
Lesson3: No permisson gate.
Executor call handler directly, catch exception to LLM.
"""

from dataclasses import dataclass
from typing import Any, Callable

from tools.permission import PermissionGate

# ==========================
# 1. Tool Definition
# ==========================

@dataclass
class Tool:
    """A full tool definiation
    name        : tool's name for LLM
    description : tool's description for LLM
    parameters  : tool's parameters for LLM
    handler     : Realtime executing python function
    """
    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]

    def to_llm_schema(self):
        """Transform into OpenAI function calling format"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

# ======================
# Tool registry
# ======================
class ToolRegistry:
    """
    Tool Registry Center
    
    Responsibilities:
    1. Register tools
    2. Look up a tool by name
    3. Get all tools
    4. Generate tool schema for LLM
    """

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        if tool.name in self._tools:
            raise ValueError(f"Tool already exists: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Get a tool by name"""
        if name not in self._tools:
            raise ValueError(f"Unknow tool: {name}")
        return self._tools[name]

    def list_tools(self):
        """List all registed tools"""
        return list(self._tools.values())

    def schema(self):
        """Get all tool's LLM Schema"""
        return [tool.to_llm_schema() for tool in self._tools.values()]

# ===========
# 3. Tool Executor
# ===========

class ToolExecutor:
    """Tool Executor
    Registry find tool
    Executor run tool    
    """
    def __init__(self, registry: ToolRegistry, gate: PermissionGate | None = None):
        self.registry = registry
        self.gate = gate or PermissionGate()

    def execute(self, name: str, arguments: dict):
        """Executor function by tool'name and parameters."""
        tool = self.registry.get(name)
        # Permission Gate
        denied = self.gate.guard(name, arguments)
        if denied:
            print(f"[Permission] {denied}")
            return denied
        
        print(f"[Executor] run Tool:{name}")
        print(f"[Executor] parameters: {arguments}")

        try:
            result = tool.handler(**arguments)
        except Exception as e:
            return f"Tool execute failed: {e}"
        return result