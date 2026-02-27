"""Responsive CSS injection for mobile compatibility."""
import streamlit as st


def inject_responsive_css():
    """Inject CSS media queries to make Streamlit layouts mobile-friendly.

    Call once per page, after st.set_page_config().
    """
    st.markdown("""
    <style>
    /* Mobile: stack columns vertically */
    @media (max-width: 768px) {
        /* Force column containers to wrap vertically */
        div[data-testid="stHorizontalBlock"] {
            flex-wrap: wrap !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }

        /* Add spacing between stacked metric cards */
        div[data-testid="stMetric"] {
            margin-bottom: 0.25rem;
        }

        /* Reduce chart padding on mobile */
        div[data-testid="stPlotlyChart"] > div {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* Prevent metric value overflow */
        div[data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
            overflow-wrap: break-word;
        }

        /* Tighten main block padding */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        /* Sidebar auto-collapse hint */
        section[data-testid="stSidebar"] {
            min-width: 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
