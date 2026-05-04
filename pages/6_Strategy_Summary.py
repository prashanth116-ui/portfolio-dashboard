"""Page 6: V10.16 Strategy Summary — End-to-end ICT FVG strategy documentation."""
from pathlib import Path

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.responsive import inject_responsive_css

st.set_page_config(page_title="Strategy Summary", page_icon="📋", layout="wide")
inject_responsive_css()

st.markdown("# V10.16 ICT FVG Strategy")
st.caption("Intraday futures strategy using Fair Value Gaps on 3-minute bars")
st.markdown("---")

# --- Overview metrics ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Version", "V10.16")
with c2:
    st.metric("Instruments", "ES, NQ, MES, MNQ")
with c3:
    st.metric("Timeframe", "3-min bars")
with c4:
    st.metric("Session", "04:00-16:00 ET")

st.markdown("---")

# --- How It Works ---
st.markdown("### How It Works")
st.markdown("""
The strategy detects **Fair Value Gaps (FVGs)** — 3-bar price gaps where the high of bar 1 doesn't overlap
the low of bar 3 (bullish) or vice versa. These gaps represent institutional order flow imbalances.
When price creates or retraces into an FVG with sufficient momentum and trend alignment, the bot enters
a position with a multi-contract exit structure designed to lock profit early while letting runners capture
extended moves.
""")

# --- Signal Pipeline ---
st.markdown("### Signal Pipeline")
st.markdown("""
```
TradingView 3-min bars (bar-aligned scan every 3 min)
    │
    ▼
FVG Detection (wick-based boundaries)
    │
    ▼
Hybrid Filter System (2 mandatory + 2/3 optional)
    │
    ▼
Entry Type Classification (Creation / Retrace / BOS)
    │
    ▼
Risk Manager Gate (consecutive losses, daily limits, position limits)
    │
    ▼
Dynamic Position Sizing (1st trade: 3 cts, 2nd+: 2 cts)
    │
    ▼
Multi-Target Exit (T1 fixed → Trail → T2 lock → Runner)
```
""")

st.markdown("---")

# --- Entry Types ---
st.markdown("### Entry Types")

entry_data = [
    {
        "type": "A — Creation",
        "trigger": "Enter immediately when FVG forms with displacement",
        "confirmation": "2-scan confirmation (live bot only — must persist across consecutive scans)",
        "notes": "Primary entry type (~72% of all trades). 3x displacement override skips ADX filter.",
    },
    {
        "type": "B1 — Overnight Retrace",
        "trigger": "Price retraces into overnight FVG with rejection wick",
        "confirmation": "Inherently confirmed (FVG is from prior session)",
        "notes": "Requires ADX >= 22. Morning only (09:30-12:00).",
    },
    {
        "type": "B2 — Intraday Retrace",
        "trigger": "Price retraces into session FVG (2+ bars old) with rejection",
        "confirmation": "No 2-scan filter (uses older FVGs that are inherently confirmed)",
        "notes": "Disabled for SPY (24% WR drag). Primary source of live-backtest divergence.",
    },
    {
        "type": "C — BOS Retrace",
        "trigger": "Price retraces into FVG after Break of Structure",
        "confirmation": "Inherently confirmed (post-BOS FVG)",
        "notes": "ES/MES/SPY: disabled. NQ/MNQ/QQQ: enabled with 1 loss/day limit.",
    },
]

for entry in entry_data:
    with st.container(border=True):
        st.markdown(f"**{entry['type']}**")
        st.markdown(f"**Trigger:** {entry['trigger']}")
        st.markdown(f"**Confirmation:** {entry['confirmation']}")
        st.caption(entry['notes'])

st.markdown("---")

# --- Hybrid Filter System ---
st.markdown("### Hybrid Filter System")
st.markdown("Separates filters into mandatory (must pass) and optional (2 of 3 must pass).")

col_m, col_o = st.columns(2)
with col_m:
    st.markdown("#### Mandatory (must pass)")
    st.markdown("""
| Filter | Condition |
|--------|-----------|
| DI Direction | +DI > -DI for LONG, -DI > +DI for SHORT |
| FVG Size | >= 5 ticks |
""")

