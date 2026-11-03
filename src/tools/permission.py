"""Permission policy: a three-state gate (allow/deny/ask) before tool execution.

The ask lock ensures that only one thread at a time prompts the user for confirmation.
"""
import threading

# ============================================================
# 1. Action constants
# ============================================================

ALLOW, DENY, ASK = "allow", "deny", "ask"

# ============================================================
# 2. Permission rules (hard-coded, consistent with the style of config.py)
# ============================================================

PERMISSION_RULES = {
    "read_file": ALLOW,
    "calculate": ALLOW,
    "write_file": ASK,
}

# ============================================================
# 3. PermissionPolicy
# ============================================================
class PermissionPolicy:
    """
    One-dimensional permission policy: tool_name -> action.
    Keep args available for a future two-dimensional policy: (tool_name, pattern).
    """
    def __init__(self, rules: dict | None = None):
        self.rules = rules if rules is not None else PERMISSION_RULES
        self._approved = set()  # Tool names approved for this policy instance.

    def check(self, tool_name: str, args: dict | None = None) -> str:
        action = self.rules.get(tool_name, ALLOW)
        if action == ALLOW:
            return ALLOW
        if action == DENY:
            return DENY
        if action == ASK:
            if tool_name in self._approved:
                return ALLOW
            return ASK
        return ALLOW

    def approve(self, tool_name: str):
        """Remember approval for this tool for the lifetime of this policy instance."""
        self._approved.add(tool_name)

# ============================================================
# 4. PermissionGate: the gate called by the executor
# ============================================================
class PermissionGate:
    """
    Encapsulate the check, user interaction, and lock.
    The executor calls gate.guard(name, args), which returns None to allow or a string with the rejection reason.
    """
    def __init__(self, policy: PermissionPolicy | None = None):
        self.policy = policy or PermissionPolicy()
        self._ask_lock = threading.Lock()

    def guard(self, tool_name: str, args: dict) -> str | None:
        """
        Return None to allow execution, or a string with the rejection reason.
        """
        action = self.policy.check(tool_name, args)

        if action == DENY:
            return f"Reject: rules do not allow {tool_name}"
        if action == ASK:
            with self._ask_lock:
                choice = input(f"Allow execute {tool_name}({args})?[once/always/reject] "
                               ).strip().lower()
                if choice == "always":
                    self.policy.approve(tool_name)
                elif choice != "once":
                    return f"Permission reject: Reject executing {tool_name}"
            return None