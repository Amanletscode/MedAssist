from llm import LLMClient

llm = LLMClient()

def chat():
    print("MedAssist AI Agent")
    print("-------------------")

    history = []  # memory

    while True:
        user = input("\nYou: ")
        if user.lower() in ["exit", "quit"]:
            break

        history.append({"role": "user", "content": user})

        messages = [
            {"role": "system", "content": "You are a helpful AI assistant."}
        ] + history

        reply = llm.ask(messages)

        history.append({"role": "assistant", "content": reply})

        print("\nAI:", reply)

if __name__ == "__main__":
    chat()