with col_o:
    st.markdown("#### Optional (2 of 3 must pass)")
    st.markdown("""
| Filter | Condition |
|--------|-----------|
| Displacement | >= 1.0x average candle body |
| ADX | >= 11 (or >= 10 with 3x displacement) |
| EMA Trend | EMA20 > EMA50 for LONG, < for SHORT |
""")

st.markdown("---")

# --- Position Sizing ---
st.markdown("### Position Sizing")

sz1, sz2 = st.columns(2)
with sz1:
    st.markdown("#### Dynamic Contract Allocation")
    st.markdown("""
| Trade # | Contracts | Structure |
|---------|-----------|-----------|
| 1st in direction | 3 | T1 + T2 + Runner |
| 2nd in direction | 2 | T1 + T2 (no runner) |
| 3rd in direction | 2 | T1 + T2 (no runner) |
""")
    st.caption("Max 3 open trades per direction. Max 6 contracts total exposure.")

with sz2:
    st.markdown("#### Risk Management")
    st.markdown("""
| Control | ES/MES | NQ/MNQ |
|---------|--------|--------|
| Min risk | 1.5 pts | 6.0 pts |
| Max BOS risk | 8.0 pts | 20.0 pts |
| Retrace risk cap | 8.0 pts (force 1 ct) | No cap |
| Consec loss stop | 2 / symbol / day | 3 / symbol / day |
| Max losses/dir | 3 / direction / day | 3 / direction / day |
""")

st.markdown("---")

# --- Exit Structure ---
st.markdown("### Exit Structure")
st.markdown("Multi-target exits lock profit progressively while allowing runners to capture extended moves.")

es_col, nq_col = st.columns(2)

with es_col:
    st.markdown("#### ES / MES (T2 fixed at 5R)")
    st.markdown("""
```
Entry @ FVG midpoint
  │
  ▼ Price hits 3R
T1 (1 ct): FIXED exit at 3R ✓
  Stop moves to breakeven
  │
  ▼ Price hits 4R
  Trail activates (3R floor)
  │
  ▼ Price hits 5R
T2 (1 ct): FIXED exit at 5R ✓
  │
  ▼ Only Runner remains
Runner (1 ct): Structure trail
  with 6-tick buffer until
  trail stop or EOD
```
""")

with nq_col:
    st.markdown("#### NQ / MNQ (T2 trails)")
    st.markdown("""
```
Entry @ FVG midpoint
  │
  ▼ Price hits 3R
T1 (1 ct): FIXED exit at 3R ✓
  Stop moves to breakeven
  │
  ▼ Price hits 4R
  Trail activates (3R floor)
  │
  ▼ T2 trails with 4-tick buffer
  ▼ Runner trails with 6-tick buffer
  │
T2 + Runner ride trends until
  trail stop or EOD
  (big NQ moves go 10-20R)
```
""")

st.caption(
    "Per-symbol philosophy: ES benefits from locking profit early (T2 at 5R). "
    "NQ benefits from letting runners ride — big NQ trends go 10-20R."
)

st.markdown("---")

# --- Per-Symbol Philosophy ---
st.markdown("### Per-Symbol Configuration Philosophy")
st.markdown("""
A consistent pattern across 6 A/B tests: **ES benefits from tighter risk management,
NQ benefits from letting runners run.** Every per-symbol decision follows this principle:
""")

st.markdown("""
| Feature | ES / MES | NQ / MNQ | Why |
|---------|----------|----------|-----|
| BOS entries | **OFF** | ON (1 loss/day limit) | ES BOS: 20-38% WR, net drag. NQ BOS recovers. |
| Retrace risk cap | **8.0 pts (force 1 ct)** | No cap | NQ wide retraces catch big trends (+$18.6k uncapped) |
| T2 exit | **Fixed at 5R** | Trail (4-tick buffer) | ES pullbacks hit at 5-7R. NQ trends go 10-20R. |
| Consec loss stop | **2 / symbol** | 3 / symbol | ES whipsaw costs $5k+. NQ 2-consec often precedes recovery. |
| Opposing FVG exit | 10-tick min after 4R | 5-tick min after 4R | ES reversals are sharp. NQ: small filter to catch extremes. |
""")

