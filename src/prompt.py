"""Build the agent's system prompt from layered components.

Inspired by OpenCode's layered approach (header/environment/custom), this minimal
version follows mini_agent's incremental development: header (identity) +
core_rules (behavior) + environment (runtime context).
Custom instructions (loaded from AGENTS.md) are deferred until the file tools
are complete in v0.8.
"""

import os
import sys
from datetime import date

# ============================================================
# 1. header: identity layer that tells the model which mini_agent agent it is
# ============================================================


def header(agent_name: str = "build") -> str:
    """Return the identity prompt for the selected mini_agent agent.

    The parameter supports multiple agents and sub-agents; currently only
    ``build`` is implemented. Add ``explore`` or ``plan`` here in the future.
    """
    agents = {
        "build": (
            "You are a programming agent. "
            "You complete programming tasks by using tools. You can currently read, "
            "write, and edit files and perform mathematical calculations; support "
            "for running commands and tests will be added later. "
            "Your goal is to independently complete basic programming tasks, not just chat."
        )
        # Reserved for a future lesson; not implemented yet:
        # "explore": "You are the agent's explore sub-agent and only inspect the codebase...",
        # "plan": "You are the agent's planning sub-agent and only create plans...",
    }
    return agents.get(agent_name, agents["build"])

# ============================================================
# 2. environment: context layer that dynamically injects runtime information
# ============================================================


def environment() -> str:
    """Dynamically inject runtime context.

    Use only the standard library to obtain the working directory, Git status,
    platform, and date. This helps the model resolve relative paths, choose
    platform-appropriate commands, and account for the current date.
    """
    cwd = os.getcwd()  # current working directory
    is_git = _detcet_git(cwd)

    return "\n".join([
        "<env>",
        f" Working directory: {cwd}"
        f" Is directory a git repo: {'yes' if is_git else 'no'}"
        f" Platform: {sys.platform}"
        f" Today's date: {date.today().isoformat()}"
        "</env>",
    ])


def _detcet_git(cwd: str) -> bool:
    """Walk up the directory tree looking for .git to detect a Git repository.

    This uses directory traversal only and does not depend on the Git executable,
    in keeping with mini_agent's self-contained design. It may miss worktrees and
    submodules; improve it later if needed.
    """
    p = os.path.abspath(cwd)
    while True:
        if os.path.isdir(os.path.join(p, ".git")):
            return True
        parent = os.path.dirname(p)
        if parent == p:
            return False
        p = parent

# ============================================================
# 3. core_rules: static behavior rules shared by all agents
#


_CORE_RULES = """<rules>
# Tone and style
- Be concise and direct. Output is displayed in a command line and uses GitHub-flavored Markdown.
- Do not use emoji unless the user explicitly requests them.
- Tool results are fed back to you; do not repeat them in your response.
- After making code changes or performing file operations, do not summarize what you did unless asked.

# Professional objectivity
- Prioritize technical accuracy and truth over agreeing with the user's assumptions.
- When uncertain, investigate first (read files and inspect code) rather than agreeing based on guesses.
- If the user's understanding is incorrect, say so and correct it objectively instead of agreeing blindly.

# Tool usage
- Prefer using tools to complete tasks instead of relying on conversation alone.
- Provide complete, valid tool arguments. Use absolute paths or paths relative to the working directory.
- Independent tool calls in the same round may be issued together and will run concurrently.

# Safety
- The permission gate will prompt for approval before writing files; this is expected behavior.
- Do not guess URLs unless you are confident they will help with the programming task.
- Tool failures raise exceptions and stop the loop by design, keeping the core logic clear.
</rules>"""

# ============================================================
# 4. build_system_prompt: prompt assembly entry point
# ============================================================


def build_system_prompt(agent_name: str = "build") -> str:
    """Assemble the complete system prompt: identity, behavior rules, and environment.

    Return a string to use as the content of messages[0].
    """
    return "\n\n".join([
        header(agent_name),
        _CORE_RULES,
        environment()
    ])
