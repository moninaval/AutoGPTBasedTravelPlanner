# Tool: Dummy flight lookup tool
# tools/flight_tool.py

def search_flights(origin: str, destination: str, date: str, num_travelers: int = 1) -> str:
    """
    Simulates searching for flights. In a real application, this would call a flight API.
    Assumes fixed dummy prices and availability.
    """
    print(f"\n[TOOL CALL] Searching flights: {origin} to {destination} on {date} for {num_travelers} people.")
    
    # Dummy flight data
    if origin.lower() == "delhi" and destination.lower() == "bali":
        if "july 2025" in date.lower() or "august 2025" in date.lower():
            # Example: Round trip for one person
            base_price = 30000.0  # INR
            total_price = base_price * num_travelers
            return_date = "7 days after " + date
            return (
                f"Found flights from {origin} to {destination} on {date} (returning {return_date}) "
                f"for {num_travelers} person(s). Estimated total cost: ₹{total_price:.2f}. "
                "Availability: Good. (Dummy Data)"
            )
        else:
            return f"No direct flights found for {date}. (Dummy Data)"
    return f"No flights found for { requested route {origin} to {destination}. (Dummy Data)"