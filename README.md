# Late Blight Detection App

A Streamlit web app that detects late blight disease in potato crops from drone images.

## How It Works

1. Upload a drone photo of a potato field
2. The app slices it into patches
3. Choose a detection method:
   - **ML Model** — Fast scan. Classifies each patch as Sick or Healthy using a trained CNN (MobileNetV2)
   - **AI + Detection Guide** — Detailed analysis. Sends patches to Gemini API with a detection guide for Early/Mid/Late severity classification
   - **Combo** — ML filters sick patches first, then AI classifies their severity

## Tech Stack

- **Streamlit** — UI and deployment
- **TensorFlow** — ML model inference
- **Gemini API** — AI-powered severity classification
- **Pillow** — Image slicing and processing

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Add your Gemini API key in `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-key-here"
```

## Live Demo

Coming soon — deploying to Streamlit Cloud.
