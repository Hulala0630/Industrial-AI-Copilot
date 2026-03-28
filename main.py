from core.llm_client import ask_llm 
def main():
    print("Welcome to the Industrial AI Copilot!")
    
    while True:
        user_input = input("Please enter your question: ")
        if user_input == "exit":
            break
        result = ask_llm(user_input)
        print("Industrial AI Copilot:", result)

if __name__ == "__main__":
    main()