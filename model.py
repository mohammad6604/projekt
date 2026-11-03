"""
Educational machine-learning demo.
Uses the Wisconsin Diagnostic Breast Cancer dataset, stored in this project as
data/breast_cancer.csv (569 rows; see data/README.md for source and licence).
This is not a medical device and must not be used for diagnosis or treatment.
"""
import csv
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

FEATURE_NAMES = [
    "mean radius",
    "mean texture",
    "mean perimeter",
    "mean area",
    "mean smoothness",
    "mean compactness",
    "mean concavity",
    "mean concave points",
    "mean symmetry",
    "mean fractal dimension",
]
FEATURE_LABELS_FA = {
    "mean radius": "شعاع میانگین",
    "mean texture": "بافت میانگین",
    "mean perimeter": "محیط میانگین",
    "mean area": "مساحت میانگین",
    "mean smoothness": "صافی میانگین",
    "mean compactness": "فشردگی میانگین",
    "mean concavity": "مقعر بودن میانگین",
    "mean concave points": "نقاط فرورفته میانگین",
    "mean symmetry": "تقارن میانگین",
    "mean fractal dimension": "بُعد فراکتالی میانگین",
}

DATA_PATH = Path(__file__).resolve().parent / "data" / "breast_cancer.csv"

def load_dataset(path=DATA_PATH):
    """
    اگر فایل CSV وجود داشت می‌خواند، در غیر این صورت از sklearn دانلود می‌کند.
    """
    # ۱. اگر فایل روی سیستم شما یا سرور بود، همان را می‌خواند
    if Path(path).exists():
        with open(path, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        features = np.array([[float(r[name]) for name in FEATURE_NAMES] for r in rows])
        target = np.array([int(r["target"]) for r in rows])
        return features, target
        
    # ۲. اگر فایل نبود (مثل سرور Render)، از sklearn می‌گیرد
    else:
        from sklearn.datasets import load_breast_cancer
        data = load_breast_cancer()
        # فقط ۱۰ ویژگی 'mean' را برمی‌داریم تا با FEATURE_NAMES هماهنگ باشد
        features = data.data[:, :10] 
        target = data.target
        return features, target

X, y = load_dataset()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
MODEL = make_pipeline(
    StandardScaler(),
    LogisticRegression(max_iter=3000, random_state=42)
)
MODEL.fit(X_train, y_train)

_y_pred = MODEL.predict(X_test)
HOLDOUT_ACCURACY = accuracy_score(y_test, _y_pred)


def _build_metrics():
    """Hold-out metrics. 'Malignant' (label 0) is treated as the positive class."""
    cm = confusion_matrix(y_test, _y_pred, labels=[0, 1])
    return {
        "n_test": int(len(y_test)),
        "accuracy": float(HOLDOUT_ACCURACY),
        "precision_malignant": float(precision_score(y_test, _y_pred, pos_label=0)),
        "recall_malignant": float(recall_score(y_test, _y_pred, pos_label=0)),
        "f1_malignant": float(f1_score(y_test, _y_pred, pos_label=0)),
        # rows = actual [malignant, benign], columns = predicted [malignant, benign]
        "confusion_matrix": cm.tolist(),
    }


METRICS = _build_metrics()

# Min / max / mean of every feature in the public dataset. Used for form hints
# and for warning the user when an input is outside the range the model has seen.
FEATURE_RANGES = {
    name: {
        "min": float(X[:, i].min()),
        "max": float(X[:, i].max()),
        "mean": float(X[:, i].mean()),
    }
    for i, name in enumerate(FEATURE_NAMES)
}


def _pick_example(target):
    """First hold-out row of the given class that the model classifies correctly."""
    for row, label, pred in zip(X_test, y_test, _y_pred):
        if label == target and pred == target:
            return dict(zip(FEATURE_NAMES, [round(float(v), 4) for v in row]))
    raise RuntimeError("no example found")  # pragma: no cover


# Real rows from the public dataset, for the "fill with example" buttons.
EXAMPLE_SAMPLES = {
    "benign": {"label": "نمونه‌ی خوش‌خیم", "values": _pick_example(1)},
    "malignant": {"label": "نمونه‌ی بدخیم", "values": _pick_example(0)},
}


def out_of_range_features(values):
    """Names of features whose value is outside the training-data range."""
    out = []
    for name, value in zip(FEATURE_NAMES, values):
        rng = FEATURE_RANGES[name]
        if value < rng["min"] or value > rng["max"]:
            out.append(name)
    return out


def predict_sample(values):
    """Return a cautious, educational model output for a 10-feature sample."""
    arr = np.asarray(values, dtype=float).reshape(1, -1)
    if arr.shape[1] != len(FEATURE_NAMES):
        raise ValueError("تعداد ویژگی‌ها معتبر نیست.")
    probabilities = MODEL.predict_proba(arr)[0]
    # sklearn's target labels are [0, 1]: malignant, benign
    malignant_probability = float(probabilities[0])
    benign_probability = float(probabilities[1])
    prediction = int(MODEL.predict(arr)[0])
    return {
        "label": "خوش‌خیم" if prediction == 1 else "بدخیم",
        "class_key": "benign" if prediction == 1 else "malignant",
        "benign_probability": round(benign_probability * 100, 1),
        "malignant_probability": round(malignant_probability * 100, 1),
        "accuracy": round(float(HOLDOUT_ACCURACY) * 100, 1),
    }
