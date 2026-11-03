"""Define tools, a registry, and an executor.

The executor checks permissions before calling a handler and returns handler errors as strings.
"""

from dataclasses import dataclass
from typing import Any, Callable

from tools.permission import PermissionGate

# ==========================
# 1. Tool Definition
# ==========================

@dataclass
class Tool:
    """A complete tool definition.

    name        : Name exposed to the LLM.
    description : Description exposed to the LLM.
    parameters  : Parameter schema exposed to the LLM.
    handler     : Python callable invoked to execute the tool.
    """
    name: str
    description: str
    parameters: dict
    handler: Callable[..., Any]

    def to_llm_schema(self):
        """Convert this tool to the OpenAI function-calling format."""
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
    """Registry for registering, looking up, and listing tools and their LLM schemas."""

    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        """Register a tool."""
        if tool.name in self._tools:
            raise ValueError(f"Tool already exists: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        """Get a tool by name."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name]

    def list_tools(self):
        """List all registered tools."""
        return list(self._tools.values())

    def schema(self):
        """Return the LLM schemas for all registered tools."""
        return [tool.to_llm_schema() for tool in self._tools.values()]

# ===========
# 3. Tool Executor
# ===========

class ToolExecutor:
    """Look up tools, check permissions, and execute their handlers."""
    def __init__(self, registry: ToolRegistry, gate: PermissionGate | None = None):
        self.registry = registry
        self.gate = gate or PermissionGate()

    def execute(self, name: str, arguments: dict):
        """Execute a named tool with the supplied arguments."""
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