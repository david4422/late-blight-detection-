"""
Ticket-011: Late Blight Detection App — Demo
Just a quick preview to see how Streamlit looks.
Run with: streamlit run app.py
"""
import streamlit as st
from PIL import Image

import tensorflow as tf
import numpy as np

import google.generativeai as genai
import base64
import json
import os

# ---- Page Config ----
st.set_page_config(
    page_title="Late Blight Detector",
    page_icon="🌿",
    layout="wide",
) 

# ---- Session State (storage box that survives re-runs) ----
if "patches" not in st.session_state:
    st.session_state.patches = None
if "results" not in st.session_state:
    st.session_state.results = None
if "detect_mode" not in st.session_state:
    st.session_state.detect_mode = "model"

# ---- Model ----
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("late_blight_model.h5")

model = load_model()
def predict_patches(patches):
    """Run ML model on all patches and return results."""
    results = []
    progress = st.progress(0)

    for i, p in enumerate(patches):
        img_array = np.array(p["image"].convert("RGB").resize((224, 224))) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = model.predict(img_array, verbose=0)[0][0]
        label = "Sick" if pred >= 0.5 else "Healthy"
        confidence = pred if pred >= 0.5 else 1 - pred

        results.append({
            "col": p["col"], "row": p["row"],
            "x": p["x"], "y": p["y"], 
            "label": label, "confidence": float(confidence),
        })

        progress.progress((i + 1) / len(patches))

    progress.empty() 
    return results 


# ---- Gemini AI ----
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini = genai.GenerativeModel("gemini-2.5-flash")

# Load detection guide
with open("detection-guide.md", "r") as f:
    detection_guide = f.read()

