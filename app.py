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

tab_detect_round1, tab_detect_round2, tab_gallery, tab_round1, tab_round2 = st.tabs([
    "🔍 Detection roun1"," 🔍 Detection roun2", "🖼️ Gallery", "📊 Round 1", "🔮 Round 2"
])

with tab_detect_round1:
    render_detect_round1_tab()

with tab_detect_round2:
    st.header("🔮 Round 2 — Coming Soon")
    st.markdown("Round 2 will include: YOLO model, Guide v2, expert labels, and real healthy training data.")

with tab_gallery:
    render_gallery_tab()

with tab_round1:
    render_round1_tab()

with tab_round2:
    st.header("🔮 Round 2 — Coming Soon")
    st.markdown("Round 2 will include: YOLO model, Guide v2, expert labels, and real healthy training data.")
