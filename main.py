from core.agent import decide_and_execute
from core.llm_client import ask_llm 


def main():
    print("Welcome to the Industrial AI Copilot!")
    
    while True:
        user_input = input("Please enter your question: ")
        if user_input == "exit":
            break

        tool_name, tool_result = decide_and_execute(user_input)
        if tool_name:
            print(f"[Tool Used]: {tool_name}")
            print(f"[Tool Result]: {tool_result}")
            
            enhanced_input = f"""
            User question:
            {user_input}
            Tool used:
            {tool_name}
            Tool result:
            {tool_result}
            Please explain and give suggestion.
            """
            result = ask_llm(enhanced_input)
        else:
            result = ask_llm(user_input)
            
        print("Industrial AI Copilot:", result)

if __name__ == "__main__":
    main()