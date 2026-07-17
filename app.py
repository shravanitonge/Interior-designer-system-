"""
AI Interior Designer — Office Edition (Streamlit)
Single-file build: catalog + design engine + visualizer + UI all in one file
on purpose, so there are no local module imports that can go missing on
deployment. Only third-party packages (streamlit, pandas, matplotlib) are
required — see requirements.txt.
"""

import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ===========================================================================
# 1. CATALOG DATA (prices, wood types, design norms — edit freely)
# ===========================================================================

WOOD_TYPES = {
    "Teak Wood":          {"multiplier": 1.8, "desc": "Premium, durable, water-resistant"},
    "Walnut Wood":        {"multiplier": 1.9, "desc": "Premium, dark tone, luxury look"},
    "Oak Wood":           {"multiplier": 1.5, "desc": "Durable mid-premium hardwood"},
    "Sheesham Wood":      {"multiplier": 1.3, "desc": "Sturdy, cost-effective hardwood"},
    "Plywood + Laminate": {"multiplier": 1.0, "desc": "Standard commercial office finish"},
    "MDF (Painted)":      {"multiplier": 0.8, "desc": "Budget-friendly, smooth painted finish"},
}

FURNITURE_BASE_PRICE = {
    "Ergonomic Chair":              4500,
    "Visitor Chair":                2500,
    "Executive Chair":              8500,
    "Workstation Desk (1 seat)":    6000,
    "Cabin Table (Executive)":      15000,
    "Meeting Table (per seat)":     4000,
    "Conference Table (per seat)":  5500,
    "Interview Table (small)":      7000,
    "Canteen Table (4-seater)":     9000,
    "Canteen Chair":                1800,
    "Reception Desk":               22000,
    "Storage Cabinet":              6500,
    "Ceiling Fan":                  2200,
    "Cabin Partition Unit":         12000,
}

WOOD_APPLICABLE_ITEMS = {
    "Cabin Table (Executive)", "Meeting Table (per seat)", "Conference Table (per seat)",
    "Interview Table (small)", "Canteen Table (4-seater)", "Reception Desk",
    "Storage Cabinet", "Workstation Desk (1 seat)", "Cabin Partition Unit",
}

NORMS = {
    "sqft_per_workstation": 60,
    "sqft_per_cabin": 100,
    "sqft_per_fan": 120,
    "interview_room_seats": 3,
    "canteen_sqft_per_seat": 12,
}

# ===========================================================================
# 2. DESIGN ENGINE (requirements -> room-by-room furniture plan)
# ===========================================================================


def _price(item_name, wood_type):
    base = FURNITURE_BASE_PRICE[item_name]
    if item_name in WOOD_APPLICABLE_ITEMS:
        base = base * WOOD_TYPES[wood_type]["multiplier"]
    return round(base)


def _fans_for_area(area_sqft):
    return max(1, math.ceil(area_sqft / NORMS["sqft_per_fan"]))


