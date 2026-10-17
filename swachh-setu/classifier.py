"""Pluggable classifier.

If a trained Keras model exists, it is used. Otherwise the app runs in DEMO mode with
deterministic placeholder predictions, so the UI and dashboard can be built and tested
before the real model is dropped in. Demo mode is always flagged in the API response.

Configure with environment variables:
  MODEL_PATH   path to .h5/.keras model   (default: model/waste_model.h5)
  LABELS_PATH  JSON list of class names   (default: model/labels.json)
  PREPROCESS   "mobilenet" (scale to [-1,1]) or "rescale" (divide by 255)
  IMG_SIZE     input size                 (default: 224)
"""
import hashlib
import io
import json
import os

import numpy as np
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.environ.get("MODEL_PATH", os.path.join(BASE, "model", "waste_model.h5"))
LABELS_PATH = os.environ.get("LABELS_PATH", os.path.join(BASE, "model", "labels.json"))
PREPROCESS = os.environ.get("PREPROCESS", "mobilenet")
IMG_SIZE = int(os.environ.get("IMG_SIZE", "224"))

DEFAULT_LABELS = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]


def _load_labels():
    if os.path.exists(LABELS_PATH):
        with open(LABELS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_LABELS


class Classifier:
    def __init__(self):
        self.labels = _load_labels()
        self.model = None
        self.demo = True
        self.error = None
        if os.path.exists(MODEL_PATH):
            try:
                from tensorflow.keras.models import load_model  # imported lazily
                self.model = load_model(MODEL_PATH)
                self.demo = False
            except Exception as exc:  # keep the app alive for the demo
                self.error = f"Could not load model: {exc}"

    def _preprocess(self, image: Image.Image) -> np.ndarray:
        image = image.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
        arr = np.asarray(image, dtype="float32")
        arr = arr / 127.5 - 1.0 if PREPROCESS == "mobilenet" else arr / 255.0
        return np.expand_dims(arr, 0)

    def predict(self, data: bytes, top_k: int = 3):
        image = Image.open(io.BytesIO(data))
        if self.model is not None:
            probs = self.model.predict(self._preprocess(image), verbose=0)[0]
        else:
            probs = self._demo_probs(data)
        order = np.argsort(probs)[::-1][:top_k]
        return [
            {"label": self.labels[i], "confidence": float(probs[i])}
            for i in order
            if i < len(self.labels)
        ]

    def _demo_probs(self, data: bytes) -> np.ndarray:
        seed = int(hashlib.sha256(data).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        raw = rng.random(len(self.labels)) ** 3
        return raw / raw.sum()


classifier = Classifier()