st.markdown("---")

# --- Time Filters ---
st.markdown("### Time Filters")
st.markdown("""
| Filter | Window | Effect |
|--------|--------|--------|
| Trading session | 04:00-16:00 ET | All entries |
| Overnight retrace (B1) | 09:30-12:00 only | Morning setups only |
| Midday cutoff | 12:00-14:00 | No new entries during lunch lull |
| PM cutoff | After 14:00 | No NQ/MNQ/QQQ entries (trend exhaustion) |
""")

st.markdown("---")

# --- Live Bot Architecture ---
st.markdown("### Live Bot Architecture")

st.markdown("""
| Component | Purpose |
|-----------|---------|
| **Bar-aligned scanning** | Scans fire at :00:05, :03:05, :06:05 — always processing finalized bars |
| **2-scan confirmation** | CREATION entries must appear in 2 consecutive scans (filters phantom FVGs) |
| **Risk manager** | Consecutive loss tracking, daily limits, position limits — all per-symbol |
| **Paper mode** | Full trade lifecycle simulation — source of truth for P/L |
| **Webhook executor** | PickMyTrade.trade integration for multi-account Tradovate execution |
| **Telegram alerts** | Entry/exit events, hourly heartbeat, daily summary, EOD next-day outlook |
| **Local bar storage** | Saves 3m bars to CSV daily for 30+ day backtests (90-day retention) |
""")

st.markdown("---")

# --- Live vs Backtest ---
st.markdown("### Live vs Backtest Divergence")
st.markdown("""
The live bot trails the backtest by ~43% over 45 days. This is an inherent gap — not a code bug.
""")

st.markdown("""
| Metric | Live Bot (45d) | Backtest (45d) |
|--------|---------------:|---------------:|
| Trades | 314 | 392 |
| Win Rate | 55.7% | 78.3% |
| Winning Days | 80% | 91% |
""")

with st.expander("Root Cause Analysis"):
    st.markdown("""
**Real-time vs finalized bars:** TradingView 3-minute bars have incomplete OHLC data while candles
are still forming. Even with the 5-second post-bar-close buffer, some bars take longer to finalize.
This produces **phantom FVGs** — gaps that exist on incomplete data but vanish once the bar closes.

**Impact chain:**
1. Phantom FVG triggers entry (usually INTRADAY_RETRACE — no 2-scan confirmation)
2. FVG disappears on next bar → price immediately hits stop → loss
3. Loss increments consecutive loss counter
4. Counter hits limit (2 for ES, 3 for NQ) → blocks subsequent real entries
5. Blocked entries would have been winners in backtest

**Key finding:** INTRADAY_RETRACE entries have 28% win rate live vs ~80% in backtest.
They generate 47% of all system losses but only 3% of total profit.

**Mitigations deployed:**
- Bar-aligned scanning (V10.15) — scans 5s after bar close
- 2-scan confirmation for CREATION entries — filters ~90% of phantom CREATION FVGs
- Consecutive loss stop — limits damage cascades

**Under investigation:**
- Post-entry FVG validation (close phantom trades immediately)
- Increase bar-close buffer (5s → 15-20s)
- Disable INTRADAY_RETRACE for live bot entirely
""")

st.markdown("---")

# --- Backtest Results ---
st.markdown("### 22-Day Validation Results (V10.16)")

st.markdown("""
| Symbol | Trades | Win Rate | Total P/L | Day Win Rate | Max Drawdown |
|--------|--------|----------|-----------|-------------|-------------|
| ES | 219 | 84.5% | +$191,231 | 100% (22/22) | $0 |
| MES | 210 | 81.9% | +$17,864 | 100% (22/22) | $0 |
| NQ | 169 | 82.2% | +$340,743 | 90.9% (20/22) | $778 |
| MNQ | 162 | 80.9% | +$31,349 | 90.9% (20/22) | $55 |
| **Combined** | **760** | **82.5%** | **+$581,187** | — | **$778** |
""")

st.caption("Backtest uses finalized bar data — live performance will be lower due to real-time data differences.")
