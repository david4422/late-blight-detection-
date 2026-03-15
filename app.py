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

from modules.ui_detect import render_detect_tab
from modules.ui_gallery import render_gallery_tab

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
tab_detect, tab_guide, tab_gallery = st.tabs(["🔍 Detection", "📖 Guide", "🖼️ Gallery"])

with tab_detect:
    render_detect_tab()

with tab_guide:
    st.header("Detection Guide")
    with open("guide/detection-guide.md", "r") as f:
        guide_text = f.read()
        st.markdown(guide_text)

with tab_gallery:
    render_gallery_tab()
