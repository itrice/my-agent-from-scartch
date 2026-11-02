### Fist tool


Learned:
1. @dataclass

| 问题              | 答案                                            |
| :---------------- | :---------------------------------------------- |
| @dataclass 干嘛的 | 自动生成 __init__/__repr__/__eq__，少写样板代码 |
| 要装吗            | 不用，标准库 dataclasses                        |
| 怎么写            | 类里只声明带类型注解的字段                      |
| 适合什么          | 以"存数据"为主的简单类，如你的 Tool             |

2. Callable[..., Any]

3. __init__.py 

标记"这是一个包", 是包被 import 时自动执行的代码。Python 3.3+ 的变化：没有 __init__.py 也能导入

4. After each tool call, the result needs to be appended to the messages.

```python
messages.append({
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call.id,
                })
```

5. 发给 LLM 的 message 中，`role` 字段的具体取值取决于你所使用的 API 规范或模型提供商。主流方案（如 OpenAI、Claude、Mistral）通常支持或要求以下几种核心角色，但在不同平台间存在细微差异。
   1. **主流 LLM API 支持的角色类型**

    | 角色 (`role`)   | 核心作用                                                                                             | 主要支持平台/说明                                        |
    | :-------------- | :--------------------------------------------------------------------------------------------------- | :------------------------------------------------------- |
    | **`system`**    | 设定模型的背景、行为准则或全局指令（如“你是一个 helpful assistant”）。通常作为对话的第一条消息出现。 | OpenAI、Mistral、Azure OpenAI                            |
    | **`user`**      | 代表终端用户的输入，即你向模型提出的问题或发出的指令。                                               | 几乎所有主流平台（OpenAI, Claude, Mistral, AWS Bedrock） |
    | **`assistant`** | 代表模型生成的回复。在多轮对话中，需要将历史回复以此角色传回，以维持上下文。                         | 几乎所有主流平台（OpenAI, Claude, Mistral, AWS Bedrock） |
    | **`tool`**      | 用于回传外部工具（或函数）的执行结果。当模型请求调用函数后，你需要以此角色将函数输出喂回给模型。     | OpenAI 及其兼容接口（如 Azure OpenAI）                   |
    | **`developer`** | 类似于 `system`，但在某些新规范（如 OpenAI 的 Harmony 格式或较新的 Azure API）中用于传递开发者指令。 | OpenAI 部分新接口、Azure OpenAI                          |
   
   2. **重要差异与注意事项**
   
      **Claude (Anthropic) 的特殊性:**
        Claude 的 Messages API 在核心参数上通常**仅明确区分 `user` 和 `assistant`** 两种角色 。如果你需要设定系统级指令（System Prompt），在 Claude 中通常不是通过 `role: "system"` 的消息来实现，而是使用 API 请求中独立的 `system` 顶层参数（具体取决于你使用的 SDK 或云平台封装）。

      **函数调用（Function Calling）的配套角色:**
         如果你在使用工具调用功能，`role: "tool"` 是必不可少的。它的出现是为了将 `assistant` 发起的 `tool_calls` 结果准确对应回模型，从而让模型基于工具返回的数据继续生成自然语言回答 。
         
      **接口兼容性:**
        虽然 OpenAI 定义了 `system` / `user` / `assistant` / `tool` 的标准，但部分开源模型（如通过 vLLM 或 Ollama 部署时）可能仅严格支持前三种，对 `tool` 的支持取决于具体的推理框架版本。

6. os.path.join("src", "/data", "file.txt")
   
   --> "/data/file.txt" 为什么？因为 "/data" 带了前导斜杠，Python 会极其死板地认为这就是一个绝对路径的开头。于是它毫不留情地把前面的 "src" 丢掉了。

7. 在 Python 里，__name__ 是一个内置变量。它的值取决于文件是怎么被执行起来的：

   直接运行（比如你在终端敲 python app.py，或者在 VS Code 里点击了“运行”按钮）：
此时 Python 会把当前文件的 __name__ 自动设为 "__main__"。
👉 所以 if "__main__" == "__main__": 条件成立，下面的代码会被执行。

   被导入（比如在另一个文件里写了 import app）：
此时 Python 会把被导入的 app.py 里的 __name__ 设为它的模块名（也就是 "app"）。
👉 所以 if "app" == "__main__": 条件不成立，下面的代码会被跳过。