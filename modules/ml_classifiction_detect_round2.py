from modules.model import predict_patches_load_model
import streamlit as st
from PIL import Image
from modules.slicing import slice_image
from modules.detection import run_detection
import csv
import io

patch_size = (128, 128)
model_path = 'model/new_model_85.keras'

def render_detect_round2_ml_tab():
    """Render the detection tab UI."""
    # ---- Sidebar ----
    st.sidebar.header("Detection Method")
    use_model = st.sidebar.checkbox("🤖 ML Model (fast)", value=True)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**ML Model**: {patch_size} patches → Sick/Healthy")

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
            st.image(image, caption=f"Uploaded: {w} × {h} pixels", use_container_width=True)

        # Patch size depends on method
        patch_w, patch_h = patch_size[0], patch_size[1]
        st.info(f"🤖 ML Model selected — slicing into **{patch_size}** patches")
    
        cols_count = -(-w // patch_w)
        rows_count = -(-h // patch_h)
        total_patches = cols_count * rows_count

        st.markdown(f"**{cols_count} × {rows_count} = {total_patches} patches**")

        # Slice button
        if st.button("✂️ Slice into Patches", type="primary"):
            patches, cols_count, rows_count = slice_image(image, patch_w, patch_h)
            st.session_state.patches = patches

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
                        st.session_state.patch_start = min(st.session_state.get("patch_start", 0) + 5, max(total - 5, 0))
                with col_slider:
                    start = st.slider("Navigate patches", 0, max(total - 5, 0), st.session_state.get("patch_start", 0), step=5)
                    st.session_state.patch_start = start
            else:
                start = 0

            carousel_cols = st.columns(5)
            for i, col in enumerate(carousel_cols):
                idx = start + i
                if idx < total:
                    with col:
                        st.image(patches[idx]["image"], use_container_width=True)
                        st.caption(f"#{idx + 1} ({patches[idx]['col']},{patches[idx]['row']})")

            # Detect button
            if st.button("🔍 Detect Disease", type="primary"):
                results = predict_patches_load_model(path=model_path, patches=patches, patch_size=patch_size)
                st.session_state.results = results

            # Show results
            if st.session_state.results:
                results = st.session_state.results

                sick_count = sum(1 for r in results if r["label"] == "Sick")
                healthy_count = sum(1 for r in results if r["label"] == "Healthy")
                st.success(f"**{sick_count} Sick** / **{healthy_count} Healthy** out of {len(results)} patches")

                # Filter buttons
                filter_label = st.radio("Show:", ["All", "Sick", "Healthy"], horizontal=True)
                if filter_label == "All":
                    filtered = list(enumerate(results))
                else:
                    filtered = [(i, r) for i, r in enumerate(results) if r["label"] == filter_label]

                st.markdown(f"### Showing {len(filtered)} patches")

                # Carousel for filtered results
                total_filtered = len(filtered)
                if total_filtered > 5:
                    col_prev3, col_slider3, col_next3 = st.columns([1, 8, 1])
                    with col_prev3:
                        if st.button("◀", key="prev_filtered"):
                            st.session_state.filtered_start = max(st.session_state.get("filtered_start", 0) - 5, 0)
                    with col_next3:
                        if st.button("▶", key="next_filtered"):
                            st.session_state.filtered_start = min(st.session_state.get("filtered_start", 0) + 5, max(total_filtered - 5, 0))
                    with col_slider3:
                        fstart = st.slider("Navigate results", 0, max(total_filtered - 5, 0), st.session_state.get("filtered_start", 0), step=5, key="filtered_slider")
                        st.session_state.filtered_start = fstart
                else:
                    fstart = 0

                carousel_cols3 = st.columns(5)
                for j, col in enumerate(carousel_cols3):
                    fidx = fstart + j
                    if fidx < total_filtered:
                        idx, r = filtered[fidx]
                        with col:
                            st.image(patches[idx]["image"], use_container_width=True)
                            color = "#f85149" if r["label"] == "Sick" else "#3fb950"
                            st.markdown(f'<span style="color:{color}; font-weight:bold;">{r["label"]} ({r["confidence"]:.0%})</span>', unsafe_allow_html=True)

                            st.caption(f"#{idx + 1} ({r['col']},{r['row']})")
                # Download CSV button
                csv_buffer = io.StringIO()
                writer = csv.writer(csv_buffer)

                writer.writerow(["image_name", "patch_id", "col", "row", "x", "y", "label", "confidence"])
                for i, r in enumerate(results):
                    writer.writerow([uploaded.name, i+1, r["col"], r["row"], r["x"], r["y"], r["label"], f'{r["confidence"]:.4f}'])
               
                st.download_button(
                    label="📥 Download Results CSV",
                    data=csv_buffer.getvalue(),
                    file_name=f"{uploaded.name.rsplit('.', 1)[0]}_ml_classification_results.csv",
                    mime="text/csv"
                )

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
            st.markdown(f"Auto-cut into {patch_size} patches")
        with col3:
            st.markdown("**3. Detect**")   
            st.markdown("ML model → Sick / Healthy")