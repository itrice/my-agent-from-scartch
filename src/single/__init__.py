from tools.base import ToolRegistry, ToolExecutor, Tool
from tools.calc import calculate_tool

registory=ToolRegistry()
registory.register(calculate_tool)

executor=ToolExecutor(registory)