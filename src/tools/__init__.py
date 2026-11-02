from tools.base import ToolRegistry, ToolExecutor, Tool
from tools.calc import calculate_tool
from tools.file import write_file_tool, read_file_tool

registry = ToolRegistry()
registry.register(calculate_tool)
registry.register(read_file_tool)
registry.register(write_file_tool)

executor = ToolExecutor(registry)