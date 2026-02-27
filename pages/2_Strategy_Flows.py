"""Page 2: Strategy Flow Diagrams — Display 9 architecture diagrams."""
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Strategy Flows", page_icon="🔄", layout="wide")

st.markdown("# Strategy Flow Diagrams")
st.markdown("Visual architecture of the V10 FVG trading system — from signal detection through exit management.")
st.markdown("---")

# Diagram metadata
DIAGRAMS = [
    {
        "file": "01_master_flow.png",
        "title": "Master Strategy Flow",
        "description": "End-to-end execution pipeline from market open to close. Shows how bars are processed, signals generated, and trades managed through the full session lifecycle.",
    },
    {
        "file": "02_entry_types.png",
        "title": "Entry Types (A/B1/B2/C)",
        "description": "Four entry mechanisms: Creation (immediate FVG), Overnight Retrace (B1), Intraday Retrace (B2), and Break of Structure (C). Each has unique trigger conditions and filter requirements.",
    },
    {
        "file": "03_hybrid_filters.png",
        "title": "Hybrid Filter Pipeline",
        "description": "Two-tier filter system: 2 mandatory gates (DI direction, FVG size) plus 2-of-3 optional checks (displacement, ADX, EMA trend). Balances signal quality with trade frequency.",
    },
    {
        "file": "04_entry_gates.png",
        "title": "Entry Gate Checks",
        "description": "Pre-entry validation: circuit breaker (3 losses/direction/day), consecutive loss stop (ES/MES: 2), position limit (max 3 open), midday cutoff (12:00-14:00), and BOS loss limit.",
    },
    {
        "file": "05_exit_management.png",
        "title": "Exit Management",
        "description": "Three-phase exit: T1 fixed at 3R (1 ct), T2 structure trail after 6R (4-tick buffer), Runner structure trail (6-tick buffer, 1st trade only). Opposing FVG exit override after 6R.",
    },
    {
        "file": "06_trail_logic.png",
        "title": "Trail Stop Logic",
        "description": "Structure-based trailing stops with swing high/low tracking. T2 uses 4-tick buffer, Runner uses 6-tick buffer. Floor at 3R prevents giving back guaranteed profit.",
    },
    {
        "file": "07_symbol_config.png",
        "title": "Per-Symbol Configuration",
        "description": "Symbol-specific parameter matrix: tick values, risk limits, BOS control, retrace caps, and consecutive loss stops. ES/NQ have different optimal configs validated by A/B testing.",
    },
    {
        "file": "08_session_timeline.png",
        "title": "Session Timeline",
        "description": "Trading hours with entry windows and cutoff zones. Pre-market (04:00), RTH open (09:30), midday cutoff (12:00-14:00), NQ PM cutoff (14:00), market close (16:00).",
    },
    {
        "file": "09_position_sizing.png",
        "title": "Dynamic Position Sizing",
        "description": "1st trade: 3 contracts (T1 + T2 + Runner). 2nd/3rd trades: 2 contracts (T1 + T2). Retrace risk > 8pts (ES/MES): force 1 contract. Max 6 contracts total exposure.",
    },
]

diagrams_dir = Path(__file__).parent.parent / 'diagrams'

for i, diagram in enumerate(DIAGRAMS):
    img_path = diagrams_dir / diagram['file']

    with st.container(border=True):
        st.markdown(f"### {diagram['title']}")
        st.caption(diagram['description'])

        if img_path.exists():
            with st.expander("View Diagram", expanded=(i == 0)):
                st.image(str(img_path), use_container_width=True)
        else:
            st.warning(f"Diagram not found: {diagram['file']}")
