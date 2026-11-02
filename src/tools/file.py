"""read_file / write_file 工具：读写文本文件。"""

from tools.base import Tool


def read_file(path: str):
    """Read context from a file."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str):
    """Write context into a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Already write into file: {path}"


read_file_tool = Tool(
    name="read_file",
    description="Reading content from a file",
    parameters={
        "path": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "the path need to read"
                }
            },
            "required": ["path"]
        }
    },
    handler=read_file,
)

write_file_tool = Tool(
    name="write_file",
    description="将内容写入文本文件",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要写入的文件路径",
            },
            "content": {
                "type": "string",
                "description": "要写入的内容",
            },
        },
        "required": ["path", "content"],
    },
    handler=write_file,
)
