"""
Portfolio Dashboard — Landing Page

Streamlit entrypoint. Run with:
    streamlit run app.py
"""
import json
from pathlib import Path

import streamlit as st

# Add project root to path for component imports
import sys
sys.path.insert(0, str(Path(__file__).parent))
from components.project_cards import render_project_card_mini, render_trading_card_mini

st.set_page_config(
    page_title="Prashanth Sundaram — Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def load_projects():
    with open(Path(__file__).parent / 'data' / 'projects_metadata.json') as f:
        return json.load(f)


@st.cache_data
def load_strategies():
    with open(Path(__file__).parent / 'data' / 'strategy_metadata.json') as f:
        return json.load(f)


projects = load_projects()
strategies = load_strategies()

# --- Hero ---
st.markdown("# Prashanth Sundaram")
st.markdown(
    "Software engineer building algorithmic trading systems, SaaS products, "
    "and cloud infrastructure tools."
)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Projects", len(projects) + 3)  # 4 software + 3 trading repos
with col2:
    st.metric("Trading Systems", "3 repos")
with col3:
    st.metric("Strategies", len(strategies))

st.markdown("---")

# --- Software Projects (2x2) ---
st.markdown("### Software Projects")

row1 = st.columns(2)
row2 = st.columns(2)
cols = [row1[0], row1[1], row2[0], row2[1]]
for i, proj in enumerate(projects):
    with cols[i]:
        render_project_card_mini(proj)

st.markdown("---")

# --- Trading Systems (3 columns) ---
st.markdown("### Trading Systems")

# Group strategies by repo/system
trading_systems = [
    {
        "name": "tradovate-futures-bot",
        "status": "ACTIVE",
        "version": "V10.15",
        "instruments": ["ES", "NQ", "MES", "MNQ", "SPY", "QQQ"],
        "tagline": "ICT intraday — 4 entry types, 87% win rate, automated execution",
        "tech_stack": ["Python", "TradingView", "Tradovate", "Telegram"],
        "strategies": [s['name'] for s in strategies if s['id'] in ('v10_fvg', 'ict_sweep', 'ict_ote', 'ict_state_machine')],
    },
    {
        "name": "htf-swing-strategy",
        "status": "IN_DEVELOPMENT",
        "version": "V1",
        "instruments": ["ES", "NQ", "CL", "GC", "SPY", "QQQ"],
        "tagline": "Multi-TF swing trading (Daily/4H/1H/15m) with Pine Script indicators",
        "tech_stack": ["Python", "TradingView", "Pine Script"],
        "strategies": ["ICT Multi-Timeframe Swing"],
    },
    {
        "name": "ttfm-strategy",
        "status": "EXPERIMENTAL",
        "version": "V2.0",
        "instruments": ["ES", "NQ", "MES", "MNQ"],
        "tagline": "Mechanical fractal model — C3/C4 candle patterns with CISD confirmation",
        "tech_stack": ["Python", "TradingView"],
        "strategies": ["TTFM Fractal Model"],
    },
]

STATUS_DOTS = {
    'ACTIVE': 'green',
    'IN_DEVELOPMENT': 'blue',
    'EXPERIMENTAL': 'orange',
}

STATUS_LABELS = {
    'ACTIVE': 'Active',
    'IN_DEVELOPMENT': 'In Development',
    'EXPERIMENTAL': 'Experimental',
}

tcols = st.columns(3)
for i, sys_info in enumerate(trading_systems):
    with tcols[i]:
        dot = STATUS_DOTS.get(sys_info['status'], 'gray')
        label = STATUS_LABELS.get(sys_info['status'], sys_info['status'])
        with st.container(border=True):
            st.markdown(f"**{sys_info['name']}**")
            st.caption(sys_info['tagline'])
            st.markdown(f":{dot}_circle: {label} | {sys_info['version']}")
            st.caption(f"Instruments: {', '.join(sys_info['instruments'])}")
            tags = " ".join([f"`{t}`" for t in sys_info['tech_stack']])
            st.markdown(tags)

st.markdown("---")
st.markdown("### Pages")
st.markdown(
    "- **Software Projects** — 4 project cards with status, completion, and tech stack\n"
    "- **Trading Strategies** — 6 strategies across 3 repos with entry types, filters, and exits\n"
    "- **Strategy Flows** — 9 architecture diagrams covering the signal-to-execution pipeline\n"
    "- **Version Timeline** — 20 versions from V6 to V10.15 with A/B test results\n"
    "- **Performance** — Backtest equity curves, entry breakdowns, and trade distributions"
)

st.caption("Use the sidebar to navigate between pages.")
