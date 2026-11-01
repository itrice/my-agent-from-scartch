### Fist tool


Learned:
1. @dataclass

| 问题 | 答案 |
|:---|:---|
| @dataclass 干嘛的 | 自动生成 __init__/__repr__/__eq__，少写样板代码 |
| 要装吗 | 不用，标准库 dataclasses |
| 怎么写 | 类里只声明带类型注解的字段 |
| 适合什么 | 以"存数据"为主的简单类，如你的 Tool |

2. Callable[..., Any]

3. __init__.py 

标记"这是一个包", 是包被 import 时自动执行的代码。Python 3.3+ 的变化：没有 __init__.py 也能导入

