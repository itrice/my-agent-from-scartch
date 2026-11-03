import sys
from agent import agent_loop
from prompt import build_system_prompt

if __name__ == "__main__":
    messages = [{"role":"system","content":build_system_prompt()}]
    if len(sys.argv) > 1:
        messages.append({"role":"user","content": sys.argv[1]})
        reply = agent_loop(messages)
        # print(reply)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except(EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("exit","quit","bye"):
            break
        messages.append({"role":"user","content": user_input})
        reply = agent_loop(messages)
        print(reply)
        
