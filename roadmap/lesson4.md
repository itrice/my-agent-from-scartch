## 这一课，学习了如何定义和使用PermissionGate

### 知识点：
**“默认允许”（fail-open）的策略**
```ptyhon
action = self.rules.get(tool_name, ALLOW)
```
self.rules.get(tool_name, ALLOW) 用的是字典 get() 的第二个参数：找不到 tool_name 时返回的默认值。

**互斥锁**

_ask_lock 是互斥锁，用来保证同一时间只有一个线程执行需要用户输入的权限确认。

isinstance(对象, 类型) 用来检查对象是否属于某种类型（或其子类），结果是 True 或 False。