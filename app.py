"""
ICT Trading System — Portfolio Dashboard

Streamlit entrypoint. Run with:
    streamlit run dashboard/app.py
"""
import streamlit as st

st.set_page_config(
    page_title="ICT Trading System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("# ICT Futures Trading System")
st.markdown("---")

st.markdown(
    """
    Automated futures trading bot implementing **Inner Circle Trader (ICT)** concepts
    with algorithmic execution on E-mini and Micro E-mini S&P 500 and Nasdaq futures.

    ### What's Inside

    - **Strategy Overview** — 5 strategies (1 active, 4 experimental) with entry types, filters, and exit structure
    - **Strategy Flows** — 9 architecture diagrams covering the full signal-to-execution pipeline
    - **Version Timeline** — 17 versions from V6 to V10.15 with A/B test results
    - **Performance Dashboard** — Backtest results with equity curves, entry breakdowns, and trade distributions

    ### Architecture

    | Component | Technology |
    |-----------|-----------|
    | Strategy Engine | Python (custom) |
    | Market Data | TradingView (real-time 3m bars) |
    | Execution | Tradovate API + PickMyTrade webhooks |
    | Deployment | DigitalOcean droplet (auto-start 3:55 AM ET) |
    | Alerts | Telegram (entries, exits, hourly heartbeat, EOD outlook) |
    | Backtesting | Local bar storage with 90-day retention |

    ### Key Metrics (V10.15)

    | Metric | ES (19 days) | NQ (19 days) |
    |--------|:---:|:---:|
    | Win Rate | 87% | 82% |
    | Winning Days | 95% | 95% |
    | Entry Types | 4 (Creation, Retrace, Intraday, BOS) |  |
    | Filters | 2 mandatory + 2/3 optional (hybrid) |  |
    | Position Sizing | Dynamic (3/2/1 contracts) |  |

    ---

    Use the **sidebar** to navigate between pages.
    """
)
