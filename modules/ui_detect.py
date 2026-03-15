import streamlit as st
from PIL import Image
from modules.slicing import slice_image
from modules.detection import run_detection


def render_detect_tab():
    """Render the detection tab UI."""
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
                        st.image(patches[idx]["image"], use_column_width=True)
                        st.caption(f"#{idx + 1} ({patches[idx]['col']},{patches[idx]['row']})")

            # Detect button
            if st.button("🔍 Detect Disease", type="primary"):
                results, mode = run_detection(patches, use_model, use_guide)
                st.session_state.results = results
                st.session_state.detect_mode = mode

            # Show results
            if st.session_state.results:
                results = st.session_state.results
                mode = st.session_state.get("detect_mode", "model")

                if mode == "model":
                    sick_count = sum(1 for r in results if r["label"] == "Sick")
                    healthy_count = sum(1 for r in results if r["label"] == "Healthy")
                    st.success(f"**{sick_count} Sick** / **{healthy_count} Healthy** out of {len(results)} patches")

                    # Filter buttons
                    filter_label = st.radio("Show:", ["All", "Sick", "Healthy"], horizontal=True)
                    if filter_label == "All":
                        filtered = list(enumerate(results))
                    else:
                        filtered = [(i, r) for i, r in enumerate(results) if r["label"] == filter_label]

                else:
                    for sev in ["Clean", "Early", "Mid", "Late", "Healthy"]:
                        count = sum(1 for r in results if r.get("severity") == sev)
                        if count > 0:
                            st.write(f"**{sev}**: {count}")

                    # Filter buttons
                    available = ["All"] + [s for s in ["Clean", "Early", "Mid", "Late", "Healthy"] if any(r.get("severity") == s for r in results)]
                    filter_label = st.radio("Show:", available, horizontal=True)
                    if filter_label == "All":
                        filtered = list(enumerate(results))
                    else:
                        filtered = [(i, r) for i, r in enumerate(results) if r.get("severity") == filter_label]

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
                            st.image(patches[idx]["image"], use_column_width=True)
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
