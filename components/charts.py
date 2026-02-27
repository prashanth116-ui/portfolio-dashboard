"""Plotly chart builders for performance dashboard."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


COLORS = {
    'green': '#00d97e',
    'red': '#e63757',
    'blue': '#2c7be5',
    'amber': '#f6c343',
    'gray': '#6e84a3',
    'bg': '#0e1117',
    'card_bg': '#1a1d23',
    'text': '#e6e6e6',
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color=COLORS['text'], size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
)


def equity_curve(daily_data: list, show_dollars: bool) -> go.Figure:
    """Cumulative P/L line chart."""
    dates = [d['date'] for d in daily_data]
    cumulative = []
    running = 0
    for d in daily_data:
        running += d['summary']['total_pnl']
        cumulative.append(running if show_dollars else running / 375.0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=cumulative,
        mode='lines+markers',
        line=dict(color=COLORS['blue'], width=2),
        marker=dict(size=5),
        fill='tozeroy',
        fillcolor='rgba(44,123,229,0.1)',
        name='Cumulative P/L',
    ))
    label = 'Cumulative P/L ($)' if show_dollars else 'Cumulative P/L (R)'
    fig.update_layout(title=label, yaxis_title=label, xaxis_title='Date', **LAYOUT_DEFAULTS)
    return fig


def daily_pnl_bars(daily_data: list, show_dollars: bool) -> go.Figure:
    """Daily P/L bar chart (green/red)."""
    dates = [d['date'] for d in daily_data]
    pnls = [d['summary']['total_pnl'] if show_dollars else d['summary']['total_pnl'] / 375.0
            for d in daily_data]
    colors = [COLORS['green'] if p >= 0 else COLORS['red'] for p in pnls]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=dates, y=pnls, marker_color=colors, name='Daily P/L'))
    label = 'Daily P/L ($)' if show_dollars else 'Daily P/L (R)'
    fig.update_layout(title=label, yaxis_title=label, xaxis_title='Date', **LAYOUT_DEFAULTS)
    return fig


def entry_type_pie(trades: list) -> go.Figure:
    """Entry type breakdown pie chart."""
    counts = {}
    for t in trades:
        et = t.get('entry_type', 'UNKNOWN')
        counts[et] = counts.get(et, 0) + 1

    labels = list(counts.keys())
    values = list(counts.values())
    pie_colors = [COLORS['blue'], COLORS['green'], COLORS['amber'], COLORS['red']]

    fig = go.Figure()
    fig.add_trace(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=pie_colors[:len(labels)]),
        hole=0.4,
        textinfo='label+percent',
        textfont=dict(size=12),
    ))
    fig.update_layout(title='Entry Type Breakdown', showlegend=False, **LAYOUT_DEFAULTS)
    return fig


def win_rate_gauge(win_rate: float) -> go.Figure:
    """Win rate gauge chart."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=win_rate,
        number=dict(suffix="%", font=dict(size=36)),
        gauge=dict(
            axis=dict(range=[0, 100], tickwidth=1, tickcolor=COLORS['text']),
            bar=dict(color=COLORS['green'] if win_rate >= 70 else COLORS['amber'] if win_rate >= 50 else COLORS['red']),
            bgcolor='rgba(255,255,255,0.05)',
            steps=[
                dict(range=[0, 50], color='rgba(230,55,87,0.15)'),
                dict(range=[50, 70], color='rgba(246,195,67,0.15)'),
                dict(range=[70, 100], color='rgba(0,217,126,0.15)'),
            ],
        ),
        title=dict(text='Win Rate', font=dict(size=16)),
    ))
    fig.update_layout(height=250, **LAYOUT_DEFAULTS)
    return fig


def trade_distribution(trades: list, show_dollars: bool) -> go.Figure:
    """Trade P/L distribution histogram."""
    pnls = [t['total_dollars'] if show_dollars else t['total_dollars'] / 375.0 for t in trades]

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=pnls,
        nbinsx=30,
        marker_color=COLORS['blue'],
        opacity=0.8,
    ))
    label = 'Trade P/L ($)' if show_dollars else 'Trade P/L (R)'
    fig.update_layout(title='Trade P/L Distribution', xaxis_title=label, yaxis_title='Count', **LAYOUT_DEFAULTS)
    return fig


def exit_type_breakdown(trades: list) -> go.Figure:
    """Breakdown of exit types across all trades."""
    exit_counts = {}
    for t in trades:
        for e in t.get('exits', []):
            etype = e.get('type', 'UNKNOWN')
            exit_counts[etype] = exit_counts.get(etype, 0) + 1

    if not exit_counts:
        return go.Figure()

    labels = list(exit_counts.keys())
    values = list(exit_counts.values())

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=values, marker_color=COLORS['blue']))
    fig.update_layout(title='Exit Type Breakdown', xaxis_title='Exit Type', yaxis_title='Count', **LAYOUT_DEFAULTS)
    return fig
