from agent import agent

if __name__ == "__main__":
    print("Trip Planner Agent started. Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        try:
            result = agent.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ]
                },
                config={
                    "configurable": {
                        "thread_id": "user_123"
                    }
                }
            )
            last_message = result['messages'][-1].content
            if isinstance(last_message, list):
                last_message = "\n".join(
                    block['text'] for block in last_message
                    if isinstance(block, dict) and block.get('type') == 'text'
                )
            print(f"\nAgent: {last_message}\n")
        except Exception as e:
            print(f"\n[Error] Something went wrong: {e}\nPlease try again.\n")
