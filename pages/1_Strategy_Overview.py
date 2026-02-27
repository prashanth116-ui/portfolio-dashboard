"""Page 1: Strategy Overview — Hero section + strategy cards."""
import json
from pathlib import Path

import streamlit as st

# Add project root to path for component imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.strategy_cards import render_strategy_card

st.set_page_config(page_title="Strategy Overview", page_icon="📊", layout="wide")

st.markdown("# Strategy Overview")
st.markdown(
    "5 strategies across futures and equities. "
    "V10 FVG is the active production strategy; others are in research/experimental phases."
)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active", "V10.15")
with col2:
    st.metric("Instruments", "6")
with col3:
    st.metric("Versions", "20")
with col4:
    st.metric("Development", "5 months")

st.markdown("---")

@st.cache_data
def load_strategies():
    data_path = Path(__file__).parent.parent / 'data' / 'strategy_metadata.json'
    with open(data_path) as f:
        return json.load(f)

strategies = load_strategies()

# Active strategy first (full width)
active = [s for s in strategies if s['status'] == 'ACTIVE']
for s in active:
    render_strategy_card(s)

st.markdown("### Other Strategies")

# Other strategies in 2-column grid
others = [s for s in strategies if s['status'] != 'ACTIVE']
cols = st.columns(2)
for i, s in enumerate(others):
    with cols[i % 2]:
        render_strategy_card(s)
