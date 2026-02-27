"""Page 4: Performance Dashboard — Charts, metrics, and privacy toggle."""
import json
from pathlib import Path

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.metrics import show_privacy_toggle, format_dollar, format_dollar_abs, compute_avg_risk
from components.charts import (
    equity_curve, daily_pnl_bars, entry_type_pie,
    win_rate_by_entry_type, trade_distribution, exit_type_breakdown,
)

st.set_page_config(page_title="Performance", page_icon="📈", layout="wide")

st.markdown("# Performance Dashboard")
st.markdown("---")


# Load data with caching
@st.cache_data
def load_backtest_data():
    data_path = Path(__file__).parent.parent / 'data' / 'backtest_results.json'
    with open(data_path) as f:
        return json.load(f)


all_data = load_backtest_data()

# Sidebar controls
show_dollars = show_privacy_toggle()

available_symbols = list(all_data.keys())
symbol_choice = st.sidebar.selectbox("Symbol", ["Combined"] + available_symbols)

# Combine data based on selection
if symbol_choice == "Combined":
    date_map = {}
    for sym, sym_data in all_data.items():
        for day in sym_data['days']:
            dt = day['date']
            if dt not in date_map:
                date_map[dt] = {'date': dt, 'trades': [], 'summary': {'num_trades': 0, 'wins': 0, 'losses': 0, 'total_pnl': 0}}
            date_map[dt]['trades'].extend(day['trades'])
            date_map[dt]['summary']['num_trades'] += day['summary']['num_trades']
            date_map[dt]['summary']['wins'] += day['summary']['wins']
            date_map[dt]['summary']['losses'] += day['summary']['losses']
            date_map[dt]['summary']['total_pnl'] += day['summary']['total_pnl']
    daily_data = sorted(date_map.values(), key=lambda x: x['date'])
    display_symbol = "ES + NQ Combined"
else:
    daily_data = all_data[symbol_choice]['days']
    display_symbol = symbol_choice

# Flatten all trades
all_trades = []
for day in daily_data:
    all_trades.extend(day['trades'])

# Compute avg risk for R-multiple conversion
avg_risk = compute_avg_risk(all_trades)

# Compute summary metrics
total_trades = len(all_trades)
total_wins = sum(1 for t in all_trades if t['total_dollars'] > 0)
total_losses = sum(1 for t in all_trades if t['total_dollars'] < 0)
win_rate = (total_wins / total_trades * 100) if total_trades > 0 else 0
total_pnl = sum(t['total_dollars'] for t in all_trades)

gross_profit = sum(t['total_dollars'] for t in all_trades if t['total_dollars'] > 0)
gross_loss = abs(sum(t['total_dollars'] for t in all_trades if t['total_dollars'] < 0))
profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

winning_days = sum(1 for d in daily_data if d['summary']['total_pnl'] > 0)
total_days = len(daily_data)
day_win_rate = (winning_days / total_days * 100) if total_days > 0 else 0

# Max drawdown
peak = 0
max_dd = 0
cumulative = 0
for d in daily_data:
    cumulative += d['summary']['total_pnl']
    if cumulative > peak:
        peak = cumulative
    dd = peak - cumulative
    if dd > max_dd:
        max_dd = dd

avg_daily = total_pnl / total_days if total_days > 0 else 0

# Summary header
st.markdown(f"### {display_symbol}")
version = all_data.get(symbol_choice, {}).get('strategy_version', 'V10.15') if symbol_choice != 'Combined' else 'V10.15'
st.caption(f"{total_days} trading days | {version}")

# Metrics — row 1
row1 = st.columns(3)
with row1[0]:
    st.metric("Total Trades", total_trades)
with row1[1]:
    st.metric("Win Rate", f"{win_rate:.1f}%")
with row1[2]:
    pf_str = f"{profit_factor:.1f}" if profit_factor != float('inf') else "INF"
    st.metric("Profit Factor", pf_str)

# Metrics — row 2
row2 = st.columns(3)
with row2[0]:
    st.metric("Max Drawdown", format_dollar_abs(max_dd, show_dollars, avg_risk))
with row2[1]:
    st.metric("Avg Daily P/L", format_dollar(avg_daily, show_dollars, avg_risk))
with row2[2]:
    st.metric("Day Win Rate", f"{day_win_rate:.0f}% ({winning_days}/{total_days})")

st.markdown("---")

# Charts — row 1
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(equity_curve(daily_data, show_dollars, avg_risk), use_container_width=True)
with col2:
    st.plotly_chart(daily_pnl_bars(daily_data, show_dollars, avg_risk), use_container_width=True)

# Charts — row 2
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(entry_type_pie(all_trades), use_container_width=True)
with col4:
    st.plotly_chart(win_rate_by_entry_type(all_trades), use_container_width=True)

# Charts — row 3
col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(trade_distribution(all_trades, show_dollars, avg_risk), use_container_width=True)
with col6:
    st.plotly_chart(exit_type_breakdown(all_trades), use_container_width=True)

# Daily breakdown table with cumulative P/L
st.markdown("---")
st.markdown("### Daily Breakdown")

table_data = []
running_pnl = 0
for d in daily_data:
    s = d['summary']
    wr = (s['wins'] / s['num_trades'] * 100) if s['num_trades'] > 0 else 0
    running_pnl += s['total_pnl']
    table_data.append({
        'Date': d['date'],
        'Trades': s['num_trades'],
        'Wins': s['wins'],
        'Losses': s['losses'],
        'Win Rate': f"{wr:.0f}%",
        'P/L': format_dollar(s['total_pnl'], show_dollars, avg_risk),
        'Cumulative': format_dollar(running_pnl, show_dollars, avg_risk),
    })

st.dataframe(table_data, use_container_width=True, hide_index=True)
