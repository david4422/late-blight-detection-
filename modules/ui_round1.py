"""
Round 1 tab — shows summaries with images
"""
import streamlit as st
import re
import os

SUMMARY_DIR = "summerys"

def render_markdown_with_images(md_text, image_base_dir):
    """Render markdown, replacing <img src> tags with st.image()"""
    # Split by img tags
    parts = re.split(r'(<img[^>]+>)', md_text)

    for part in parts:
        if part.startswith('<img'):
            # Extract src and width
            src_match = re.search(r'src="([^"]+)"', part)
            width_match = re.search(r'width="(\d+)"', part)

            if src_match:
                src = src_match.group(1)
                width = int(width_match.group(1)) if width_match else 600

                # Build full path
                img_path = os.path.join(image_base_dir, src)

                if os.path.exists(img_path):
                    st.image(img_path, width=width)
                else:
                    st.warning(f"Image not found: {img_path}")
        else:
            if part.strip():
                st.markdown(part)

def render_round1_tab():
    st.header("📊 Round 1 — Research Results")

    # Sub-tabs for each summary
    sub1, sub2, sub3, sub4, sub5 = st.tabs([
        "🌍 Overview",
        "🔬 Image Analysis ",
        "⚖️ Method Comparison ",
        "📝 Learning Log",
        "🔍 Detection Guide"
    ])

    with sub1:
        with open(f"{SUMMARY_DIR}/round-1-overview.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())

    with sub2:
        with open(f"{SUMMARY_DIR}/image-analysis-summary.md ", "r", encoding="utf-8") as f:
            md = f.read()
        render_markdown_with_images(md, SUMMARY_DIR)

    with sub3:
        with open(f"{SUMMARY_DIR}/method-comparison-summary.md ", "r", encoding="utf-8") as f:
            md = f.read()
        render_markdown_with_images(md, SUMMARY_DIR)

    with sub4:
        with open(f"{SUMMARY_DIR}/learning-log.md", "r", encoding="utf-8") as f:
            st.markdown(f.read())

    with sub5:
        with open("guide/detection-guide.md", "r") as f:
            guide_text = f.read()
            st.markdown(guide_text)