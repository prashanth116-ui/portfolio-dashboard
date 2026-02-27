"""Strategy card rendering helpers."""
import streamlit as st


STATUS_COLORS = {
    'ACTIVE': '#00d97e',
    'DEPRECATED': '#6e84a3',
    'EXPERIMENTAL': '#f6c343',
}

STATUS_EMOJI_MAP = {
    'ACTIVE': 'green',
    'DEPRECATED': 'gray',
    'EXPERIMENTAL': 'orange',
}


def render_strategy_card(strategy: dict):
    """Render a single strategy card with expandable details."""
    status = strategy['status']
    color = STATUS_COLORS.get(status, '#6e84a3')
    status_dot = f":{STATUS_EMOJI_MAP.get(status, 'gray')}_circle:"

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### {strategy['name']}")
            st.caption(f"{strategy.get('version', '')} | {', '.join(strategy.get('instruments', []))}")
        with col2:
            st.markdown(f"{status_dot} **{status}**")

        st.markdown(strategy['description'])

        if strategy.get('tech_stack'):
            tags = " ".join([f"`{t}`" for t in strategy['tech_stack']])
            st.markdown(tags)

        # Expandable details for active strategy
        if strategy.get('entry_types'):
            with st.expander("Entry Types"):
                for et in strategy['entry_types']:
                    st.markdown(f"**Type {et['type']}: {et['name']}** - {et['description']}")

        if strategy.get('exit_structure'):
            with st.expander("Exit Structure"):
                es = strategy['exit_structure']
                st.markdown(f"- **T1**: {es['t1']}")
                st.markdown(f"- **T2**: {es['t2']}")
                st.markdown(f"- **Runner**: {es['runner']}")

        if strategy.get('filters'):
            with st.expander("Filter Pipeline"):
                mandatory = strategy['filters'][:2]
                optional = strategy['filters'][2:]
                st.markdown("**Mandatory (must pass):**")
                for f in mandatory:
                    st.markdown(f"- {f}")
                st.markdown("**Optional (2 of 3 must pass):**")
                for f in optional:
                    st.markdown(f"- {f}")
