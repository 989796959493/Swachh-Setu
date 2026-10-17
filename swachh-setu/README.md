# Swachh Setu

**Scan → Segregate → Recycle → Track.** An AI-first waste assistant built for the
AI First Product Builder Hackathon 2026 (India's garbage problem).

Point your phone at a piece of waste. Swachh Setu identifies it with a MobileNetV2
image classifier (the Kachra Cam engine), tells you which bin it belongs in, suggests how
to reuse or recycle it, and logs the scan to an impact dashboard.

## Tracks covered

| Hackathon track | What Swachh Setu does |
|---|---|
| Waste collection & segregation | Image classification mapped to green / blue / black bins and e-waste |
| Recycling & circular economy | Per-item recycling flag, reuse ideas and disposal tips |
| Civic education | Every result teaches the citizen *why* and *how* to dispose correctly |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # open http://localhost:5000
```

Without a model file the app starts in **demo mode** (placeholder predictions, clearly
flagged in the UI) so you can test the whole flow.

## Plug in the trained Kachra Cam model

1. Put the model at `model/waste_model.h5` (or set `MODEL_PATH`).
2. Put the class names, **in the same order as training**, in `model/labels.json`, e.g.
   `["cardboard", "glass", "metal", "paper", "plastic", "trash"]`.
3. Preprocessing must match training. Default is MobileNetV2 scaling to [-1, 1]. If you
   trained with `rescale=1/255`, run with `PREPROCESS=rescale`.
4. Restart. The demo banner disappears.

Labels the app does not know get a safe "not sure" fallback. Add new ones in `knowledge.py`.

## API

| Endpoint | Purpose |
|---|---|
| `POST /api/classify` | multipart field `image` → label, bin, tips, confidence |
| `GET /api/stats` | totals, recyclable %, per-category counts, recent scans |
| `GET /api/health` | model status (`demo_mode`) |

Scans below 60% confidence are shown to the user with a retake prompt and are **not**
counted, so the dashboard reflects reliable data.

## Project layout

```
app.py          Flask routes + SQLite scan log
classifier.py   Model loading / prediction (demo fallback)
knowledge.py    Label → bin, recyclability, tips
templates/      Single-page mobile-first UI
```

## Limitations and next steps

- Classifies one item per photo; multi-object scenes are not supported yet.
- Accuracy depends on the training data. Photos in Indian street conditions matter most.
- Next: drain-blockage monitoring (track 4), ward-level heatmap from geotagged scans,
  and hardware/IoT smart-bin integration (track 6).

## Team

Team Swachh Setu · Pranveer Singh Institute of Technology, Kanpur
