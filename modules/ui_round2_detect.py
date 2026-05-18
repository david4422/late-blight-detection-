
"""Round 2 Detection — supports 3 models: YOLO unified, YOLO 2-class, CNN-R2."""
import streamlit as st
from PIL import Image, ImageDraw
from modules.slicing import slice_image
from modules.yolo_detect import predict_patch_yolo
from modules.cnn_r2_detect import predict_patch_cnn_r2

CLS_COLOR = {
    'Disease':     '#a78bfa',
    'Late blight': '#3fb950',
    'Abnormality': '#f0883e',
}

# Model registry — each entry tells the UI everything it needs
MODELS = {
    "YOLO Unified (1 class)": {
        "kind":  "yolo",
        "name":  "unified",
        "patch": 640,
        "desc":  "YOLOv8s on confirmed boxes. Detects 'Disease' regions. mAP@50=0.417",
    },
    "YOLO 2-class": {
        "kind":  "yolo",
        "name":  "2class",
        "patch": 640,
        "desc":  "YOLOv8s separating Late blight from Abnormality. mAP@50=0.386",
    },
    "CNN-R2 (MobileNetV2)": {
        "kind":  "cnn",
        "name":  "r2",
        "patch": 224,
        "desc":  "MobileNetV2 classifier on Round 2 data — Sick or Healthy per patch",
    },
}


def render_detect_round2_tab():
    # ─── Sidebar ───
    st.sidebar.header("Round 2 — Pick Model")
    model_key = st.sidebar.radio("Model:", list(MODELS.keys()), index=0)
    cfg = MODELS[model_key]

    conf = st.sidebar.slider("Confidence threshold", 0.05, 0.95, 0.25, 0.05)

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{model_key}**")
    st.sidebar.caption(cfg["desc"])
    st.sidebar.caption(f"Patch size: **{cfg['patch']}×{cfg['patch']}**")

    # ─── Upload ───
    uploaded = st.file_uploader(
        "Drag & drop a drone image here",
        type=["jpg", "jpeg", "png"],
        key="r2_upload",
    )
    if not uploaded:
        st.info("Upload a drone photo (any resolution).")
        return

    image = Image.open(uploaded).convert("RGB")
    w, h = image.size
    col_img, _ = st.columns([1, 1])
    with col_img:
        st.image(image, caption=f"Uploaded: {w} × {h} px", use_container_width=True)

    p = cfg["patch"]
    cols_count = -(-w // p)
    rows_count = -(-h // p)
    st.markdown(f"**{cols_count} × {rows_count} = {cols_count * rows_count} patches** at {p}×{p}")

    # ─── Slice ───
    if st.button("✂️ Slice into Patches", type="primary", key="r2_slice_btn"):
        patches, _, _ = slice_image(image, p, p)
        st.session_state.r2_patches = patches
        st.session_state.r2_results = None

    patches = st.session_state.get("r2_patches")
    if not patches:
        return
    st.success(f"Done! {len(patches)} patches created")

    # Patch carousel with pagination
    st.markdown("### All Patches")
    total = len(patches)
    if total > 5:
        cprev, cslide, cnext = st.columns([1, 8, 1])
        with cprev:
            if st.button("◀", key="r2_prev_p"):
                st.session_state.r2_p_start = max(st.session_state.get("r2_p_start", 0) - 5, 0)
        with cnext:
            if st.button("▶", key="r2_next_p"):
                st.session_state.r2_p_start = min(st.session_state.get("r2_p_start", 0) + 5, max(total - 5, 0))
        with cslide:
            start = st.slider("Navigate patches", 0, max(total - 5, 0),
                                st.session_state.get("r2_p_start", 0), step=5)
            st.session_state.r2_p_start = start
    else:
        start = 0

    pcols = st.columns(5)
    for i, c in enumerate(pcols):
        idx = start + i
        if idx < total:
            with c:
                st.image(patches[idx]["image"], use_container_width=True)
                st.caption(f"#{idx + 1} ({patches[idx]['col']},{patches[idx]['row']})")

    # ─── Detect ───
    if st.button("🔍 Detect", type="primary", key="r2_detect_btn"):
        results = []
        bar = st.progress(0)
        for i, pt in enumerate(patches):
            if cfg["kind"] == "yolo":
                boxes = predict_patch_yolo(pt["image"], model_name=cfg["name"], conf=conf)
                results.append({"patch": pt, "boxes": boxes})
            else:
                label, c = predict_patch_cnn_r2(pt["image"], conf=conf)
                results.append({"patch": pt, "label": label, "confidence": c})
            bar.progress((i + 1) / len(patches))
        st.session_state.r2_results = results
        st.session_state.r2_kind = cfg["kind"]

    # ─── Results ───
    results = st.session_state.get("r2_results")
    if not results:
        return
    kind = st.session_state.r2_kind

    st.markdown("### Results")

    # Optional filter for YOLO — show only patches with detections
    if kind == "yolo":
        show_filter = st.radio("Show:", ["All patches", "Only with boxes"],
                                horizontal=True, key="r2_filter")
        if show_filter == "Only with boxes":
            filtered = [(i, r) for i, r in enumerate(results) if len(r["boxes"]) > 0]
        else:
            filtered = list(enumerate(results))
    else:
        show_filter = st.radio("Show:", ["All", "Sick", "Healthy"],
                                horizontal=True, key="r2_filter")
        if show_filter == "All":
            filtered = list(enumerate(results))
        else:
            filtered = [(i, r) for i, r in enumerate(results) if r["label"] == show_filter]

    total_f = len(filtered)
    st.markdown(f"Showing **{total_f}** patches")

    # Pagination for results
    if total_f > 5:
        cprev, cslide, cnext = st.columns([1, 8, 1])
        with cprev:
            if st.button("◀", key="r2_prev_r"):
                st.session_state.r2_r_start = max(st.session_state.get("r2_r_start", 0) - 5, 0)
        with cnext:
            if st.button("▶", key="r2_next_r"):
                st.session_state.r2_r_start = min(st.session_state.get("r2_r_start", 0) + 5, max(total_f - 5, 0))
        with cslide:
            rstart = st.slider("Navigate results", 0, max(total_f - 5, 0),
                                st.session_state.get("r2_r_start", 0), step=5)
            st.session_state.r2_r_start = rstart
    else:
        rstart = 0

    rcols = st.columns(5)
    for j, c in enumerate(rcols):
        ridx = rstart + j
        if ridx < total_f:
            i, r = filtered[ridx]
            with c:
                if kind == "yolo":
                    annotated = r["patch"]["image"].copy()
                    draw = ImageDraw.Draw(annotated)
                    for b in r["boxes"]:
                        color = CLS_COLOR.get(b["cls"], "#888")
                        draw.rectangle([b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]],
                                        outline=color, width=3)
                        draw.text((b["x"] + 2, b["y"] + 2), f"{b['cls']} {b['conf']:.0%}", fill=color)
                    st.image(annotated, use_container_width=True)
                    st.caption(f"#{i+1} — {len(r['boxes'])} boxes")
                else:
                    st.image(r["patch"]["image"], use_container_width=True)
                    color = "#f85149" if r["label"] == "Sick" else "#3fb950"
                    st.markdown(
                        f'<span style="color:{color};font-weight:bold;">{r["label"]} ({r["confidence"]:.0%})</span>',
                        unsafe_allow_html=True,
                    )
                    st.caption(f"#{i+1}")