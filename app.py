import streamlit as st
import pandas as pd

from data.catalog import WOOD_TYPES
from design_engine import generate_design
from visualizer import draw_layout

st.set_page_config(page_title="AI Office Interior Designer", layout="wide")

st.title("🏢 AI Interior Designer — Office Edition")
st.caption(
    "Enter your office requirements and get an auto-generated furniture plan, "
    "cost estimate, and a schematic layout."
)

# ---------------------------------------------------------------------------
# Sidebar: requirements form
# ---------------------------------------------------------------------------
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

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------
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
