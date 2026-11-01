from tools.base import ToolRegistry, ToolExecutor, Tool
from tools.calc import calculate_tool

registry = ToolRegistry()
registry.register(calculate_tool)

executor = ToolExecutor(registry)