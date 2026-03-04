"""Page 1: Software Projects — detailed project cards."""
import json
from pathlib import Path

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.project_cards import render_project_card
from components.responsive import inject_responsive_css

st.set_page_config(page_title="Software Projects", page_icon="💻", layout="wide")
inject_responsive_css()

st.markdown("# Software Projects")


@st.cache_data
def _load_projects():
    data_path = Path(__file__).parent.parent / 'data' / 'projects_metadata.json'
    with open(data_path) as f:
        return json.load(f)


_projects = _load_projects()

_status_counts = {}
for p in _projects:
    s = p['status']
    _status_counts[s] = _status_counts.get(s, 0) + 1

st.markdown(
    f"{len(_projects)} projects spanning cloud infrastructure, SaaS, AI tools, "
    "real estate, and market research."
)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Active / Complete", _status_counts.get('COMPLETE', 0) + _status_counts.get('ACTIVE', 0))
with col2:
    st.metric("In Progress", _status_counts.get('IN_PROGRESS', 0))
with col3:
    st.metric("Research", _status_counts.get('RESEARCH', 0))
with col4:
    st.metric("Total", len(_projects))

st.markdown("---")

# Group projects by status category
_STATUS_GROUPS = [
    ("Active / Complete", ("ACTIVE", "COMPLETE")),
    ("In Progress", ("IN_PROGRESS",)),
    ("Research", ("RESEARCH",)),
    ("Archived", ("ARCHIVED",)),
]

for group_label, statuses in _STATUS_GROUPS:
    group = [p for p in _projects if p['status'] in statuses]
    if not group:
        continue
    st.markdown(f"### {group_label} ({len(group)})")
    for project in group:
        render_project_card(project)
