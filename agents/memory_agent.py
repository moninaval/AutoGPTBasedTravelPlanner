# Memory agent: retrieves past thoughts or RAG chunks
# agents/memory_agent.py

from typing import Dict, Any, List

class MemoryAgent:
    def __init__(self):
        self.memory_store: List[Dict[str, Any]] = []

    def store_state(self, state: Dict[str, Any]) -> None:
        """Stores the current state in memory."""
        # A simple append; in a real scenario, you might summarize or extract key info
        self.memory_store.append(state)
        print("\n[MEMORY AGENT] State stored.")

    def retrieve_info(self, query: str = None) -> List[Dict[str, Any]]:
        """Retrieves relevant information from memory."""
        print(f"\n[MEMORY AGENT] Retrieving info for: '{query}' (dummy retrieval).")
        # For simplicity, return all recent states or states matching a simple keyword
        if query:
            return [s for s in self.memory_store if query.lower() in str(s).lower()]
        return self.memory_store[-5:] # Return last 5 states

    def process_memory(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """Processes and potentially updates memory based on current state."""
        self.store_state(current_state.copy()) # Store a copy to avoid mutation issues
        return current_state