#"""Swachh Setu: scan -> segregate -> recycle -> track."""
import os
import sqlite3
from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request

from classifier import classifier
from knowledge import CATEGORY_META, describe

BASE = os.path.dirname(os.path.abspath(__file__))
# Demo mode uses its own database so placeholder scans never mix with real ones.
DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(BASE, "scans_demo.db" if classifier.demo else "scans.db"),
)
# Demo predictions are random, so the confidence floor is not applied to them.
CONFIDENCE_FLOOR = 0.0 if classifier.demo else 0.60
MAX_UPLOAD_MB = 8

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                label TEXT NOT NULL,
                category TEXT NOT NULL,
                recyclable INTEGER NOT NULL,
                confidence REAL NOT NULL
            )"""
        )


init_db()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify(
        demo_mode=classifier.demo,
        labels=classifier.labels,
        error=classifier.error,
    )


@app.post("/api/classify")
def classify():
    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify(error="No image uploaded."), 400
    try:
        preds = classifier.predict(file.read())
    except Exception:
        return jsonify(error="That file could not be read as an image."), 400

    top = preds[0]
    info = describe(top["label"])
    uncertain = top["confidence"] < CONFIDENCE_FLOOR

    # Only log confident scans so the dashboard is not polluted by blurry photos.
    if not uncertain:
        with db() as conn:
            conn.execute(
                "INSERT INTO scans (ts, label, category, recyclable, confidence) VALUES (?,?,?,?,?)",
                (
                    datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    top["label"],
                    info["category"],
                    int(info["recyclable"]),
                    top["confidence"],
                ),
            )

    return jsonify(
        demo_mode=classifier.demo,
        uncertain=uncertain,
        result={**info, "confidence": top["confidence"]},
        alternatives=[
            {"label": p["label"], "confidence": p["confidence"]} for p in preds[1:]
        ],
    )


@app.get("/api/stats")
def stats():
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        recyclable = conn.execute(
            "SELECT COUNT(*) FROM scans WHERE recyclable = 1"
        ).fetchone()[0]
        by_cat = conn.execute(
            "SELECT category, COUNT(*) AS n FROM scans GROUP BY category"
        ).fetchall()
        recent = conn.execute(
            "SELECT ts, label, category, confidence FROM scans ORDER BY id DESC LIMIT 8"
        ).fetchall()
    return jsonify(
        total=total,
        recyclable=recyclable,
        recyclable_pct=round(100 * recyclable / total) if total else 0,
        by_category=[
            {
                "category": r["category"],
                "label": CATEGORY_META[r["category"]]["label"],
                "color": CATEGORY_META[r["category"]]["color"],
                "count": r["n"],
            }
            for r in by_cat
        ],
        recent=[dict(r) for r in recent],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
