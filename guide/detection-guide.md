# Late Blight Detection Guide Patch Analysis

> **Purpose**: Reusable guide for any AI model to detect and classify late blight severity in 224X224 pixel drone image patches.
> **Trained on**: 1,170 confirmed disease patches from validated agricultural database.
> **Methodology**: "Late Blight Master Classifier" classify by SPREAD, not by color.
>
> **Visual Reference**: [Detection Guide Test Report (with real images & coordinates)](http://localhost:3200/knowledge-base/detection_guide_test_report.html)

---

## Quick Reference — Decision Algorithm

```
1. Is there necrotic (brown/black) tissue with water-soaked appearance?
   NO  → Clean
   YES → Go to step 2

2. What percentage of leaf surface is affected?
   <15%  → Early
   15-50% → Mid
   >50%  → Late

3. Are there additional signals?
   - Sporulation (white fuzz) → supports Mid, but check spread first
   - Blackened stem/petiole → Late (strongest single indicator)
   - Multiple spots merging → Mid (coalescence)
   - Structural collapse → Mid or Late depending on extent
   - Multiple leaves affected → Late

4. Assign confidence:
   - 0.3-0.5: Barely visible, almost no visible symptoms
   - 0.5-0.7: Subtle but detectable symptoms
   - 0.7-0.85: Clear symptoms, straightforward classification
   - 0.85-0.95: Very obvious, textbook case
```

---

## What Is Late Blight?

Late blight (*Phytophthora infestans*) is a devastating plant disease affecting potatoes and tomatoes. It spreads rapidly in cool, moist conditions and can destroy entire fields in days. The disease progresses from small isolated spots → merging lesions → total leaf death.

---

## Step 1: Detection: Is There Disease?

**Look for**: Necrotic (black/brown) tissue with a water-soaked appearance on leaf surfaces.

**If no symptoms found** → label as **"Clean"**

### What Clean Looks Like
- Uniform green color, intact leaf structure
- No browning, no wilting, no fuzzy growth
- May contain healthy leaves, stems, soil, shadows, background
- **Key**: If there is NO necrotic tissue and NO water-soaked appearance → Clean
- When scanning a full field image, 99%+ of patches will be Clean

### Ground vs. Brown Leaves  Don't Confuse Them
Many patches will contain **soil, mud, or bare ground** which is brown/gray. This is NOT disease.
- **Ground/soil**: Uniform texture, no leaf veins, no water-soaked edges. Looks like dirt. → **Clean**
- **Brown leaves (disease)**: Has leaf structure (veins, edges, shape), water-soaked or collapsed tissue, sits ON or AMONG green foliage. → **Disease**
- **Key difference**: Ground has no leaf structure. Diseased tissue still looks like a leaf — just a dying one.
- If a patch is mostly soil/ground with no plant tissue → **Clean** (nothing to be sick)

### What Disease Looks Like (At Any Stage)
- Brown, black, or gray-brown spots or areas on leaf tissue
- Water-soaked (translucent, wet-looking) edges around lesions
- Tissue that is collapsing, shriveling, or dying
- White fuzzy growth (sporulation) on leaf surface

---

## Step 2: Classification: How Bad Is It?

**CRITICAL RULE: Classify by SPREAD (area affected), NOT by color intensity.**
A small dark spot = Early. A large pale area = Mid. Darkness tells you nothing about severity.

### Early Stage (59% of patches)
| Feature | Description |
|---------|-------------|
| **Pattern** | Isolated, distinct necrotic spots separate, NOT merging |
| **Scope** | Less than 15% of leaf surface affected |
| **Systemic impact** | None. No stem/petiole involvement. Surrounding tissue healthy/green |
| **Spots** | 1-3 separate spots, each clearly distinct |
| **Color variants** | Gray-brown, yellow-brown, purple-brown, reddish-brown all valid |
| **Confidence range** | 0.3 (barely visible) to 0.9 (textbook isolated spot) |

**Subtle Early patches**: Some are barely visible pale discoloration, less than 5% affected, confidence as low as 0.3. These cluster in certain image sources. Trust the database disease is confirmed even when near-invisible.

**Early + sporulation**: ~15% of Early patches show sporulation (white fuzz on a small isolated lesion). This is normal sporulation alone does NOT upgrade to Mid. Always check spread first.

### Mid Stage (36% of patches)
| Feature | Description |
|---------|-------------|
| **Pattern** | Coalescence multiple spots MERGING together |
| **Scope** | 15-50% of leaf surface affected |
| **Systemic impact** | Progression toward leaf veins or petioles |
| **Sporulation** | White fuzzy growth is a strong Mid indicator (~35% of Mid patches show it) |
| **Texture** | Collapsed, shriveled gray-brown tissue covering large areas |
| **Confidence range** | 0.7 (borderline 15%) to 0.9 (clear 30-40% with coalescence) |

**Key indicators of Mid (vs Early)**:
1. Spots are CONNECTING, not isolated
2. Area affected is clearly above 15%
3. Tissue is collapsing (not just discolored, but structurally damaged)
4. Heavy sporulation covering large areas

**Borderline Early/Mid (the hardest call)**: At ~15% affected:
- If spots are still isolated → Early (0.75-0.8)
- If spots are starting to merge + sporulation → Mid (0.75)
- When in doubt at 15%, lean toward the side with more evidence

### Late Stage (5% of patches)
| Feature | Description |
|---------|-------------|
| **Pattern** | Extensive, uncontrolled necrosis  overwhelming damage |
| **Scope** | More than 50% of leaf area affected, OR total structural collapse |
| **Systemic impact** | Blackened stems, dying/dead leaves, multi-leaf involvement |
| **Healthy tissue** | Little to none remaining |
| **Confidence** | Almost always 0.9-0.95 (Late is unmistakable) |

**Strongest Late indicators** (any one of these = Late):
1. **Blackened, shriveled stem/petiole** → Late (0.9). The single strongest indicator. Can extend to fruit pedicels.
2. **Multi-leaf necrosis** → When necrosis spans across multiple leaves in one patch.
3. **Total structural collapse** → Leaf tissue is dead, no functional tissue remaining.
4. **>50% necrosis** → More brown/black than green.

**Late + sporulation**: Unusual but confirmed (~3% of Late patches). Indicates transitional phase where severe damage coexists with active spore production.

**Late clusters unpredictably**: Late patches cluster in specific image source groups, not evenly distributed. Some batches have zero Late, others have 10%. Extreme example: image_id 8782293 had 50% Late rate (3 of 6 patches) some sources capture severely diseased areas.

---

## Confidence Scoring Rubric

**IMPORTANT: Distribute confidence scores across the FULL range. Do NOT default to 0.85 for every clear case.**
Use the decision tree below to pick the right score — each score has distinct criteria.

| Score | Meaning | When to use |
|-------|---------|-------------|
| **0.3** | Extremely subtle | Near-invisible symptoms. Patch looks almost clean but database confirms disease. |
| **0.4** | Very subtle | Barely detectable discoloration. Need to look hard to find anything. |
| **0.5** | Borderline visible | Faint symptoms present but classification is uncertain. |
| **0.6** | Somewhat clear | Symptoms visible but small or ambiguous. Could be Early or could be nothing. |
| **0.7** | Moderately clear | Clear disease present but affected area is hard to estimate precisely. |
| **0.75** | Fairly clear | Good evidence but some ambiguity — borderline between two stages (e.g., Early/Mid at ~15%). |
| **0.8** | Clear | Solid match for the assigned stage. The affected area is clearly within one stage's range but not a textbook example. |
| **0.85** | Very clear | Strong match — affected area and pattern strongly support the classification. No real ambiguity. |
| **0.9** | Highly confident | Textbook case. Unmistakable pattern. ALL Late classifications should be 0.9+. |
| **0.95** | Maximum confidence | Reserved for extreme Late cases (total structural collapse, >70% necrosis, blackened stems with dead tissue). |

### Confidence decision tree:
```
Is the disease barely visible?
  YES → 0.3-0.5 (based on how hard it is to see)
  NO ↓
Are you uncertain between two stages?
  YES → 0.7-0.75 (borderline cases)
  NO ↓
Is it a solid match but with some minor ambiguity?
  YES → 0.8
  NO ↓
Is it a strong, clear case?
  YES → 0.85
  NO ↓
Is it unmistakable / textbook?
  YES → 0.9 (or 0.95 for extreme Late)
```

---

## Common Mistakes to Avoid

### 1. Color Darkness != Severity
A small, very dark spot is Early. A large, pale gray area is Mid. NEVER upgrade a classification because the color is intense only upgrade based on SPREAD.

### 2. Sporulation != Mid
White fuzzy growth appears on 15% of Early patches. Always check the affected area percentage BEFORE considering sporulation. Sporulation is a supporting indicator, not a primary classifier.

### 3. Stem vs. Leaf Assessment
Some patches show stems more prominently than leaves. Stem necrosis (blackened, shriveled) indicates systemic spread:
- Blackened stem alone → Late (0.9)
- Stem discoloration without shriveling → Mid consideration
- Stem is naturally darker don't confuse healthy dark stems with disease

### 4. Same Source = Different Severity
Multiple patches from the same image can span Early/Mid/Late. Don't assume consistency — classify each patch independently. The largest cluster observed: 9 findings from one image (image_id 4267804) spanning Early and Mid.

### 5. Trust the Database
Every patch in this dataset is CONFIRMED disease. If a patch looks almost clean, it still has disease — just barely visible. Assign Early with low confidence (0.3-0.5) rather than Clean.

### 6. Sporulation: Default to "No", Not "Undetermined"
Sporulation = white fuzzy/cottony growth on the leaf surface. It's either visible or it isn't.
- If you see white fuzzy growth → **"Yes"**
- If the patch is clear enough to assess but shows no white fuzz → **"No"**
- Only use **"Undetermined"** when the patch is too blurry, dark, or low-quality to assess sporulation at all
- Do NOT default to "Undetermined" out of caution — most patches are clear enough to say "No"

### 7. Don't Cluster Confidence at 0.85
Use the full confidence range. Not every clear case is 0.85. Use the confidence decision tree above:
- A clear Early with a single well-defined spot → 0.8 (solid match, not extraordinary)
- A clear Early with textbook isolated lesion + visible water-soaked edges → 0.85
- A clear Mid with unmistakable 30-40% coverage + coalescence → 0.9
- Differentiate between "clear" (0.8) and "very clear" (0.85) and "textbook" (0.9)

---

## Color & Texture Reference

### Color Variants (All Valid for Any Stage)
| Color | Description | Stage frequency |
|-------|-------------|----------------|
| **Gray-brown** | Most common. Dark matte brown. | All stages |
| **Yellow-brown** | Translucent, wet-looking. Water-soaked variant. | Mostly Early |
| **Purple-brown** | Classic late blight color. Distinct purple tint. | Very common in Early |
| **Reddish-brown** | Reddish tint variant. | Both Early and Mid |
| **Dark black** | Very dark necrotic tissue. | Mid and Late |

### Texture Indicators
| Texture | Description | What it means |
|---------|-------------|---------------|
| **Water-soaked** | Slightly translucent, wet-looking tissue edges | Active disease, any stage |
| **Collapsed/dried** | Shriveled, sunken leaf areas | Mid or higher |
| **White fuzzy** | Sporulation — cottony white growth on surface | Supports Mid, but verify spread |
| **Structural collapse** | Leaf tissue completely dead and crumbling | Late |
| **Blackened stem** | Dark, shriveled petiole or stem | Late (strongest indicator) |

---

## Output Per Patch

For every patch analyzed, provide:
1. **Classification**: Early | Mid | Late | Clean
2. **Confidence Score**: 0.0 - 1.0 (see rubric above)
3. **Rationale**: One sentence focusing on SPREAD and PATTERN observed
4. **Sporulation Check**: Yes / No / Undetermined

---

## Statistical Profile (1,170 patches)

| Metric | Value |
|--------|-------|
| Patches analyzed | 1,170 / 5,280 |
| Clean | 0 (all confirmed disease) |
| Early stage | 697 (60%) |
| Mid stage | 395 (34%) |
| Late stage | 78 (7%) |
| Sporulation detected | 218 patches (19%) |
| Avg confidence | 0.82 |
| Confidence range | 0.3 — 0.95 |
| Phase | Gemini 2.5 Flash batch classification |

### Distribution Insights
- **Early dominates**: ~60% of all patches. Most disease in this dataset is early-stage.
- **Mid is substantial**: ~34%. Significant amount of progressed disease.
- **Late is rare but clustered**: ~7% overall, but reaches 10-25% in some source batches. Later survey periods tend to have more Late — disease progresses over time.
- **Sporulation**: 19% overall. ~35% of Mid patches show it, ~15% of Early patches show it.
- **Zero Clean**: Every confirmed patch has detectable disease, even if barely visible.
- **Distribution is stable but shifts**: 60/34/7 across 1,170 patches. Early batches had ~60/35/5; later batches trend toward more Mid and Late (up to 17% Late in heaviest batch). Later survey periods capture more progressed disease.
- **Disease severity trends up**: Later finding IDs (higher numbers = later surveys) show more Late-stage disease. Some source batches hit 17-25% Late rate vs 5% average. This reflects temporal disease progression in the field.

---

## Full Image Scanning — ALWAYS Slice First

**CRITICAL: NEVER try to analyze a full image directly. ALWAYS slice into 224×224 patches first.**

This guide was trained on **224×224 pixel patches**. That is the only resolution it works at. Any image of any size MUST be sliced into 224×224 patches before classification. Do not skip this step. Do not try to eyeball the full image — disease spots are tiny and invisible at full zoom.

### Slice Protocol (Mandatory)
1. Take the input image (any size: W × H pixels)
2. **Slice** into a grid of **224×224 patches** — this is non-negotiable
3. Start from top-left (0, 0), move right by 224px, down by 224px
4. Edge handling: last column/row overlaps to cover all pixels
5. Grid size: `ceil(W/224) × ceil(H/224)` patches
6. **Classify EACH patch individually** using Steps 1-2 of this guide
7. Each patch is analyzed at 224×224 — the resolution this guide was trained on
8. Do NOT analyze patches at any other resolution

### Required Output: Severity Map
After classifying all patches, **always produce a severity map**. This is a required output, not optional.

**Severity Map Color Code:**
| Color | Meaning |
|-------|---------|
| Green | Clean — no disease |
| Yellow | Early — isolated spots, <15% affected |
| Orange | Mid — merging lesions, 15-50% affected |
| Red | Late — extensive necrosis, >50% affected |

**Map format**: A grid matching the patch layout. Each cell colored by classification. Include:
- Grid coordinates (column, row) for every non-Clean patch
- Pixel coordinates (x, y) for every non-Clean patch
- Classification + confidence for each disease patch
- Summary: total patches, disease count, Early/Mid/Late breakdown

### Detection Challenges to Watch For
1. **Ground vs. brown leaves** — Soil/mud is brown but is NOT disease. Only brown LEAF tissue with leaf structure (veins, edges) counts as disease. See "Ground vs. Brown Leaves" section above.
2. **Stem necrosis** — brown on brown = low contrast. Look carefully for blackened, shriveled stems.
3. **Flowers/dried petals** — #1 false positive. White/brown petals look brownish. Must distinguish from disease tissue.
4. **Tiny disease spots** — invisible at full image zoom, only visible at patch level. That's why slicing is mandatory.
5. **Most patches are Clean** — 99%+ in a healthy field. Only 1-5 out of hundreds may show disease.

---

## How to Use This Guide

### For a single patch (224×224):
1. **Detect**: Is there late blight? If no symptoms → Clean
2. **Classify**: Based on SPREAD and SYSTEMIC IMPACT (not color darkness)
3. **Score confidence**: Using the rubric above
4. **Output**: Classification, Confidence, Rationale, Sporulation

### For a full field image (any size):
1. **Slice** into 224×224 patches — ALWAYS, no exceptions
2. **Classify** each patch individually at 224×224 resolution
3. **Build severity map** — color-coded grid (Green/Yellow/Orange/Red)
4. **Report** all disease locations with grid + pixel coordinates
5. **Output**: Severity map + disease patch list + summary statistics

---

*Last updated: 2026-03-03*
*Source: Ticket-008 — Disease Patch Analysis (1,170 patches across 12 batches)*
*Classifier: Gemini 2.5 Flash with iterative guide refinement every 20 patches*
