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
st.markdown("---")

# Hero section
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("## ICT Futures Trading System")
    st.markdown(
        "Automated futures trading bot implementing **Inner Circle Trader** concepts "
        "with algorithmic execution. Fair Value Gap detection, multi-entry framework, "
        "hybrid filter system, and dynamic position sizing."
    )
    tech_tags = "`Python` `TradingView` `Tradovate` `DigitalOcean` `Telegram` `PickMyTrade`"
    st.markdown(tech_tags)

with col2:
    st.markdown("### Current Version")
    st.markdown("## V10.15")
    st.caption("Bar-Aligned Scanning")
    st.markdown("**17 versions** over 5 months")
    st.markdown("**6 instruments** (ES, NQ, MES, MNQ, SPY, QQQ)")

st.markdown("---")
st.markdown("## Strategies")

# Load strategy metadata
data_path = Path(__file__).parent.parent / 'data' / 'strategy_metadata.json'
with open(data_path) as f:
    strategies = json.load(f)

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
