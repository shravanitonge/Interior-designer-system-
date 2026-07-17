"""
Rule-based AI Interior Design Engine for Offices.

Takes a structured set of user requirements and returns:
  - a room-by-room furniture plan (list of dict rows)
  - a summary furniture count
  - a total cost estimate
"""

from data.catalog import FURNITURE_BASE_PRICE, WOOD_TYPES, WOOD_APPLICABLE_ITEMS, NORMS
import math


def _price(item_name, wood_type):
    base = FURNITURE_BASE_PRICE[item_name]
    if item_name in WOOD_APPLICABLE_ITEMS:
        base = base * WOOD_TYPES[wood_type]["multiplier"]
    return round(base)


def _fans_for_area(area_sqft):
    return max(1, math.ceil(area_sqft / NORMS["sqft_per_fan"]))


def generate_design(req: dict):
    """
    req keys expected:
      employees, cabins, workstations, meeting_rooms, meeting_room_seats,
      conference_rooms, conference_seats, interview_rooms, canteen, canteen_capacity,
      washrooms, wood_type, chair_type, add_fans
    """
    rows = []          # room-by-room furniture rows for the plan table
    wood = req["wood_type"]

    def add_row(room, item, qty, note=""):
        unit_price = _price(item, wood)
        rows.append({
            "Room": room,
            "Item": item,
            "Qty": qty,
            "Unit Price (₹)": unit_price,
            "Subtotal (₹)": unit_price * qty,
            "Note": note,
        })

    chair_map = {
        "Standard": "Ergonomic Chair",
        "Premium": "Executive Chair",
        "Budget": "Visitor Chair",
    }
    workstation_chair = chair_map.get(req["chair_type"], "Ergonomic Chair")

    # ---- Open workstations -------------------------------------------------
    if req["workstations"] > 0:
        area = req["workstations"] * NORMS["sqft_per_workstation"]
        add_row("Open Workstation Area", "Workstation Desk (1 seat)", req["workstations"])
        add_row("Open Workstation Area", workstation_chair, req["workstations"])
        if req["add_fans"]:
            add_row("Open Workstation Area", "Ceiling Fan", _fans_for_area(area),
                    f"~{area} sqft @ 1 fan/{NORMS['sqft_per_fan']}sqft")

    # ---- Private cabins ------------------------------------------------
    for i in range(1, req["cabins"] + 1):
        room = f"Cabin {i}"
        add_row(room, "Cabin Table (Executive)", 1)
        add_row(room, "Executive Chair", 1)
        add_row(room, "Visitor Chair", 2)
        add_row(room, "Storage Cabinet", 1)
        add_row(room, "Cabin Partition Unit", 1)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", _fans_for_area(NORMS["sqft_per_cabin"]))

    # ---- Meeting rooms ---------------------------------------------------
    for i in range(1, req["meeting_rooms"] + 1):
        room = f"Meeting Room {i}"
        seats = req["meeting_room_seats"]
        add_row(room, "Meeting Table (per seat)", seats, f"seats {seats}")
        add_row(room, "Ergonomic Chair", seats)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", 1)

    # ---- Conference rooms --------------------------------------------------
    for i in range(1, req["conference_rooms"] + 1):
        room = f"Conference Room {i}"
        seats = req["conference_seats"]
        add_row(room, "Conference Table (per seat)", seats, f"seats {seats}")
        add_row(room, "Executive Chair", seats)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", _fans_for_area(seats * 15))

    # ---- Interview rooms -----------------------------------------------
    for i in range(1, req["interview_rooms"] + 1):
        room = f"Interview Room {i}"
        seats = NORMS["interview_room_seats"]
        add_row(room, "Interview Table (small)", 1)
        add_row(room, "Ergonomic Chair", seats)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", 1)

    # ---- Canteen -------------------------------------------------------
    if req["canteen"]:
        cap = req["canteen_capacity"]
        tables = math.ceil(cap / 4)
        area = cap * NORMS["canteen_sqft_per_seat"]
        add_row("Canteen", "Canteen Table (4-seater)", tables)
        add_row("Canteen", "Canteen Chair", cap)
        if req["add_fans"]:
            add_row("Canteen", "Ceiling Fan", _fans_for_area(area))

    # ---- Reception -------------------------------------------------------
    add_row("Reception", "Reception Desk", 1)
    add_row("Reception", "Visitor Chair", 3)

    # ---- Washrooms (fixtures noted, no furniture cost) ---------------------
    wash_note = f"{req['washrooms']} washroom(s) — fixtures/plumbing not included in furniture cost"

    summary_furniture = {}
    total_cost = 0
    for r in rows:
        summary_furniture[r["Item"]] = summary_furniture.get(r["Item"], 0) + r["Qty"]
        total_cost += r["Subtotal (₹)"]

    return {
        "rows": rows,
        "summary_furniture": summary_furniture,
        "total_cost": total_cost,
        "washroom_note": wash_note,
    }
