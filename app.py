"""
ICT Trading System — Portfolio Dashboard

Streamlit entrypoint. Run with:
    streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="ICT Trading System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# ICT Futures Trading System")
st.markdown(
    "Automated futures trading bot implementing **Inner Circle Trader (ICT)** concepts "
    "with algorithmic execution on E-mini and Micro E-mini S&P 500 and Nasdaq futures."
)

st.markdown("---")

# Architecture and navigation in columns
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Architecture")
    st.markdown("""
| Component | Technology |
|-----------|-----------|
| Strategy Engine | Python (custom) |
| Market Data | TradingView (real-time 3m bars) |
| Execution | Tradovate API + PickMyTrade webhooks |
| Deployment | DigitalOcean droplet (auto-start 3:55 AM ET) |
| Alerts | Telegram (entries, exits, heartbeat, EOD outlook) |
| Backtesting | Local bar storage with 90-day retention |
""")

with col2:
    st.markdown("### Key Metrics (V10.15)")
    st.markdown("""
| Metric | ES (19d) | NQ (19d) |
|--------|:---:|:---:|
| Win Rate | 87% | 82% |
| Winning Days | 95% | 95% |
| Entry Types | 4 | 4 |
| Filters | Hybrid (2 + 2/3) | Hybrid (2 + 2/3) |
| Sizing | Dynamic (3/2/1 ct) | Dynamic (3/2/1 ct) |
""")

st.markdown("---")

st.markdown("### Pages")
st.markdown(
    "- **Strategy Overview** — 5 strategies with entry types, filters, and exit structure\n"
    "- **Strategy Flows** — 9 architecture diagrams covering the signal-to-execution pipeline\n"
    "- **Version Timeline** — 20 versions from V6 to V10.15 with A/B test results\n"
    "- **Performance** — Backtest equity curves, entry breakdowns, and trade distributions"
)

st.caption("Use the sidebar to navigate between pages.")
