"""Page 2: Trading Strategies — 7 strategy cards across 3 repos."""
import json
from pathlib import Path

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.strategy_cards import render_strategy_card
from components.responsive import inject_responsive_css

st.set_page_config(page_title="Trading Strategies", page_icon="📊", layout="wide")
inject_responsive_css()

st.markdown("# Trading Strategies")
st.markdown(
    "6 strategies across 3 repositories — futures and equities. "
    "V10 FVG is the active production strategy; others are in research/development."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active", "V10.15")
with col2:
    st.metric("Instruments", "8")
with col3:
    st.metric("Strategies", "6")
with col4:
    st.metric("Repos", "3")

st.markdown("---")


@st.cache_data
def load_strategies():
    data_path = Path(__file__).parent.parent / 'data' / 'strategy_metadata.json'
    with open(data_path) as f:
        return json.load(f)


strategies = load_strategies()

# Group strategies by status with counts
_STATUS_GROUPS = [
    ("Active", ("ACTIVE",), False),
    ("In Development", ("IN_DEVELOPMENT",), False),
    ("Experimental", ("EXPERIMENTAL",), True),
    ("Deprecated", ("DEPRECATED",), True),
]

for group_label, statuses, use_grid in _STATUS_GROUPS:
    group = [s for s in strategies if s['status'] in statuses]
    if not group:
        continue
    st.markdown(f"### {group_label} ({len(group)})")
    if use_grid:
        cols = st.columns(2)
        for i, s in enumerate(group):
            with cols[i % 2]:
                render_strategy_card(s)
    else:
        for s in group:
            render_strategy_card(s)
