# Tool: Web search stub for now
# tools/search_tool.py

def search_internet(query: str) -> str:
    """
    Simulates an internet search. In a real application, this would call a search API.
    """
    print(f"\n[TOOL CALL] Searching for: '{query}'...")
    # Dummy results based on common Bali search queries
    if "7-day relaxing trip Bali" in query.lower():
        return "Bali offers diverse experiences: beaches (Seminyak, Kuta, Nusa Dua), cultural sites (Ubud, temples like Tanah Lot, Uluwatu), and nature (Mount Batur, Tegalalang rice terraces). Average cost for 7 days can range from ₹60,000 to ₹120,000 depending on luxury."
    elif "beaches in Bali" in query.lower():
        return "Popular beaches include Kuta (lively, surfing), Seminyak (upscale, dining), Nusa Dua (resorts, water sports), Jimbaran (seafood dinners), Padang Padang (small, scenic)."
    elif "cultural sites Bali" in query.lower() or "temples Bali" in query.lower():
        return "Key cultural sites: Ubud (art, yoga, Monkey Forest, rice terraces), Tanah Lot Temple (ocean temple, sunset), Uluwatu Temple (cliff temple, Kecak dance), Besakih Temple (mother temple)."
    elif "nature activities Bali" in query.lower():
        return "Nature activities: Mount Batur sunrise trek, Tegalalang Rice Terraces, Tegenungan Waterfall, snorkeling/diving in Nusa Penida or Menjangan Island."
    elif "cost of food Bali" in query.lower():
        return "Food in Bali can range from 100-300 INR for local warungs to 1000-3000 INR+ per meal for fine dining."
    elif "transportation in Bali" in query.lower():
        return "Transportation options include ride-hailing apps (Gojek, Grab), private drivers, scooter rentals, and taxis. A private driver for a day costs around 2000-4000 INR."
    else:
        return f"No specific information found for '{query}'. This is a dummy search."