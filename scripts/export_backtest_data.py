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
from runners.symbol_defaults import get_session_v10_kwargs
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
    kwargs = get_session_v10_kwargs(symbol)

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

    daily_data = []
    for target_date in trading_dates:
        day_bars = [b for b in all_bars if b.timestamp.date() == target_date]
        session_bars = [b for b in day_bars if dt_time(4, 0) <= b.timestamp.time() <= dt_time(16, 0)]
        if len(session_bars) < 50:
            continue

        results = run_session_v10(
            session_bars, all_bars,
            **kwargs,
            fvg_mode="wick",
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


def main():
    """Export backtest data only. Version history and strategy metadata are
    maintained directly in data/*.json — this script does NOT overwrite them."""
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
