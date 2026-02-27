"""
Export backtest data to JSON for Streamlit dashboard.

Run locally: python -m dashboard.scripts.export_backtest_data
Generates:
  - dashboard/data/backtest_results.json
  - dashboard/data/version_history.json
  - dashboard/data/strategy_metadata.json
"""
import sys
import json
import os
from datetime import time as dt_time, datetime
from pathlib import Path

sys.path.insert(0, '.')

from runners.bar_storage import load_bars_with_history
from runners.run_v10_dual_entry import run_session_v10
from version import STRATEGY_VERSION


DATA_DIR = Path('dashboard/data')


def serialize_trade(trade: dict) -> dict:
    """Convert trade result dict to JSON-serializable format."""
    result = {}
    for k, v in trade.items():
        if isinstance(v, datetime):
            result[k] = v.isoformat()
        elif k == 'exits':
            result[k] = []
            for exit in v:
                e = {}
                for ek, ev in exit.items():
                    if isinstance(ev, datetime):
                        e[ek] = ev.isoformat()
                    else:
                        e[ek] = ev
                result[k].append(e)
        else:
            result[k] = v
    return result


def export_backtest(symbol: str, days: int = 30) -> dict:
    """Run backtest and return structured results."""
    tick_size = 0.25
    tick_value = {
        'ES': 12.50, 'NQ': 5.00, 'MES': 1.25, 'MNQ': 0.50
    }.get(symbol, 12.50)
    min_risk_pts = 1.5 if symbol in ['ES', 'MES'] else 6.0
    max_bos_risk_pts = 8.0 if symbol in ['ES', 'MES'] else 20.0
    max_retrace_risk_pts = 8.0 if symbol in ['ES', 'MES'] else None

    print(f'Loading {symbol} bars...')
    all_bars = load_bars_with_history(symbol=symbol, interval='3m', n_bars=10000)
    if not all_bars:
        print(f'  No data for {symbol}')
        return {'symbol': symbol, 'days': []}

    # Get trading dates
    all_dates = sorted(set(b.timestamp.date() for b in all_bars), reverse=True)
    trading_dates = []
    for d in all_dates:
        day_bars = [b for b in all_bars if b.timestamp.date() == d]
        rth_bars = [b for b in day_bars if dt_time(9, 30) <= b.timestamp.time() <= dt_time(16, 0)]
        if len(rth_bars) >= 50:
            trading_dates.append(d)
        if len(trading_dates) >= days:
            break
    trading_dates = sorted(trading_dates)

    print(f'  Found {len(trading_dates)} trading days ({trading_dates[0]} to {trading_dates[-1]})')

    disable_bos = symbol in ['ES', 'MES']
    max_consec_losses = 2 if symbol in ['ES', 'MES'] else 0
    # V10.14 per-symbol opposing FVG exit
    opp_fvg_exit = True
    opp_fvg_min_ticks = 10 if symbol in ['ES', 'MES'] else 5
    opp_fvg_after_6r = True

    daily_data = []
    for target_date in trading_dates:
        day_bars = [b for b in all_bars if b.timestamp.date() == target_date]
        session_bars = [b for b in day_bars if dt_time(4, 0) <= b.timestamp.time() <= dt_time(16, 0)]
        if len(session_bars) < 50:
            continue

        results = run_session_v10(
            session_bars, all_bars,
            tick_size=tick_size, tick_value=tick_value, contracts=3,
            min_risk_pts=min_risk_pts,
            enable_creation_entry=True, enable_retracement_entry=True, enable_bos_entry=True,
            retracement_morning_only=False,
            t1_fixed_4r=True,
            midday_cutoff=True, pm_cutoff_nq=True,
            max_bos_risk_pts=max_bos_risk_pts,
            max_retrace_risk_pts=max_retrace_risk_pts,
            symbol=symbol,
            high_displacement_override=3.0,
            disable_bos_retrace=disable_bos,
            bos_daily_loss_limit=1,
            t1_r_target=3, trail_r_trigger=6,
            max_consec_losses=max_consec_losses,
            fvg_mode="wick",
            opposing_fvg_exit=opp_fvg_exit,
            opposing_fvg_min_ticks=opp_fvg_min_ticks,
            opposing_fvg_after_6r_only=opp_fvg_after_6r,
            entry_min_fvg_ticks=5,
        )

        trades_serialized = [serialize_trade(r) for r in results]
        day_pnl = sum(r['total_dollars'] for r in results)
        day_wins = sum(1 for r in results if r['total_dollars'] > 0)
        day_losses = sum(1 for r in results if r['total_dollars'] < 0)

        daily_data.append({
            'date': str(target_date),
            'trades': trades_serialized,
            'summary': {
                'num_trades': len(results),
                'wins': day_wins,
                'losses': day_losses,
                'total_pnl': day_pnl,
            }
        })
        status = 'WIN' if day_pnl > 0 else 'LOSS' if day_pnl < 0 else 'BE'
        print(f'  {target_date}: {len(results)} trades, {day_wins}W/{day_losses}L, ${day_pnl:+,.0f} [{status}]')

    return {
        'symbol': symbol,
        'tick_value': tick_value,
        'strategy_version': STRATEGY_VERSION,
        'exported_at': datetime.now().isoformat(),
        'days': daily_data,
    }


