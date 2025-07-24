# Tool: Check budget constraints
# tools/budget_tool.py

class BudgetManager:
    def __init__(self, initial_budget: float):
        self.total_budget = initial_budget
        self.remaining_budget = initial_budget
        self.expenses = []

    def add_expense(self, item: str, cost: float) -> str:
        if cost <= self.remaining_budget:
            self.remaining_budget -= cost
            self.expenses.append({"item": item, "cost": cost})
            return f"Added expense: {item} - ₹{cost:.2f}. Remaining budget: ₹{self.remaining_budget:.2f}."
        else:
            return f"Cannot add expense '{item}' (₹{cost:.2f}). Exceeds remaining budget of ₹{self.remaining_budget:.2f}."

    def get_status(self) -> str:
        total_spent = self.total_budget - self.remaining_budget
        return (
            f"Total Budget: ₹{self.total_budget:.2f}\n"
            f"Total Spent: ₹{total_spent:.2f}\n"
            f"Remaining Budget: ₹{self.remaining_budget:.2f}\n"
            f"Current Expenses: {self.expenses}"
        )

# Initialize a global budget manager for simplicity in this example
# In a real app, this might be passed through the graph state or managed differently
BUDGET_MANAGER = BudgetManager(80000.0)

def manage_budget(action: str, item: str = None, cost: float = None) -> str:
    """
    Manages the trip budget.
    Actions: 'add_expense', 'get_status'.
    """
    print(f"\n[TOOL CALL] Budget action: {action}")
    if action == "add_expense":
        if item and cost is not None:
            return BUDGET_MANAGER.add_expense(item, cost)
        else:
            return "Error: 'item' and 'cost' are required for 'add_expense'."
    elif action == "get_status":
        return BUDGET_MANAGER.get_status()
    else:
        return "Invalid budget action. Use 'add_expense' or 'get_status'."