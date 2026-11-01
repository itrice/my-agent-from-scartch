import sys
from agent import agent_loop

if __name__ == "__main__":
    messages = [{"role":"system","content":"You are assistant."}]
    if len(sys.argv) > 1:
        messages.append({"role":"user","content": sys.argv[1]})
        reply = agent_loop(messages)
        print(reply)

    while True:
        try:
            user_input = input("\nYou:").strip()
        except(EOFError, KeyboardInterrupt):
            break
        if not user_input or user_input.lower() in ("exit","quit","bye"):
            break
        messages.append({"role":"user","content": user_input})
        reply = agent_loop(messages)
        print(reply)
        