def build_version_history() -> list:
    """Build structured version history from CLAUDE.md data."""
    return [
        {"version": "V6", "date": "2025-10", "title": "Aggressive FVG Creation Entry",
         "category": "feature", "impact": "Single entry point, foundation strategy",
         "description": "Initial FVG-based entry strategy with aggressive creation entries at FVG formation."},
        {"version": "V7", "date": "2025-11", "title": "Profit-Protected 2nd Entry",
         "category": "feature", "impact": "Added re-entry capability after initial profit",
         "description": "Second entry allowed only after first trade secures profit, reducing drawdown risk."},
        {"version": "V8", "date": "2025-12", "title": "Independent 2nd Entry + Position Limit",
         "category": "feature", "impact": "Concurrent trade management with position limits",
         "description": "Decoupled second entry from first trade's outcome. Added max position limit to control exposure."},
        {"version": "V9", "date": "2026-01", "title": "Min Risk Filter + Opposing FVG Exit",
         "category": "risk", "impact": "Filtered tiny FVGs, added reversal detection",
         "description": "Skip FVGs with risk below minimum threshold. Exit on opposing FVG formation to catch reversals early."},
        {"version": "V10", "date": "2026-01", "title": "Quad Entry + Hybrid Exit",
         "category": "feature", "impact": "4 entry types, 3-contract exit structure",
         "description": "Added 4 entry types (Creation, Overnight Retrace, Intraday Retrace, BOS) with T1/T2/Runner hybrid exit."},
        {"version": "V10.1", "date": "2026-01", "title": "ADX >= 22 for Overnight Retrace",
         "category": "filter", "impact": "Filtered weak-trend retrace entries",
         "description": "B1 (overnight retrace) entries now require ADX >= 22 to ensure trend strength before entry."},
        {"version": "V10.2", "date": "2026-01", "title": "Midday + NQ PM Cutoff",
         "category": "filter", "impact": "Eliminated lunch-hour and late-session noise",
         "description": "No entries 12:00-14:00 (lunch lull). No NQ/MNQ/QQQ entries after 14:00 (low liquidity)."},
        {"version": "V10.3", "date": "2026-01", "title": "BOS Risk Cap + Disable SPY Intraday",
         "category": "risk", "impact": "ES max 8pts, NQ max 20pts BOS risk",
         "description": "Capped BOS entry risk to prevent oversized losses. Disabled SPY B2 entries (24% WR drag)."},
        {"version": "V10.4", "date": "2026-01", "title": "ATR Buffer for Equities",
         "category": "risk", "impact": "+$54k P/L improvement with adaptive stops",
         "description": "Equities use ATR(14) x 0.5 for stop buffer instead of fixed $0.02. Wider stops reduce stop-hunts."},
        {"version": "V10.5", "date": "2026-01", "title": "High Displacement Override",
         "category": "filter", "impact": "3x body skips ADX check for momentum entries",
         "description": "When candle body >= 3x average, skip the ADX >= 11 requirement. Catches explosive moves immediately."},
        {"version": "V10.6", "date": "2026-02", "title": "BOS LOSS_LIMIT Per-Symbol",
         "category": "performance", "impact": "+$1.2k P/L, -$500 drawdown",
         "description": "ES/MES: BOS disabled (20-38% WR). NQ/MNQ: BOS enabled with 1 loss/day limit. 64% BOS WR (up from 47.5%).",
         "ab_test": {"days": 12, "baseline_pl": "$118,406", "new_pl": "$124,881", "improvement": "+$6,475"}},
        {"version": "V10.7", "date": "2026-02", "title": "Dynamic Sizing + ADX Lowered",
         "category": "feature", "impact": "3-contract first trade, max 6 cts exposure",
         "description": "1st trade: 3 contracts (T1+T2+Runner). 2nd/3rd: 2 contracts (T1+T2). ADX lowered to >= 11 from 17."},
        {"version": "V10.8", "date": "2026-02", "title": "Hybrid Filter System",
         "category": "filter", "impact": "+$90k/30d, +71% more trades, same win rate",
         "description": "2 mandatory filters (DI direction, FVG size) + 2/3 optional (displacement, ADX, EMA trend).",
         "ab_test": {"days": 30, "improvement": "+$90,000", "extra_trades": "+71%"}},
        {"version": "V10.9", "date": "2026-02", "title": "R-Target Tuning (3R/6R)",
         "category": "performance", "impact": "+31% P/L, 87.7% WR, zero drawdown",
         "description": "T1 exit lowered from 4R to 3R, trail activation from 8R to 6R. Locks profit before most pullbacks.",
         "ab_test": {"days": 15, "baseline_pl": "$153,275", "new_pl": "$200,533", "improvement": "+$47,258", "wr_old": "69.2%", "wr_new": "87.7%"}},
        {"version": "V10.10", "date": "2026-02-17", "title": "Entry Cap Fix + Direction-Aware Breaker",
         "category": "bugfix", "impact": "+$350k/12d combined P/L",
         "description": "Fixed lifetime entry counter, direction-aware circuit breaker (3 losses/dir/day), equity FVG date filter, BOS parity, EOD outlook alert."},
        {"version": "V10.11", "date": "2026-02-20", "title": "Retrace Risk Cap + Instant Startup",
         "category": "risk", "impact": "ES retrace losses cut 50%, 57-min startup lag eliminated",
         "description": "ES/MES retrace risk > 8pts forces 1 contract (NQ uncapped). Live bot uses local bar history for instant warmup.",
         "ab_test": {"days": 15, "baseline_pl": "$144,613", "new_pl": "$145,825", "improvement": "+$1,212"}},
        {"version": "V10.12", "date": "2026-02-24", "title": "Backtest Parity Fixes",
         "category": "bugfix", "impact": "~11% gap reduced to ~2-3%",
         "description": "Trail logic fixes (~$850 recovered), parameter parity between live and backtest, risk manager tracking in paper mode."},
        {"version": "V10.13", "date": "2026-02-24", "title": "Global Consecutive Loss Stop",
         "category": "risk", "impact": "Feb 19 loss halved (-$900 to -$412)",
         "description": "ES/MES stop all trading after 2 consecutive losses. NQ exempt (consecutive losses precede big winners).",
         "ab_test": {"days": 17, "baseline_pl": "$160,706", "new_pl": "$161,194", "improvement": "+$488"}},
        {"version": "V10.14", "date": "2026-02-26", "title": "Opposing FVG Exit for T2/Runner",
         "category": "performance", "impact": "ES +$9,519/18d (+5.8%)",
         "description": "After 6R touch, exit T2/Runner on opposing FVG formation. Per-symbol: ES 10 ticks, NQ 5 ticks.",
         "ab_test": {"days": 18, "baseline_pl": "$163,350", "new_pl": "$172,869", "improvement": "+$9,519"}},
        {"version": "V10.15", "date": "2026-02-26", "title": "Bar-Aligned Scanning",
         "category": "bugfix", "impact": "Eliminates phantom FVGs from incomplete bars",
         "description": "Live bot scans synced to 3-min bar close + 5s buffer instead of fixed 180s interval. Prevents phantom FVGs from incomplete TradingView data."},
    ]


