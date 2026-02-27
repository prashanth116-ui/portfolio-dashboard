"""Project card rendering with status badges, completion bars, and tech tags."""
import streamlit as st


STATUS_COLORS = {
    'COMPLETE': '#00d97e',
    'IN_PROGRESS': '#2c7be5',
    'RESEARCH': '#f6c343',
    'ACTIVE': '#00d97e',
    'EXPERIMENTAL': '#f6c343',
    'IN_DEVELOPMENT': '#2c7be5',
    'DEPRECATED': '#6e84a3',
}

STATUS_DOTS = {
    'COMPLETE': 'green',
    'IN_PROGRESS': 'blue',
    'RESEARCH': 'orange',
    'ACTIVE': 'green',
    'EXPERIMENTAL': 'orange',
    'IN_DEVELOPMENT': 'blue',
    'DEPRECATED': 'gray',
}

STATUS_LABELS = {
    'COMPLETE': 'Complete',
    'IN_PROGRESS': 'In Progress',
    'RESEARCH': 'Research',
    'ACTIVE': 'Active',
    'EXPERIMENTAL': 'Experimental',
    'IN_DEVELOPMENT': 'In Development',
    'DEPRECATED': 'Deprecated',
}

STATUS_EMOJI = {
    'COMPLETE': '\U0001F7E2',
    'IN_PROGRESS': '\U0001F535',
    'RESEARCH': '\U0001F7E0',
    'ACTIVE': '\U0001F7E2',
    'EXPERIMENTAL': '\U0001F7E0',
    'IN_DEVELOPMENT': '\U0001F535',
    'DEPRECATED': '\u26AA',
}


def _completion_bar(pct: int, color: str):
    """Render a CSS progress bar."""
    st.markdown(
        f'<div style="background:#1a1d23;border-radius:4px;height:8px;width:100%;margin:4px 0 8px 0">'
        f'<div style="background:{color};border-radius:4px;height:8px;width:{pct}%"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_project_card(project: dict):
    """Render a software project card with status badge, completion bar, and tech tags."""
    status = project['status']
    color = STATUS_COLORS.get(status, '#6e84a3')
    emoji = STATUS_EMOJI.get(status, '\u26AA')
    label = STATUS_LABELS.get(status, status)

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {project['name']}")
        with col2:
            st.markdown(f"{emoji} **{label}**")

        st.markdown(project.get('tagline', ''))

        # Completion bar (skip for research/0%)
        pct = project.get('completion', 0)
        if pct > 0:
            st.caption(f"{pct}% complete")
            _completion_bar(pct, color)

        st.markdown(project['description'])

        # Tech tags
        if project.get('tech_stack'):
            tags = " ".join([f"`{t}`" for t in project['tech_stack']])
            st.markdown(tags)

        # Features
        if project.get('features'):
            with st.expander("Key Features"):
                for f in project['features']:
                    st.markdown(f"- {f}")

        # Remaining work
        if project.get('remaining'):
            with st.expander("Remaining Work"):
                for r in project['remaining']:
                    st.markdown(f"- {r}")

        # Links
        links = []
        if project.get('github_url'):
            links.append(f"[GitHub]({project['github_url']})")
        if project.get('live_url'):
            links.append(f"[Live App]({project['live_url']})")
        if project.get('deployment') and project['deployment'] != 'N/A':
            links.append(f"Deployment: {project['deployment']}")
        if links:
            st.markdown(" | ".join(links))


def render_project_card_mini(project: dict):
    """Render a compact project card for the home page grid."""
    status = project['status']
    color = STATUS_COLORS.get(status, '#6e84a3')
    dot = STATUS_DOTS.get(status, 'gray')
    label = STATUS_LABELS.get(status, status)
    pct = project.get('completion', 0)

    with st.container(border=True):
        st.markdown(f"**{project['name']}**")
        st.caption(project.get('tagline', ''))

        if pct > 0:
            _completion_bar(pct, color)
        st.markdown(f"{STATUS_EMOJI[status]} {label}")

        if project.get('tech_stack'):
            tags = " ".join([f"`{t}`" for t in project['tech_stack'][:4]])
            st.markdown(tags)


def render_trading_card_mini(strategy: dict):
    """Render a compact trading system card for the home page grid."""
    status = strategy['status']
    dot = STATUS_DOTS.get(status, 'gray')
    label = STATUS_LABELS.get(status, status)

    with st.container(border=True):
        st.markdown(f"**{strategy['name']}**")
        instruments = ', '.join(strategy.get('instruments', []))
        st.caption(f"{strategy.get('version', '')} | {instruments}")
        st.markdown(f"{STATUS_EMOJI[status]} {label}")

        if strategy.get('tech_stack'):
            tags = " ".join([f"`{t}`" for t in strategy['tech_stack'][:4]])
            st.markdown(tags)
