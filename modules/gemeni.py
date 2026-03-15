
import google.generativeai as genai
from PIL import Image
import streamlit as st
import json

# ---- Gemini AI ----
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
gemini = genai.GenerativeModel("gemini-2.5-flash")

# Load detection guide
with open("guide/detection-guide.md", "r") as f:
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