def build_strategy_metadata() -> list:
    """Build strategy card metadata."""
    return [
        {
            "id": "v10_fvg",
            "name": "ICT FVG Quad Entry",
            "version": STRATEGY_VERSION,
            "status": "ACTIVE",
            "color": "green",
            "instruments": ["ES", "NQ", "MES", "MNQ", "SPY", "QQQ"],
            "description": "Fair Value Gap strategy with 4 entry types, hybrid filter system, and dynamic position sizing. Deployed on DigitalOcean with PickMyTrade webhook execution.",
            "entry_types": [
                {"type": "A", "name": "Creation", "description": "Enter on FVG formation with displacement (3x override skips ADX)"},
                {"type": "B1", "name": "Overnight Retrace", "description": "Price retraces into overnight FVG + rejection (ADX >= 22)"},
                {"type": "B2", "name": "Intraday Retrace", "description": "Price retraces into session FVG (2+ bars old) + rejection"},
                {"type": "C", "name": "BOS + Retrace", "description": "Price retraces into FVG after Break of Structure"},
            ],
            "exit_structure": {
                "t1": "Fixed profit at 3R (1 contract)",
                "t2": "Structure trail with 4-tick buffer after 6R (1 contract)",
                "runner": "Structure trail with 6-tick buffer after 6R (1st trade only)",
            },
            "filters": ["DI Direction", "FVG Size >= 5 ticks", "Displacement >= 1.0x", "ADX >= 11", "EMA 20/50 Trend"],
            "tech_stack": ["Python", "TradingView", "Tradovate", "DigitalOcean", "Telegram", "PickMyTrade"],
        },
        {
            "id": "ict_state_machine",
            "name": "ICT State Machine",
            "version": "V1",
            "status": "DEPRECATED",
            "color": "gray",
            "instruments": ["ES"],
            "description": "Event-driven state machine approach to ICT concepts. Replaced by V10 FVG strategy due to complexity and lower performance.",
            "tech_stack": ["Python"],
        },
        {
            "id": "ict_sweep",
            "name": "ICT Liquidity Sweep",
            "version": "V1",
            "status": "EXPERIMENTAL",
            "color": "amber",
            "instruments": ["ES", "NQ"],
            "description": "Targets liquidity sweeps above/below previous session highs/lows followed by FVG formation. Captures stop-hunt reversals.",
            "tech_stack": ["Python", "TradingView"],
        },
        {
            "id": "ict_ote",
            "name": "ICT Optimal Trade Entry",
            "version": "V1",
            "status": "EXPERIMENTAL",
            "color": "amber",
            "instruments": ["ES", "NQ"],
            "description": "Fibonacci-based entries at the 62-79% retracement zone within a higher-timeframe displacement leg. Classic ICT setup.",
            "tech_stack": ["Python", "TradingView"],
        },
        {
            "id": "ttfm",
            "name": "TTFM Trend Follower",
            "version": "V2",
            "status": "EXPERIMENTAL",
            "color": "amber",
            "instruments": ["ES", "NQ"],
            "description": "Trend-following momentum strategy using ADX, moving averages, and volume confirmation. Multi-timeframe analysis for entry timing.",
            "tech_stack": ["Python", "TradingView"],
        },
    ]


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Export backtest results for ES and NQ
    all_results = {}
    for symbol in ['ES', 'NQ']:
        result = export_backtest(symbol, days=30)
        all_results[symbol] = result

    backtest_path = DATA_DIR / 'backtest_results.json'
    with open(backtest_path, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f'\nBacktest results saved to {backtest_path}')

    # Export version history
    version_path = DATA_DIR / 'version_history.json'
    with open(version_path, 'w') as f:
        json.dump(build_version_history(), f, indent=2)
    print(f'Version history saved to {version_path}')

    # Export strategy metadata
    metadata_path = DATA_DIR / 'strategy_metadata.json'
    with open(metadata_path, 'w') as f:
        json.dump(build_strategy_metadata(), f, indent=2)
    print(f'Strategy metadata saved to {metadata_path}')

    # Print summary
    for symbol, data in all_results.items():
        days = data['days']
        total_trades = sum(d['summary']['num_trades'] for d in days)
        total_pnl = sum(d['summary']['total_pnl'] for d in days)
        total_wins = sum(d['summary']['wins'] for d in days)
        wr = (total_wins / total_trades * 100) if total_trades > 0 else 0
        print(f'\n{symbol}: {len(days)} days, {total_trades} trades, {wr:.1f}% WR, ${total_pnl:+,.0f}')


if __name__ == '__main__':
    main()