def classify_batch_with_ai(patch_list):
      """Send a batch of patches as a grid to Gemini with detection guide."""
      import io, time

      # Build grid image (5 columns)
      cols_per_row = 5
      rows_needed = -(-len(patch_list) // cols_per_row)
      pw, ph = 200, 150
      grid = Image.new("RGB", (cols_per_row * pw, rows_needed * ph), (0, 0, 0))

      for i, p in enumerate(patch_list):
          col = i % cols_per_row
          row = i // cols_per_row
          grid.paste(p["image"].convert("RGB").resize((pw, ph)), (col * pw, row * ph))

      # Convert grid to bytes
      buf = io.BytesIO()
      grid.save(buf, format="PNG")
      buf.seek(0)

      prompt = f"""You are a plant disease expert. Use this detection guide:

  {detection_guide}

  I'm sending you a grid image of {len(patch_list)} drone image patches arranged in {cols_per_row} columns.
  Patches are numbered left-to-right, top-to-bottom starting from 1.

  For EACH patch, analyze it and return a JSON array. Example for 3 patches:
  [
    {{"patch": 1, "severity": "Early", "confidence": 0.7, "sporulation": "No", "reasoning": "small brown
  spots"}},
    {{"patch": 2, "severity": "Clean", "confidence": 0.9, "sporulation": "No", "reasoning": "all green"}},
    {{"patch": 3, "severity": "Mid", "confidence": 0.8, "sporulation": "Yes", "reasoning": "white fuzz
  visible"}}
  ]

  Return ONLY the JSON array, nothing else. Exactly {len(patch_list)} entries."""

      response = gemini.generate_content([
          prompt,
          {"mime_type": "image/png", "data": buf.getvalue()}
      ])

      try:
          text = response.text.strip()
          if text.startswith("```"):
              text = text.split("\n", 1)[1].rsplit("```", 1)[0]
          return json.loads(text)
      except:
          return [{"patch": i+1, "severity": "Error", "confidence": 0, "sporulation": "No", "reasoning":
  "Failed"} for i in range(len(patch_list))]


def classify_all_patches_ai(patches):
    """Classify all patches using Gemini in batches of 20."""
    import time
    all_results = []
    batch_size = 20
    progress = st.progress(0)

    for batch_start in range(0, len(patches), batch_size):
        batch = patches[batch_start:batch_start + batch_size]
        batch_results = classify_batch_with_ai(batch)

        for i, r in enumerate(batch_results):
            idx = batch_start + i
            if idx < len(patches):
                all_results.append({
                    "col": patches[idx]["col"], "row": patches[idx]["row"],
                    "x": patches[idx]["x"], "y": patches[idx]["y"],
                    "severity": r.get("severity", "Error"),
                    "confidence": r.get("confidence", 0),
                    "sporulation": r.get("sporulation", "No"),
                    "reasoning": r.get("reasoning", ""),
                })

        progress.progress(min((batch_start + batch_size) / len(patches), 1.0))

        # Rate limit: wait between batches
        if batch_start + batch_size < len(patches):
            time.sleep(4)

    progress.empty()
    return all_results

# ---- Title ----
st.title("🌿 Late Blight Detector")
st.markdown("Upload a drone photo → slice into patches → detect disease")


# ---- Sidebar ----
st.sidebar.header("Detection Method")
use_model = st.sidebar.checkbox("🤖 ML Model (fast)", value=True)
use_guide = st.sidebar.checkbox("🧠 AI + Detection Guide (detailed)")

st.sidebar.markdown("---")
st.sidebar.markdown("**ML Model**: 224×224 patches → Sick/Healthy")
st.sidebar.markdown("**AI + Guide**: 200×150 patches → Early/Mid/Late")


# ---- Upload ----
uploaded = st.file_uploader(
    "Drag & drop a drone image here",
    type=["jpg", "jpeg", "png"],
)

if uploaded:
    image = Image.open(uploaded)
    w, h = image.size

    # Show uploaded image
    col_img, col_empty = st.columns([1, 1])
    with col_img:
        st.image(image, caption=f"Uploaded: {w} × {h} pixels", use_column_width=True)

    # Patch size depends on method
    if use_model:
        patch_w, patch_h = 224, 224
        st.info(f"🤖 ML Model selected — slicing into **224×224** patches")
    elif use_guide:
        patch_w, patch_h = 200, 150
        st.info(f"🧠 AI + Guide selected — slicing into **200×150** patches")
    else:
        st.warning("Select a detection method in the sidebar")
        st.stop()

    cols_count = -(-w // patch_w)
    rows_count = -(-h // patch_h)
    total_patches = cols_count * rows_count

    st.markdown(f"**{cols_count} × {rows_count} = {total_patches} patches**")


    # Slice button
    if st.button("✂️ Slice into Patches", type="primary" ):

        # Cut the image into patches
        patches = []
        for row in range(rows_count):
            for col in range(cols_count):
                x = min(col * patch_w, w - patch_w)
                y = min(row * patch_h, h - patch_h)
                patch = image.crop((x, y, x + patch_w, y + patch_h))
                patches.append({"image": patch, "row": row, "col": col, "x": x, "y": y})

        st.session_state.patches = patches  # <-- save to the box
        
    # Everything below reads from the box (survives re-runs)
    if st.session_state.patches:
        patches = st.session_state.patches
        st.success(f"Done! {len(patches)} patches created")

        # Patch carousel
        st.markdown("### All Patches")
        total = len(patches)
        if total > 5:
                col_prev, col_slider, col_next = st.columns([1, 8, 1])
                with col_prev:
                    if st.button("◀", key="prev_patch"):
                        st.session_state.patch_start = max(st.session_state.get("patch_start", 0) - 5, 0)
                with col_next:
                    if st.button("▶", key="next_patch"):
                        st.session_state.patch_start = min(st.session_state.get("patch_start", 0) + 5, max(total -5, 0))
                with col_slider:
                    start = st.slider("Navigate patches", 0, max(total - 5, 0),st.session_state.get("patch_start", 0), step=5)
                    st.session_state.patch_start = start
        else:
            start = 0

        carousel_cols = st.columns(5)
        for i, col in enumerate(carousel_cols):
            idx = start + i
            if idx < total:
                with col:
                    st.image(patches[idx]["image"], use_column_width=True)
                    st.caption(f"#{idx + 1} ({patches[idx]['col']},{patches[idx]['row']})")

        # Detect button — saves results to the box
        if st.button("🔍 Detect Disease", type="primary"):
            if use_model and not use_guide:
                st.session_state.results = predict_patches(patches)
                st.session_state.detect_mode = "model"
            elif use_guide and not use_model:
                st.session_state.results = classify_all_patches_ai(patches)
                st.session_state.detect_mode = "guide"
            elif use_model and use_guide:
                ml_results = predict_patches(patches)
                sick_patches = [patches[i] for i, r in enumerate(ml_results) if r["label"] == "Sick"]
                if sick_patches:
                    ai_results = classify_all_patches_ai(sick_patches)
                else:
                    ai_results = []
                combined = [] 
                sick_idx = 0
                for i, r in enumerate(ml_results):
                    if r["label"] == "Healthy":
                        combined.append({**r, "severity": "Healthy", "reasoning": "ML: Healthy"})
                    else:
                        if sick_idx < len(ai_results):
                            combined.append({**r, **ai_results[sick_idx]})
                            sick_idx += 1
                        else:
                            combined.append({**r, "severity": "Sick", "reasoning": "ML: Sick"})
                st.session_state.results = combined
                st.session_state.detect_mode = "combo"

        # Show results (survives re-runs)
        if st.session_state.results:
            results = st.session_state.results

            mode = st.session_state.get("detect_mode", "model")
            if mode == "model":
                sick_count = sum(1 for r in results if r["label"] == "Sick")
                healthy_count = sum(1 for r in results if r["label"] == "Healthy")
                st.success(f"**{sick_count} Sick** / **{healthy_count} Healthy** out of {len(results)} patches")
            else:
                for sev in ["Clean", "Early", "Mid", "Late", "Healthy"]:
                    count = sum(1 for r in results if r.get("severity") == sev)
                    if count > 0:
                        st.write(f"**{sev}**: {count}")

            # Severity carousel
            st.markdown("### Severity Map")

            if len(results) > 5:
                col_prev2, col_slider2, col_next2 = st.columns([1, 8, 1])
                with col_prev2:
                    if st.button("◀", key="prev_sev"):
                        st.session_state.sev_start = max(st.session_state.get("sev_start", 0) - 5, 0)
                with col_next2:
                    if st.button("▶", key="next_sev"):
                        st.session_state.sev_start = min(st.session_state.get("sev_start", 0) + 5,max(len(results) - 5, 0))
                with col_slider2:
                    start2 = st.slider("Navigate results", 0, max(len(results) - 5, 0),st.session_state.get("sev_start", 0), step=5, key="severity")
                    st.session_state.sev_start = start2
            else:
                start2 = 0

            carousel_cols2 = st.columns(5)
            for i, col in enumerate(carousel_cols2):
                idx = start2 + i
                if idx < len(results):
                    r = results[idx]
                    with col:
                        st.image(patches[idx]["image"], use_column_width=True)
                        mode = st.session_state.get("detect_mode", "model")
                        if mode == "model":
                            color = "#f85149" if r["label"] == "Sick" else "#3fb950"
                            st.markdown(f'<span style="color:{color}; font-weight:bold;">{r["label"]} ({r["confidence"]:.0%})</span>', unsafe_allow_html=True)
                        else:
                            colors = {"Clean": "#3fb950", "Healthy": "#3fb950", "Early": "#f0e040", "Mid": "#f0883e", "Late": "#f85149", "Error": "#888"}
                            sev = r.get("severity", "Error")
                            color = colors.get(sev, "#888")
                            conf = r.get("confidence", 0)
                            st.markdown(f'<span style="color:{color}; font-weight:bold;">{sev} ({conf:.0%})</span>', unsafe_allow_html=True)
                            if r.get("sporulation") == "Yes":
                                st.caption("🔬 Sporulation")
                            if r.get("reasoning"):
                                st.caption(f"💬 {r.get('reasoning')}")
                        st.caption(f"#{idx + 1} ({r['col']},{r['row']})")

else:
    # Empty state
    st.markdown("---")
    st.markdown("### How it works")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1. Upload**")
        st.markdown("Drag & drop any drone photo")
    with col2:
        st.markdown("**2. Slice**")
        if use_model:
            st.markdown("Auto-cut into 224×224 patches")
        elif use_guide:
            st.markdown("Auto-cut into 200×150 patches")
        else:
            st.markdown("Select a method in the sidebar")
    with col3:
        st.markdown("**3. Detect**")
        if use_model:
            st.markdown("ML model → Sick / Healthy")
        elif use_guide:
            st.markdown("AI + detection guide → Early / Mid / Late")
        else:
            st.markdown("ML model or AI with detection guide")
