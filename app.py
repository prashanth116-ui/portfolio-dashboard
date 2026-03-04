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
from components.responsive import inject_responsive_css

st.set_page_config(
    page_title="Prashanth Sundaram — Portfolio",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_responsive_css()


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
    st.metric("Projects", len(projects))
with col2:
    st.metric("Trading Systems", "3 repos")
with col3:
    st.metric("Strategies", len(strategies))

st.markdown("---")

# --- Software Projects (2x2) ---
header1, link1 = st.columns([4, 1])
with header1:
    st.markdown("### Software Projects")
with link1:
    st.page_link("pages/1_Software_Projects.py", label="View all →")

n_cols = 3
rows = [projects[i:i + n_cols] for i in range(0, len(projects), n_cols)]
for row in rows:
    cols = st.columns(n_cols)
    for i, proj in enumerate(row):
        with cols[i]:
            render_project_card_mini(proj)
            st.page_link("pages/1_Software_Projects.py", label="Details →")

st.markdown("---")

# --- Trading Systems (3 columns) ---
header2, link2 = st.columns([4, 1])
with header2:
    st.markdown("### Trading Systems")
with link2:
    st.page_link("pages/2_Trading_Strategies.py", label="View all →")

# Group strategies by repo/system
trading_systems = [
    {
        "name": "tradovate-futures-bot",
        "status": "ACTIVE",
        "version": "V10.16",
        "instruments": ["ES", "NQ", "MES", "MNQ", "SPY", "QQQ"],
        "tagline": "ICT intraday — 4 entry types, 82.5% WR, per-symbol trail optimization",
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

STATUS_EMOJI = {
    'ACTIVE': '\U0001F7E2',
    'IN_DEVELOPMENT': '\U0001F535',
    'EXPERIMENTAL': '\U0001F7E0',
}

STATUS_LABELS = {
    'ACTIVE': 'Active',
    'IN_DEVELOPMENT': 'In Development',
    'EXPERIMENTAL': 'Experimental',
}

tcols = st.columns(3)
for i, sys_info in enumerate(trading_systems):
    with tcols[i]:
        emoji = STATUS_EMOJI.get(sys_info['status'], '\u26AA')
        label = STATUS_LABELS.get(sys_info['status'], sys_info['status'])
        with st.container(border=True):
            st.markdown(f"**{sys_info['name']}**")
            st.caption(sys_info['tagline'])
            st.markdown(f"{emoji} {label} | {sys_info['version']}")
            st.caption(f"Instruments: {', '.join(sys_info['instruments'])}")
            tags = " ".join([f"`{t}`" for t in sys_info['tech_stack']])
            st.markdown(tags)
            st.page_link("pages/2_Trading_Strategies.py", label="Details →")

st.markdown("---")
st.markdown("### Pages")

page_links = [
    ("pages/1_Software_Projects.py", "Software Projects", "11 project cards with status, completion, and tech stack"),
    ("pages/2_Trading_Strategies.py", "Trading Strategies", "6 strategies across 3 repos with entry types, filters, and exits"),
    ("pages/3_Strategy_Flows.py", "Strategy Flows", "9 architecture diagrams covering the signal-to-execution pipeline"),
    ("pages/4_Version_Timeline.py", "Version Timeline", "21 versions from V6 to V10.16 with A/B test results"),
    ("pages/5_Performance.py", "Performance", "Backtest equity curves, entry breakdowns, and trade distributions"),
]

for path, name, desc in page_links:
    st.page_link(path, label=f"**{name}** — {desc}")
