"""YOLO inference for Round 2 — load + predict on one patch."""
from pathlib import Path
from PIL import Image
import numpy as np
import streamlit as st

_cache = {}

def _load(model_name: str):
    if model_name in _cache:
        return _cache[model_name]
    from ultralytics import YOLO
    path = Path(__file__).parent.parent / 'model' / f'yolo_{model_name}.pt'
    if not path.exists():
        st.error(f"❌ Model not found: {path.name}. Download best.pt from Kaggle.")
        return None
    _cache[model_name] = YOLO(str(path))
    return _cache[model_name]


def predict_patch_yolo(image: Image.Image, model_name: str = 'unified', conf: float = 0.25):
    """Returns list of dicts: {x, y, w, h, cls, conf}."""
    model = _load(model_name)
    if model is None:
        return []
    results = model.predict(np.array(image), conf=conf, verbose=False)[0]
    out = []
    for box in results.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        out.append({
            'x': int(x1), 'y': int(y1),
            'w': int(x2 - x1), 'h': int(y2 - y1),
            'cls': model.names[int(box.cls[0])],
            'conf': float(box.conf[0]),
        })
    return out