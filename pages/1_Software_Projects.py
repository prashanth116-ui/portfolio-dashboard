"""Page 1: Software Projects — 4 detailed project cards."""
import json
from pathlib import Path

import streamlit as st

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from components.project_cards import render_project_card

st.set_page_config(page_title="Software Projects", page_icon="💻", layout="wide")

st.markdown("# Software Projects")
st.markdown(
    "4 projects spanning cloud infrastructure, SaaS, mobile, and market research."
)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Complete", "1")
with col2:
    st.metric("In Progress", "2")
with col3:
    st.metric("Research", "1")
with col4:
    st.metric("Tech Stacks", "4")

st.markdown("---")


@st.cache_data
def load_projects():
    data_path = Path(__file__).parent.parent / 'data' / 'projects_metadata.json'
    with open(data_path) as f:
        return json.load(f)


projects = load_projects()

for project in projects:
    render_project_card(project)