def generate_design(req: dict):
    rows = []
    wood = req["wood_type"]

    def add_row(room, item, qty, note=""):
        unit_price = _price(item, wood)
        rows.append({
            "Room": room, "Item": item, "Qty": qty,
            "Unit Price (₹)": unit_price, "Subtotal (₹)": unit_price * qty, "Note": note,
        })

    chair_map = {"Standard": "Ergonomic Chair", "Premium": "Executive Chair", "Budget": "Visitor Chair"}
    workstation_chair = chair_map.get(req["chair_type"], "Ergonomic Chair")

    if req["workstations"] > 0:
        area = req["workstations"] * NORMS["sqft_per_workstation"]
        add_row("Open Workstation Area", "Workstation Desk (1 seat)", req["workstations"])
        add_row("Open Workstation Area", workstation_chair, req["workstations"])
        if req["add_fans"]:
            add_row("Open Workstation Area", "Ceiling Fan", _fans_for_area(area),
                    f"~{area} sqft @ 1 fan/{NORMS['sqft_per_fan']}sqft")

    for i in range(1, req["cabins"] + 1):
        room = f"Cabin {i}"
        add_row(room, "Cabin Table (Executive)", 1)
        add_row(room, "Executive Chair", 1)
        add_row(room, "Visitor Chair", 2)
        add_row(room, "Storage Cabinet", 1)
        add_row(room, "Cabin Partition Unit", 1)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", _fans_for_area(NORMS["sqft_per_cabin"]))

    for i in range(1, req["meeting_rooms"] + 1):
        room = f"Meeting Room {i}"
        seats = req["meeting_room_seats"]
        add_row(room, "Meeting Table (per seat)", seats, f"seats {seats}")
        add_row(room, "Ergonomic Chair", seats)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", 1)

    for i in range(1, req["conference_rooms"] + 1):
        room = f"Conference Room {i}"
        seats = req["conference_seats"]
        add_row(room, "Conference Table (per seat)", seats, f"seats {seats}")
        add_row(room, "Executive Chair", seats)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", _fans_for_area(seats * 15))

    for i in range(1, req["interview_rooms"] + 1):
        room = f"Interview Room {i}"
        seats = NORMS["interview_room_seats"]
        add_row(room, "Interview Table (small)", 1)
        add_row(room, "Ergonomic Chair", seats)
        if req["add_fans"]:
            add_row(room, "Ceiling Fan", 1)

    if req["canteen"]:
        cap = req["canteen_capacity"]
        tables = math.ceil(cap / 4)
        area = cap * NORMS["canteen_sqft_per_seat"]
        add_row("Canteen", "Canteen Table (4-seater)", tables)
        add_row("Canteen", "Canteen Chair", cap)
        if req["add_fans"]:
            add_row("Canteen", "Ceiling Fan", _fans_for_area(area))

    add_row("Reception", "Reception Desk", 1)
    add_row("Reception", "Visitor Chair", 3)

    wash_note = f"{req['washrooms']} washroom(s) — fixtures/plumbing not included in furniture cost"

    total_cost = sum(r["Subtotal (₹)"] for r in rows)

    return {"rows": rows, "total_cost": total_cost, "washroom_note": wash_note}


# ===========================================================================
# 3. VISUALIZER (schematic 2D block layout)
# ===========================================================================

ROOM_COLORS = {"Open Workstation Area": "#cfe8f3", "Reception": "#f3e5cf", "Canteen": "#e5cff3"}
DEFAULT_COLOR = "#dbeeff"
CABIN_COLOR = "#e8e2d0"
MEETING_COLOR = "#d9f0d9"
INTERVIEW_COLOR = "#f0d9d9"


def _color_for(room_name):
    if room_name in ROOM_COLORS:
        return ROOM_COLORS[room_name]
    if room_name.startswith("Cabin"):
        return CABIN_COLOR
    if room_name.startswith("Meeting") or room_name.startswith("Conference"):
        return MEETING_COLOR
    if room_name.startswith("Interview"):
        return INTERVIEW_COLOR
    return DEFAULT_COLOR


