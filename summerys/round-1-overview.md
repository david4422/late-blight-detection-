# Round 1 Overview — Late Blight Detection Research

> **Project**: Precision Agriculture — Late Blight Detection from Drone Imagery
> **Goal**: Compare three detection methods and determine which approach works best
> **Dataset**: 5,187 patches from 15 drone images of potato fields
> **Date**: February–March 2026

---

## What Is This Project About?

Late blight (*Phytophthora infestans*) is the most destructive plant disease in the world, costing farmers $6.7 billion every year. It killed 1 million people during the Irish Potato Famine. The disease spreads fast — a healthy plant can die in just 5 days.

We're building a system to detect late blight from **drone images** of potato fields. Drones fly over fields and take high-resolution photos. Our system analyzes these photos, patch by patch, to find disease.

The research question: **What is the best way to detect late blight from drone imagery?** We tested three approaches in Round 1.

---

## The Three Methods

### Method 1: ML Model (MobileNetV2 — CNN)

A traditional deep learning approach. We trained a neural network to look at a small image patch (224×224 pixels) and decide: **Sick or Healthy?**

**How we built it:**
- **Architecture**: MobileNetV2 — a pre-trained CNN from Google, originally trained on 1.4 million images (ImageNet). It already knows how to see edges, shapes, colors, and textures. We froze the MobileNetV2 backbone (2.2 million parameters, not retrained) and added our own small classification head on top.
- **Our classifier head**: GlobalAveragePooling2D → Dense(128, ReLU) → Dropout(0.3) → Dense(1, sigmoid). Only ~165,000 trainable parameters.
- **Transfer learning**: We didn't train the whole network from scratch — impossible with just 1,000 images. Instead, MobileNetV2 extracts visual features (edges, textures, patterns), and our small head learns: "this feature pattern = sick, this pattern = healthy."
- **Training data**: 1,000 patches from drone images — 500 sick + 500 healthy. Sick patches were cropped at finding coordinates from a validated agricultural database. Healthy patches were cropped from the same drone images at random positions (verified as clean by Gemini + detection guide).
- **Training**: 5-fold stratified cross validation, 30 epochs, early stopping, data augmentation (flip, rotation, brightness, contrast), class weights balanced, Adam optimizer (lr=0.0001).
- **Output**: Sick or Healthy + confidence score (0-1).

**Strengths**: Fast (~0.1s per patch), free (runs locally), deterministic (same input = same output every time).

**Weaknesses**: Binary only (no severity levels), trained on limited data. **Critical gap**: The 500 "healthy" patches were NOT verified by a human expert. They were cropped randomly from areas not overlapping findings, then verified by Gemini + the detection guide as "Clean." But the guide itself was trained on sick-only — so the "healthy" verification is circular. The guide that never saw real healthy is deciding what's healthy. This is the biggest weakness of the ML model and why Round 2's model with real expert-labeled healthy data will be significantly better.

**Model v1 lesson**: An earlier 200-image model got 100% validation accuracy but failed completely on real drone images (predicted 98% sick). It had learned the source domain, not disease features. Model v2 (1,000 images) fixed this by cropping both classes from the same drone images.

### Method 2: AI + Detection Guide (Gemini 2.5 Flash)

A novel LLM-based approach. Instead of training a neural network, we built a **text guide** that describes what late blight looks like at each severity level, then gave it to an LLM (Gemini 2.5 Flash) along with the image patch.

**How we built the guide:**
- **Feedback loop**: We classified patches in batches of ~100. After each batch, we reviewed the results, identified mistakes, and updated the guide. 12 batches, 1,170 patches total.
- **Calibration phase**: The first 20 patches were done together with David to establish core rules: severity = spread not color, sporulation ≠ Mid, color varies across variants.
- **Iterative refinement**: Each batch revealed new patterns and fixed issues. Major fixes included: confidence clustering at 0.85 (58% of patches got exactly 0.85 — fixed by rewriting the rubric), sporulation "Undetermined" overuse (46% — fixed by changing default to "No"), and guide structure (reorganized into decision algorithm + rubrics + tables).
- **The full story is in the Learning Log** — a detailed record of every batch, every lesson learned, and every guide improvement.

**Guide structure**: The guide has a decision algorithm:
1. Is there necrotic tissue with water-soaked appearance? No → Clean. Yes → step 2.
2. What percentage of leaf surface is affected? <15% → Early. 15-50% → Mid. >50% → Late.
3. Check additional signals: sporulation, stem blackening, coalescence.
4. Assign confidence using a detailed rubric (0.3-0.95).

**Output**: Severity (Clean/Early/Mid/Late) + confidence + sporulation check + text reasoning.

**Strengths**: Rich output (severity + reasoning), no training data needed for the model itself (zero-shot LLM), guide is editable (update text to improve), highly interpretable (explains its reasoning per patch).

**Weaknesses**: Slow (~2s per patch), costs money (API calls), non-deterministic (same image can get different answers — we measured 12.2% contradiction rate), depends on prompt quality.

**Remarkable finding**: The guide was trained on ONLY sick patches (Clean = 0 in all 8 batches). It never saw a single healthy patch during development. Yet when run on all 5,187 patches, it successfully identified healthy patches. The LLM learned what "no disease" looks like just by learning what disease looks like. Impressive — but also a limitation (never learned the healthy boundary from real examples).

### Method 3: Combo (ML filter → Guide)

A two-stage pipeline combining both methods:
1. **Stage 1**: ML model scans all patches. Patches labeled "Healthy" are done — skip them.
2. **Stage 2**: Patches labeled "Sick" by ML go to the Guide for detailed classification (severity, sporulation, reasoning).

**Why**: ML is fast and free — it quickly eliminates obviously healthy patches. The Guide is slow and expensive but gives detailed results. By only sending ML's "Sick" patches to the Guide, we get the best of both worlds: ML's speed + Guide's detail.

