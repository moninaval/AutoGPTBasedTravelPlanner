## agents/execution_agent.py

from typing import Dict, Any
from openai import OpenAI
from config.llm_settings import client, LLM_MODEL, LLM_TEMPERATURE
from tools.budget_tool import manage_budget
from tools.search_tool import search_internet

class ExecutionAgent:
    def __init__(self):
        self.client = client
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_internet",
                    "description": "Search the internet for detailed information for specific parts of the plan (e.g., specific restaurant, exact timings for a temple).",
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
                    "name": "manage_budget",
                    "description": "Track and manage the trip budget for granular expenses.",
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

    def refine_and_execute(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refines the trip plan and simulates execution, making detailed budget entries.
        """
        trip_plan = current_state.get("trip_plan")
        messages = current_state.get("messages", [])

        if not messages or (messages and messages[-1].get("role") == "tool"):
             # Add system message if not already present or if previous was a tool call
            messages.append({
                "role": "system",
                "content": (
                    "You are an execution agent. Your task is to refine the trip plan, "
                    "simulate booking/detail gathering, and manage the budget. "
                    "For each significant item or activity in the plan (e.g., accommodation, specific tours, daily food estimates), "
                    "use the 'manage_budget' tool to add an estimated expense. "
                    "Use 'search_internet' for any missing details. "
                    "Confirm budget status frequently. Respond with 'EXECUTION_COMPLETE' when you believe the plan is sufficiently detailed and budgeted, "
                    "or 'EXECUTION_PENDING' if more details are needed or tools were called."
                )
            })
            if trip_plan and not any("trip_plan" in msg.get("content", "") for msg in messages if msg.get("role") == "user"):
                 # Only add the trip plan as a new user message if it hasn't been added yet
                messages.append({"role": "user", "content": f"Refine and budget this plan:\n{trip_plan}"})


        print("\n[EXECUTION AGENT] Refining plan and managing budget...")
        
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
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = {}
                    try:
                        function_args = eval(tool_call.function.arguments) # Be cautious
                    except Exception as e:
                        print(f"Error parsing tool arguments: {e}")
                        import json
                        try:
                            function_args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            print(f"Failed to parse arguments as JSON: {tool_call.function.arguments}")
                            continue

                    tool_response = ""
                    if function_name == "manage_budget":
                        tool_response = manage_budget(**function_args)
                    elif function_name == "search_internet":
                        tool_response = search_internet(**function_args)
                    
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
                current_state["next_step"] = "execution" # Stay in execution if tools were called
            else:
                execution_status = response_message.content
                print(f"\n[EXECUTION AGENT] Execution status update: {execution_status}")
                messages.append(response_message)
                current_state["messages"] = messages
                if "EXECUTION_COMPLETE" in execution_status:
                    current_state["next_step"] = "finalize"
                elif "EXECUTION_PENDING" in execution_status:
                    current_state["next_step"] = "execution"
                else:
                    # If it's just general text, assume it's part of refinement and loop
                    current_state["next_step"] = "execution"

        except Exception as e:
            print(f"Error in Execution Agent: {e}")
            current_state["error"] = str(e)
            current_state["next_step"] = "error"
        
        return current_state Executor agent: calls tools like search, budget
