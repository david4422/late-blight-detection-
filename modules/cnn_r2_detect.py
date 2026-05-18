"""CNN-R2 (MobileNetV2 on Round 2 data) inference per patch."""
from pathlib import Path
from PIL import Image
import numpy as np
import streamlit as st

_model = None

def _load():
    global _model
    if _model is not None:
        return _model
    import tensorflow as tf
    path = Path(__file__).parent.parent / 'model' / 'cnn_r2.keras'
    if not path.exists():
        st.error(f"❌ Model not found: {path.name}. Train CNN-R2 first.")
        return None
    _model = tf.keras.models.load_model(str(path))
    return _model

def predict_patch_cnn_r2(image: Image.Image, conf: float = 0.5):
    """Returns (label, confidence). label in {'Sick', 'Healthy', 'Error'}."""
    model = _load()
    if model is None:
        return "Error", 0.0
    img = image.resize((224, 224))
    arr = np.array(img).astype(np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)
    pred = float(model.predict(arr, verbose=0)[0][0])
    label = "Sick" if pred > conf else "Healthy"
    conf = pred if label == "Sick" else 1 - pred
    return label, conf