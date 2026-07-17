# AI Interior Designer — Office Edition (Streamlit)

A rule-based "AI interior designer" for offices. You enter requirements
(employees, cabins, meeting/interview rooms, canteen, washrooms, wood type,
chair grade, fans) and it generates:

- a room-by-room furniture plan
- a total & per-item cost estimate
- a schematic auto-generated 2D layout diagram
- a downloadable CSV of the full plan

## Project structure
```
office_ai_designer/
├── app.py              # Streamlit UI (entry point)
├── design_engine.py     # Rule-based logic: requirements -> furniture plan
├── visualizer.py         # Draws the schematic block layout
├── catalog.py             # Furniture prices, wood types, design norms (editable)
└── requirements.txt
```
All files are flat in one folder on purpose (no subpackages) — this avoids
`ModuleNotFoundError` issues that can happen on Streamlit Cloud when a
subfolder isn't picked up correctly from GitHub.

## Setup
```bash
cd office_ai_designer
pip install -r requirements.txt
```

## Run
```bash
streamlit run app.py
```
This opens the app in your browser at http://localhost:8501

## Customizing
- **Prices / catalog**: edit `catalog.py` — `FURNITURE_BASE_PRICE`, `WOOD_TYPES`.
- **Design rules** (e.g. sqft per workstation, fan coverage, seats per room type):
  edit `NORMS` in `catalog.py`.
- **New room types**: add a block in `design_engine.generate_design()` following
  the pattern used for cabins/meeting rooms.

## Roadmap ideas (not yet built)
- Import your actual floor plan (like the office plan image you shared) and
  snap the generated layout to real room shapes/areas instead of the schematic grid.
- Swap the rule-based engine for an LLM call (via the Anthropic API) to handle
  more nuanced, free-text requirements ("modern minimalist, budget ₹15L, prefer
  standing desks for devs").
- Add a database (SQLite) to save/load multiple design versions.
- Export the plan as a formatted PDF/Word report.