**Result**: Out of ~5,187 patches, ML flagged ~2,133 as Sick. The Guide reclassified 1,177 of those (55%) as Clean — catching ML's false alarms. Only 956 patches (18.4%) were confirmed diseased by Combo.

---

## The Data

### Source
- 15 drone images of potato fields from a validated agricultural database
- Images captured at different dates across the growing season
- Fields at different stages: healthy, stressed, early disease, advanced disease

### Patch Grid
- Each drone image was sliced into a grid of 224×224 pixel patches
- Total: 5,187 patches across all 15 images
- Each patch was analyzed independently by all three methods

### Master CSVs
Three master CSV files (one per method) with 5,187 rows each, containing: image name, patch position (col, row, x, y), classification, confidence, and additional fields.

---

## What We Did in Round 1

### Phase 1: Proof of Concept
- First test: 30 images (20 sick from database + 10 healthy from PlantVillage)
- MobileNetV2 + Dense head → 100% accuracy
- Proved the concept works, but too small and too easy

### Phase 2: Detection Guide Development
- Built the detection guide through 12 batches of iterative refinement
- 1,170 patches classified by Gemini with continuous guide updates
- Discovered key patterns: severity = spread not color, sporulation on Early is normal, stem blackening = strongest Late indicator
- Major fixes: confidence clustering (58% at 0.85), sporulation defaults, guide restructure
- Final distribution: 60% Early / 34% Mid / 7% Late / 0% Clean
- Full process documented in the Learning Log

### Phase 3: ML Model Training
- Built 1,000-image dataset from drone crops (500 sick + 500 healthy)
- Healthy patches verified by Gemini + detection guide
- MobileNetV2 transfer learning, 5-fold cross validation
- Fixed Model v1's failure (learned source domain) by cropping both classes from same images

### Phase 4: Image Analysis
- Ran all three methods on 15 drone images (5,187 patches)
- Built per-image analysis: detection rates, severity distributions, heatmaps
- Key finding: ML over-detects (41% sick vs Guide 28% vs Combo 18%)
- Key finding: ML struggles with non-disease patterns (dark soil, shadows, flowers)
- Produced 5 tables + 15 heatmaps + findings summary

### Phase 5: Method Comparison
- Compared methods statistically: Kappa, QWK, McNemar's test, ECE
- Key finding: Combo is the best method (95.9% accuracy, Kappa = 0.876)
- Key finding: LLM non-determinism — 630 patches (12.2%) got opposite answers
- Key finding: Majority vote is biased (ML + Combo correlated at 77%)
- Key finding: Guide trained on sick-only but detected healthy (impressive generalization)
- Key finding: ECE = 0.0667 but misleading (mid-confidence is unreliable)
- Produced comparison tables, error analysis, prompt evolution charts, reliability diagram

---

## Key Findings Summary

  | Item | Description |
  |------|-------------|
  | Detection Guide | Reusable guide for any AI to detect late blight |
  | Learning Log | Detailed record of 12 batches of guide refinement |
  | ML Model | MobileNetV2 binary classifier (Google Colab notebook) |
  | Image Analysis Summary | Per-image results, heatmaps, detection rates |
  | Method Comparison Summary | Statistical comparison, error analysis, key findings |
  | Master CSVs (3) | Raw data: 5,187 rows per method |

---

## Limitations of Round 1

1. **No real ground truth** — no expert labeled the patches. We used majority vote (2/3 methods agree) which is biased because ML and Combo are correlated.
2. **Training data gaps** — ML's "healthy" patches were verified by Gemini + the guide, but the guide was trained on sick-only. This is circular: the system that never saw real healthy is verifying what's healthy. Guide trained on sick only. **Neither method saw real expert-labeled healthy patches.** This is the biggest gap between Round 1 and Round 2 — with real healthy data, both methods will improve significantly.
3. **LLM non-determinism** — 12.2% of patches get different answers on re-run. Not reliable enough for production use without mitigation.
4. **Binary ML** — the ML model only says Sick/Healthy. No severity classification. The Guide provides severity but is slower and costs money.
5. **Single LLM** — only tested with Gemini 2.5 Flash. Other models (Claude, GPT) might perform differently.
6. **Confidence unreliable** — mid-range confidence (0.6-0.8) is essentially a coin flip.

---

## What Round 2 Will Fix

| Limitation | Round 2 Solution |
|-----------|-----------------|
| No ground truth | Expert labels from agricultural researcher |
| No real healthy training data | Include real healthy patches in training for both methods |
| Binary ML model | YOLO object detection model (detects + localizes + classifies) |
| Single LLM | Test Guide with multiple LLMs (Claude, GPT, Gemini) |
| LLM non-determinism | Run Guide multiple times per patch, take consensus |
| Sick-only guide training | Build Guide v2 from scratch with healthy + sick, then merge with v1 |
| Guide "trust the database" bias | Remove the bias, let AI decide independently |
| Confidence clustering | Better rubric design from the start |

---

## Project Files

| Item | Location |
|------|----------|
| Detection Guide | ticket-008/disease-detection-guide.md |
| Learning Log | ticket-008/learning-log.md |
| ML Model Notebook | Google Colab (ticket-009) |
| Master CSVs (3) | agricalture/ticket-013-014-analysis/ |
| Image Analysis Summary | ticket 13/ticket-013-findings-summary.md |
| Method Comparison Summary | ticket 14/ticket-014-findings-summary.md |
| Phase 3 Findings | ticket 14/findings_phase3.md |
| All output PNGs | ticket 13/output/ + ticket 14/output/ |

---

*Round 1 complete. Next: Round 2 with YOLO, expert labels, and Guide v2.*
