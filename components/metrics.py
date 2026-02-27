"""Privacy-aware metric display helpers."""
import streamlit as st


def format_dollar(value: float, show_dollars: bool) -> str:
    """Format a dollar value, respecting privacy toggle."""
    if show_dollars:
        return f"${value:+,.0f}" if value != 0 else "$0"
    # Convert to R-multiples (rough: avg risk ~$375 for ES 3ct)
    r_val = value / 375.0
    return f"{r_val:+,.1f}R"


def format_dollar_abs(value: float, show_dollars: bool) -> str:
    """Format absolute dollar value (no sign)."""
    if show_dollars:
        return f"${value:,.0f}"
    r_val = value / 375.0
    return f"{r_val:,.1f}R"


def metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Render a metric with optional delta."""
    st.metric(label=label, value=value, delta=delta, delta_color=delta_color)


def show_privacy_toggle() -> bool:
    """Show privacy toggle in sidebar, return True if dollars should be shown."""
    return st.sidebar.toggle("Show dollar amounts", value=False,
                             help="Toggle between dollar amounts and R-multiples for portfolio sharing")
