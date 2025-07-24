# main.py

import os
from dotenv import load_dotenv
from framework.langgraph_auto_loop import BaliTripAgent

# Load environment variables from .env file
load_dotenv()

def main():
    # Ensure OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set.")
        print("Please set it before running the script (e.g., export OPENAI_API_KEY='your_key')")
        return

    print("--- Bali Trip Planner CLI Agent ---")
    user_goal = "Plan a 7-day relaxing trip to Bali with beach, culture, nature under ₹80,000 from Delhi."
    print(f"Goal: {user_goal}")

    agent = BaliTripAgent()
    final_result = agent.run(user_goal)
    
    # You can access the final state here if needed
    # print("\nFinal result from agent.run():")
    # print(final_result)


if __name__ == "__main__":
    main()# Entrypoint to run CLI AutoGPT agent
