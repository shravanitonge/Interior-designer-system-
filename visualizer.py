"""
Draws a simple 2D block-layout floor plan (schematic, not to scale)
based on the list of rooms produced by the design engine.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

ROOM_COLORS = {
    "Open Workstation Area": "#cfe8f3",
    "Reception": "#f3e5cf",
    "Canteen": "#e5cff3",
}
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
    """room_names: ordered list of unique room names (strings)."""
    rooms = list(dict.fromkeys(room_names))  # unique, order-preserved
    for i in range(1, washrooms + 1):
        rooms.append(f"Washroom {i}")

    n = len(rooms)
    cols = math.ceil(math.sqrt(n * 1.6))
    rows = math.ceil(n / cols)

    cell_w, cell_h = 4, 3
    fig, ax = plt.subplots(figsize=(cols * cell_w / 2.2, rows * cell_h / 2.2))

    for idx, room in enumerate(rooms):
        r, c = divmod(idx, cols)
        x, y = c * cell_w, (rows - r - 1) * cell_h
        color = "#f0f0f0" if room.startswith("Washroom") else _color_for(room)
        rect = patches.FancyBboxPatch(
            (x + 0.15, y + 0.15), cell_w - 0.3, cell_h - 0.3,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2, edgecolor="#555555", facecolor=color,
        )
        ax.add_patch(rect)
        ax.text(x + cell_w / 2, y + cell_h / 2, room,
                 ha="center", va="center", fontsize=8.5, wrap=True)

    ax.set_xlim(0, cols * cell_w)
    ax.set_ylim(0, rows * cell_h)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Schematic Office Layout (auto-generated, not to scale)", fontsize=11)
    fig.tight_layout()
    return fig
