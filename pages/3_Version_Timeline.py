"""Page 3: Version Timeline — V6 to V10.15 evolution."""
import json
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Version Timeline", page_icon="📅", layout="wide")

st.markdown("# Version Timeline")
st.markdown("Strategy evolution from V6 through V10.15 — 17 versions over 5 months.")
st.markdown("---")

@st.cache_data
def load_versions():
    data_path = Path(__file__).parent.parent / 'data' / 'version_history.json'
    with open(data_path) as f:
        return json.load(f)

versions = load_versions()

# Category filter
categories = sorted(set(v['category'] for v in versions))
category_labels = {
    'feature': 'New Feature',
    'performance': 'Performance',
    'risk': 'Risk Management',
    'filter': 'Filter/Signal',
    'bugfix': 'Bug Fix',
}

selected_categories = st.sidebar.multiselect(
    "Filter by category",
    options=categories,
    default=categories,
    format_func=lambda x: category_labels.get(x, x.title()),
)

filtered = [v for v in versions if v['category'] in selected_categories]

CATEGORY_COLORS = {
    'feature': '🟦',
    'performance': '🟩',
    'risk': '🟧',
    'filter': '🟨',
    'bugfix': '🟥',
}

# Render timeline (newest first)
for version in reversed(filtered):
    cat_icon = CATEGORY_COLORS.get(version['category'], '⬜')
    cat_label = category_labels.get(version['category'], version['category'])

    with st.container(border=True):
        col1, col2, col3 = st.columns([1, 3, 2])

        with col1:
            st.markdown(f"### {version['version']}")
            st.caption(version['date'])

        with col2:
            st.markdown(f"**{version['title']}**")
            st.markdown(f"{cat_icon} {cat_label}")

        with col3:
            st.caption("Impact")
            st.markdown(f"*{version['impact']}*")

        # Expandable description + A/B test
        with st.expander("Details"):
            st.markdown(version['description'])

            if version.get('ab_test'):
                ab = version['ab_test']
                st.markdown("---")
                st.markdown("**A/B Test Results:**")
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Test Period", f"{ab['days']} days")
                with cols[1]:
                    if 'baseline_pl' in ab:
                        st.metric("Baseline P/L", ab['baseline_pl'])
                with cols[2]:
                    st.metric("Improvement", ab['improvement'])

                if 'wr_old' in ab and 'wr_new' in ab:
                    st.markdown(f"Win rate: {ab['wr_old']} → **{ab['wr_new']}**")
