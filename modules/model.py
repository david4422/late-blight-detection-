
import tensorflow as tf
import streamlit as st
import numpy as np

# ---- Model ----
@st.cache_resource
def load_model():
    return tf.keras.models.load_model("model/late_blight_model.h5")

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
