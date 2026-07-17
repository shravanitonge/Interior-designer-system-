"""
Static catalog data: furniture items, wood types, and per-room design norms.
Prices are illustrative (INR) — edit freely to match real vendor quotes.
"""

# ---------------------------------------------------------------------------
# Wood types: relative price multiplier + short description
# ---------------------------------------------------------------------------
WOOD_TYPES = {
    "Teak Wood":        {"multiplier": 1.8, "desc": "Premium, durable, water-resistant"},
    "Walnut Wood":       {"multiplier": 1.9, "desc": "Premium, dark tone, luxury look"},
    "Oak Wood":          {"multiplier": 1.5, "desc": "Durable mid-premium hardwood"},
    "Sheesham Wood":     {"multiplier": 1.3, "desc": "Sturdy, cost-effective hardwood"},
    "Plywood + Laminate":{"multiplier": 1.0, "desc": "Standard commercial office finish"},
    "MDF (Painted)":     {"multiplier": 0.8, "desc": "Budget-friendly, smooth painted finish"},
}

# ---------------------------------------------------------------------------
# Base furniture catalog: base price in INR, at multiplier = 1.0
# ---------------------------------------------------------------------------
FURNITURE_BASE_PRICE = {
    "Ergonomic Chair":        4500,
    "Visitor Chair":          2500,
    "Executive Chair":        8500,
    "Workstation Desk (1 seat)": 6000,
    "Cabin Table (Executive)":  15000,
    "Meeting Table (per seat)": 4000,
    "Conference Table (per seat)": 5500,
    "Interview Table (small)":  7000,
    "Canteen Table (4-seater)": 9000,
    "Canteen Chair":            1800,
    "Reception Desk":          22000,
    "Storage Cabinet":          6500,
    "Ceiling Fan":              2200,
    "Cabin Partition Unit":    12000,
}

WOOD_APPLICABLE_ITEMS = {
    "Cabin Table (Executive)", "Meeting Table (per seat)", "Conference Table (per seat)",
    "Interview Table (small)", "Canteen Table (4-seater)", "Reception Desk",
    "Storage Cabinet", "Workstation Desk (1 seat)", "Cabin Partition Unit",
}

# ---------------------------------------------------------------------------
# Design norms — industry-typical rules of thumb used by the design engine
# ---------------------------------------------------------------------------
NORMS = {
    "sqft_per_workstation": 60,     # open workstation incl. circulation
    "sqft_per_cabin": 100,          # private cabin/office
    "sqft_per_fan": 120,            # 1 ceiling fan per X sqft
    "meeting_room_seats_default": 6,
    "conference_room_seats_default": 10,
    "interview_room_seats": 3,      # 1 candidate + 2 interviewers
    "canteen_sqft_per_seat": 12,
    "washroom_per_employees": 15,   # 1 washroom fixture-set per N employees
}
