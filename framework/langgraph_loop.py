# LangGraph logic for AutoGPT loop
# framework/langgraph_auto_loop.py

from typing import TypedDict, List, Annotated, Dict, Any
import operator
from langgraph.graph import StateGraph, END

from agents.planning_agent import PlanningAgent
from agents.execution_agent import ExecutionAgent
from agents.memory_agent import MemoryAgent
from tools.budget_tool import manage_budget, BUDGET_MANAGER # Import the global manager

# Define the state for the graph
class AgentState(TypedDict):
    goal: str
    trip_plan: str
    messages: Annotated[List[Dict[str, Any]], operator.add]
    next_step: str # To control transitions
    error: Annotated[str, operator.add]


class BaliTripAgent:
    def __init__(self):
        self.planning_agent = PlanningAgent()
        self.execution_agent = ExecutionAgent()
        self.memory_agent = MemoryAgent()
        self.workflow = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("plan", self.planning_agent.generate_plan)
        workflow.add_node("execute", self.execution_agent.refine_and_execute)
        workflow.add_node("memorize", self.memory_agent.process_memory)
        
        # Add a final step to summarize and check budget
        workflow.add_node("finalize", self._finalize_trip)
        workflow.add_node("error_state", self._handle_error)

        # Define edges (transitions)
        workflow.set_entry_point("plan")

        workflow.add_conditional_edges(
            "plan",
            lambda state: state.get("next_step"),
            {
                "planning": "plan",  # If plan needs more info (e.g., tool calls), loop back to planning
                "review": "execute", # If plan is generated, move to execution/review
                "error": "error_state"
            },
        )
        
        workflow.add_conditional_edges(
            "execute",
            lambda state: state.get("next_step"),
            {
                "execution": "execute", # If execution needs more steps/tool calls, loop back
                "finalize": "finalize", # If execution is complete, finalize
                "error": "error_state"
            },
        )
        
        # After finalize, go to memory then end
        workflow.add_edge("finalize", "memorize")
        workflow.add_edge("memorize", END)
        workflow.add_edge("error_state", END) # End if error occurs

        return workflow.compile()

    def _finalize_trip(self, state: Dict[str, Any]) -> Dict[str, Any]:
        print("\n[FINALIZING TRIP] Reviewing final plan and budget...")
        final_plan = state.get("trip_plan", "No plan generated.")
        budget_status = manage_budget("get_status")
        
        final_output = (
            "\n--- BALI TRIP PLAN COMPLETE ---\n"
            f"Here is your 7-day Bali trip plan:\n{final_plan}\n\n"
            f"Final Budget Status:\n{budget_status}\n"
            "Enjoy your relaxing trip to Bali!"
        )
        print(final_output)
        state["messages"].append({"role": "assistant", "content": final_output})
        state["next_step"] = "finished" # Signal completion for memory to store
        return state

    def _handle_error(self, state: Dict[str, Any]) -> Dict[str, Any]:
        error_message = state.get("error", "An unknown error occurred.")
        print(f"\n[ERROR] The agent encountered an error: {error_message}")
        state["messages"].append({"role": "system", "content": f"ERROR: {error_message}"})
        state["next_step"] = "finished" # Force end
        return state

    def run(self, user_goal: str):
        initial_state = {
            "goal": user_goal,
            "trip_plan": "",
            "messages": [],
            "next_step": "plan",
            "error": ""
        }
        print(f"Starting Bali Trip Planner with goal: {user_goal}")
        
        # Reset budget for a new run
        global BUDGET_MANAGER
        BUDGET_MANAGER = BUDGET_MANAGER.__class__(80000.0) # Re-initialize to original budget

        for s in self.workflow.stream(initial_state):
            print(f"\n--- Current State ---")
            for key, value in s.items():
                if key != "__end__": # Don't print the END signal itself
                    print(f"{key}: {value}")
            if "__end__" in s:
                break
        
        final_state = self.workflow.invoke(initial_state)
        # The stream above already prints, but invoke gives the final state for external use
        # print("\nFinal State of the Trip Planner:")
        # print(final_state)
        return final_state