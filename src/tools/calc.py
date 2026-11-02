"""Calculate tool: Calculate math expression"""
import re
from tools.base import Tool


def calculate(expression: str):
    """Calcuate a math expression"""
    if not re.fullmatch(r"[\d\s+\-*/().]+", expression):
        raise ValueError("Incorrect expression!")
    return str(eval(expression))


calculate_tool = Tool(
    name="calculate",
    description="Calculate a math experession",
    parameters={
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "Math expression, e.g. 3+5*2",
            }
        },
        "required": ["expression"],
    },
    handler=calculate
)
