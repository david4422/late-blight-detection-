from modules.model import predict_patches
from modules.gemeni import classify_all_patches_ai


def run_detection(patches, use_model, use_guide):
    """Run detection using the selected method(s). Returns (results, mode)."""
    if use_model and not use_guide:
        results = predict_patches(patches)
        return results, "model"

    elif use_guide and not use_model:
        results = classify_all_patches_ai(patches)
        return results, "guide"

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
        return combined, "combo"

    return [], "none"