def draw_layout(room_names, washrooms=1):
    rooms = list(dict.fromkeys(room_names))
    for i in range(1, washrooms + 1):
        rooms.append(f"Washroom {i}")

    n = len(rooms)
    cols = math.ceil(math.sqrt(n * 1.6))
    rows_n = math.ceil(n / cols)

    cell_w, cell_h = 4, 3
    fig, ax = plt.subplots(figsize=(cols * cell_w / 2.2, rows_n * cell_h / 2.2))

    for idx, room in enumerate(rooms):
        r, c = divmod(idx, cols)
        x, y = c * cell_w, (rows_n - r - 1) * cell_h
        color = "#f0f0f0" if room.startswith("Washroom") else _color_for(room)
        rect = patches.FancyBboxPatch(
            (x + 0.15, y + 0.15), cell_w - 0.3, cell_h - 0.3,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2, edgecolor="#555555", facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(x + cell_w / 2, y + cell_h / 2, room, ha="center", va="center", fontsize=8.5, wrap=True)

    ax.set_xlim(0, cols * cell_w)
    ax.set_ylim(0, rows_n * cell_h)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Schematic Office Layout (auto-generated, not to scale)", fontsize=11)
    fig.tight_layout()
    return fig


# ===========================================================================
# 4. STREAMLIT UI
# ===========================================================================

st.set_page_config(page_title="AI Office Interior Designer", layout="wide")

st.title("🏢 AI Interior Designer — Office Edition")
st.caption(
    "Enter your office requirements and get an auto-generated furniture plan, "
    "cost estimate, and a schematic layout."
)

with st.sidebar:
    st.header("📋 Office Requirements")

    employees = st.number_input("Total employees", min_value=1, value=40, step=1)

    st.subheader("Spaces")
    workstations = st.number_input("Open workstations", min_value=0, value=25, step=1)
    cabins = st.number_input("Private cabins / cabin offices", min_value=0, value=6, step=1)
    meeting_rooms = st.number_input("Meeting rooms", min_value=0, value=2, step=1)
    meeting_room_seats = st.number_input("Seats per meeting room", min_value=2, value=6, step=1)
    conference_rooms = st.number_input("Conference rooms", min_value=0, value=1, step=1)
    conference_seats = st.number_input("Seats per conference room", min_value=2, value=10, step=1)
    interview_rooms = st.number_input("Interview rooms", min_value=0, value=1, step=1)

    canteen = st.checkbox("Include canteen", value=True)
    canteen_capacity = st.number_input(
        "Canteen seating capacity", min_value=4, value=20, step=2, disabled=not canteen
    )

    washrooms = st.number_input("Washrooms", min_value=1, value=2, step=1)

    st.subheader("Finish & Fittings")
    wood_type = st.selectbox("Wood / finish type", list(WOOD_TYPES.keys()))
    st.caption(WOOD_TYPES[wood_type]["desc"])
    chair_type = st.selectbox("Workstation chair grade", ["Standard", "Premium", "Budget"])
    add_fans = st.checkbox("Include ceiling fans", value=True)

    generate = st.button("✨ Generate Design", type="primary", use_container_width=True)

if "design" not in st.session_state:
    st.session_state.design = None

if generate:
    req = dict(
        employees=employees, workstations=workstations, cabins=cabins,
        meeting_rooms=meeting_rooms, meeting_room_seats=meeting_room_seats,
        conference_rooms=conference_rooms, conference_seats=conference_seats,
        interview_rooms=interview_rooms, canteen=canteen, canteen_capacity=canteen_capacity,
        washrooms=washrooms, wood_type=wood_type, chair_type=chair_type, add_fans=add_fans,
    )
    st.session_state.design = generate_design(req)
    st.session_state.last_req = req

design = st.session_state.design

if design is None:
    st.info("Fill in your requirements in the sidebar and click **Generate Design**.")
else:
    df = pd.DataFrame(design["rows"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Estimated Cost", f"₹{design['total_cost']:,}")
    col2.metric("Rooms Planned", df["Room"].nunique())
    col3.metric("Total Furniture Items", int(df["Qty"].sum()))

    tab1, tab2, tab3 = st.tabs(["📐 Layout", "🪑 Furniture Plan", "💰 Cost Breakdown"])

    with tab1:
        fig = draw_layout(df["Room"].tolist(), washrooms=st.session_state.last_req["washrooms"])
        st.pyplot(fig)
        st.info(design["washroom_note"])

    with tab2:
        for room in df["Room"].unique():
            with st.expander(f"**{room}**", expanded=False):
                st.dataframe(
                    df[df["Room"] == room][["Item", "Qty", "Unit Price (₹)", "Subtotal (₹)", "Note"]],
                    hide_index=True, use_container_width=True,
                )

    with tab3:
        st.dataframe(df, hide_index=True, use_container_width=True)
        cost_by_item = df.groupby("Item")["Subtotal (₹)"].sum().sort_values(ascending=False)
        st.bar_chart(cost_by_item)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Full Plan (CSV)", csv, "office_design_plan.csv", "text/csv")
