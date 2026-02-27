"""Privacy-aware metric display helpers."""
import streamlit as st


def compute_avg_risk(trades: list) -> float:
    """Compute average risk in dollars from trade data for R-multiple conversion."""
    risks = []
    for t in trades:
        risk_pts = t.get('risk', 0)
        contracts = t.get('contracts', 1)
        # Infer tick value from trade data: total_dollars / (total_pnl / tick_size)
        # Simpler: use risk * contracts as proxy since risk is in points
        # We need dollar risk, which is risk_pts / tick_size * tick_value * contracts
        # But we don't have tick_size/tick_value here. Use total_dollars/total_pnl ratio.
        total_pnl = t.get('total_pnl', 0)
        total_dollars = t.get('total_dollars', 0)
        if total_pnl != 0 and total_dollars != 0:
            dollar_per_point = abs(total_dollars / total_pnl)
            risks.append(risk_pts * dollar_per_point)
    if risks:
        return sum(risks) / len(risks)
    return 375.0  # Fallback


def format_dollar(value: float, show_dollars: bool, avg_risk: float = 375.0) -> str:
    """Format a dollar value, respecting privacy toggle."""
    if show_dollars:
        return f"${value:+,.0f}" if value != 0 else "$0"
    r_val = value / avg_risk if avg_risk > 0 else 0
    return f"{r_val:+,.1f}R"


def format_dollar_abs(value: float, show_dollars: bool, avg_risk: float = 375.0) -> str:
    """Format absolute dollar value (no sign)."""
    if show_dollars:
        return f"${value:,.0f}"
    r_val = value / avg_risk if avg_risk > 0 else 0
    return f"{r_val:,.1f}R"


def show_privacy_toggle() -> bool:
    """Show privacy toggle in sidebar, return True if dollars should be shown."""
    return st.sidebar.toggle("Show dollar amounts", value=False,
                             help="Toggle between dollar amounts and R-multiples for portfolio sharing")
