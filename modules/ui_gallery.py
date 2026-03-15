import streamlit as st
from PIL import Image


def render_gallery_tab():
    """Render the disease gallery tab with educational images and descriptions."""

    st.header("Late Blight Disease Gallery")
    st.markdown(
        "Visual reference for identifying late blight (*Phytophthora infestans*) "
        "at different stages of infection."
    )

    # ---- Stage definitions ----
    stages = [
        {
            "title": "Early Stage — Initial Infection",
            "color": "#f0e040",
            "description": (
                "Small, irregular water-soaked spots appear on leaves, usually starting "
                "at the tips or edges. Spots are pale green to dark green and may look "
                "oily or wet. Lesions are small (< 15% of leaf area). "
                "At this stage the plant can still recover if treated quickly."
            ),
            "what_to_look_for": [
                "Small water-soaked spots on leaf tips or edges",
                "Pale green to dark green discoloration",
                "Oily or wet appearance on the leaf surface",
                "Lesions cover less than 15% of the leaf",
            ],
            "images": [
                {
                    "file": "images/early_leaf_spots.jpg",
                    "caption": "Early water-soaked spots on a potato leaf (NDSU)",
                },
            ],
        },
        {
            "title": "Mid Stage — Expanding Lesions",
            "color": "#f0883e",
            "description": (
                "Lesions grow larger and turn dark brown or black. A yellow (chlorotic) "
                "halo often forms around the lesion. The affected area covers 15-50% of "
                "the leaf. Multiple lesions may merge together. The disease is spreading "
                "and treatment becomes urgent."
            ),
            "what_to_look_for": [
                "Dark brown or black expanding lesions",
                "Yellow halo (chlorosis) around lesion edges",
                "Lesions covering 15-50% of the leaf",
                "Multiple lesions merging together",
            ],
            "images": [
                {
                    "file": "images/mid_dark_lesions.jpg",
                    "caption": "Dark brown/black expanding lesions (NDSU)",
                },
                {
                    "file": "images/mid_yellow_halo.jpg",
                    "caption": "Lesion with yellow chlorotic halo (NDSU)",
                },
            ],
        },
        {
            "title": "Late Stage — Severe Infection",
            "color": "#f85149",
            "description": (
                "More than 50% of the leaf is destroyed. Lesions are large, dark, and "
                "papery. Stems and petioles show brown-black streaks. The plant is "
                "severely damaged and yield loss is significant. Nearby plants are "
                "likely already infected."
            ),
            "what_to_look_for": [
                "Large dark papery lesions covering most of the leaf",
                "Brown-black streaks on stems and petioles",
                "Leaves curling, wilting, or falling off",
                "More than 50% tissue destruction",
            ],
            "images": [
                {
                    "file": "images/late_leaf_lesion.png",
                    "caption": "Severe brown papery leaf lesion (UW Extension)",
                },
                {
                    "file": "images/late_stem_lesions.jpg",
                    "caption": "Dark lesions on stems and petioles (NDSU)",
                },
            ],
        },
        {
            "title": "Sporulation — Active Pathogen Spread",
            "color": "#a78bfa",
            "description": (
                "White to gray fuzzy growth appears on the underside of leaves or at "
                "lesion margins. This is the pathogen producing spores (sporangia) that "
                "spread to other plants through wind and rain. Sporulation means the "
                "disease is actively spreading and conditions are favorable for infection."
            ),
            "what_to_look_for": [
                "White or gray fuzzy mildew on leaf undersides",
                "Cottony growth at the edges of lesions",
                "Most visible in humid or wet conditions",
                "Sign that spores are actively spreading to other plants",
            ],
            "images": [
                {
                    "file": "images/sporulation.jpg",
                    "caption": "White mildew sporulation at lesion margins (NDSU)",
                },
                {
                    "file": "images/sporulation_underside.png",
                    "caption": "White fuzzy sporulation on leaf underside (UW Extension)",
                },
            ],
        },
    ]

    # ---- Render each stage ----
    for stage in stages:
        st.markdown("---")
        st.subheader(stage["title"])
        st.markdown(
            f'<div style="border-left: 4px solid {stage["color"]}; '
            f'padding-left: 12px; margin-bottom: 12px;">'
            f'{stage["description"]}</div>',
            unsafe_allow_html=True,
        )

        # What to look for
        st.markdown("**What to look for:**")
        for item in stage["what_to_look_for"]:
            st.markdown(f"- {item}")

        # Images side by side
        img_cols = st.columns(len(stage["images"]))
        for i, img_info in enumerate(stage["images"]):
            with img_cols[i]:
                try:
                    img = Image.open(img_info["file"])
                    st.image(img, caption=img_info["caption"], use_column_width=True)
                except FileNotFoundError:
                    st.warning(f"Image not found: {img_info['file']}")

    # ---- Footer ----
    st.markdown("---")
    st.caption(
        "Images sourced from NDSU Extension and University of Wisconsin Extension. "
        "Used for educational and research purposes."
    )
