# Planner agent: decides next step using LLM
# agents/planning_agent.py

from typing import List, Dict, Any
from openai import OpenAI
from config.llm_settings import client, LLM_MODEL, LLM_TEMPERATURE
from tools.search_tool import search_internet
from tools.budget_tool import manage_budget
from tools.flight_tool import search_flights

class PlanningAgent:
    def __init__(self):
        self.client = client
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Search the internet for information about Bali trip planning, attractions, costs, etc.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "The search query."},
                        },
                        "required": ["query"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "search_flights",
                    "description": "Search for flight availability and estimated costs.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "origin": {"type": "string", "description": "Departure city (e.g., Delhi)."},
                            "destination": {"type": "string", "description": "Arrival city (e.g., Bali)."},
                            "date": {"type": "string", "description": "Travel date (e.g., '2025-07-20')."},
                            "num_travelers": {"type": "integer", "description": "Number of travelers."},
                        },
                        "required": ["origin", "destination", "date"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "manage_budget",
                    "description": "Track and manage the trip budget.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["add_expense", "get_status"], "description": "Action to perform on the budget."},
                            "item": {"type": "string", "description": "Name of the expense item (required for add_expense)."},
                            "cost": {"type": "number", "description": "Cost of the item (required for add_expense)."},
                        },
                        "required": ["action"],
                    },
                },
            },
        ]

    def generate_plan(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a high-level 7-day Bali trip plan based on the goal.
        Utilizes tools for information gathering.
        """
        user_goal = current_state.get("goal")
        messages = current_state.get("messages", [])

        if not messages:
            messages.append({"role": "user", "content": user_goal})
            messages.append({
                "role": "system",
                "content": (
                    "You are a Bali trip planning expert. Your goal is to create a detailed 7-day "
                    "relaxing trip plan covering beach, culture, and nature, staying under ₹80,000 from Delhi. "
                    "Use the provided tools (search_internet, search_flights, manage_budget) to gather information and estimate costs. "
                    "First, research Bali, then flights, and then start outlining a daily itinerary. "
                    "Be mindful of the budget at all times. Respond with a comprehensive plan when complete, or suggest next steps."
                )
            })

        print("\n[PLANNING AGENT] Thinking...")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=self.temperature
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if tool_calls:
                # Call tools and add their output to messages
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = {}
                    try:
                        function_args = eval(tool_call.function.arguments) # Be cautious with eval in production
                    except Exception as e:
                        print(f"Error parsing tool arguments: {e}")
                        # Fallback for ill-formatted JSON from LLM
                        import json
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            print(f"Failed to parse arguments as JSON: {tool_call.function.arguments}")
                            continue

                    tool_response = ""
                    if function_name == "search_internet":
                        tool_response = search_internet(**function_args)
                    elif function_name == "search_flights":
                        tool_response = search_flights(**function_args)
                        # Add flight cost to budget (dummy)
                        if "Estimated total cost" in tool_response:
                            cost_str = tool_response.split("Estimated total cost: ₹")[1].split(".")[0]
                            flight_cost = float(cost_str)
                            manage_budget("add_expense", "Flights", flight_cost)
                    elif function_name == "manage_budget":
                        tool_response = manage_budget(**function_args)
                    
                    messages.append(response_message)
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_response,
                        }
                    )
                current_state["messages"] = messages
                current_state["next_step"] = "planning" # Keep planning if tools were called
            else:
                # If no tool calls, it's generating a text response (the plan)
                plan_content = response_message.content
                print(f"\n[PLANNING AGENT] Generated Plan:\n{plan_content}")
                current_state["trip_plan"] = plan_content
                current_state["next_step"] = "review" # Transition to review or execution
                messages.append(response_message)
                current_state["messages"] = messages # Update messages for next step

        except Exception as e:
            print(f"Error in Planning Agent: {e}")
            current_state["error"] = str(e)
            current_state["next_step"] = "error"
        
        return current_state