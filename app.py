"""
Late Blight Detection App
Run with: streamlit run app.py
"""
import streamlit as st

# ---- Page Config (must be first Streamlit command) ----
st.set_page_config(
    page_title="Late Blight Detector",
    page_icon="🌿",
    layout="wide",
)

from modules.ui_detect import render_detect_round1_tab
from modules.ui_round2_detect import render_detect_round2_tab
from modules.ui_gallery import render_gallery_tab
from modules.ui_round1 import render_round1_tab

# ---- Session State ----
if "patches" not in st.session_state:
    st.session_state.patches = None
if "results" not in st.session_state:
    st.session_state.results = None
if "detect_mode" not in st.session_state:
    st.session_state.detect_mode = "model"

# ---- Title ----
st.title("🌿 Late Blight Detector")
st.markdown("Upload a drone photo → slice into patches → detect disease")

# ---- Tabs ----

# ---- Sidebar navigation ----
page = st.sidebar.radio(
    "📋 Pages",
    [
        "🔍 Round 1 Detection",
        "🔍 Round 2 Detection",
        "🖼️ Gallery",
        "📊 Round 1 Report",
        "🔮 Round 2 Report",
    ],
)
st.sidebar.markdown("---")

# ---- Route to page ----
if page == "🔍 Round 1 Detection":
    render_detect_round1_tab()        # writes its own sidebar widgets below navigation

elif page == "🔍 Round 2 Detection":
    render_detect_round2_tab()

elif page == "🖼️ Gallery":
    render_gallery_tab()

elif page == "📊 Round 1 Report":
    render_round1_tab()

elif page == "🔮 Round 2 Report":
    st.header("🔮 Round 2 — Coming Soon")