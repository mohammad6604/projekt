import os

import numpy as np
from flask import Flask, render_template, request

from model import (
    EXAMPLE_SAMPLES,
    FEATURE_LABELS_FA,
    FEATURE_NAMES,
    FEATURE_RANGES,
    METRICS,
    out_of_range_features,
    predict_sample,
)

app = Flask(__name__)


def parse_values(raw_values):
    """Validate the raw form strings and return them as a list of floats."""
    sample = []
    for name in FEATURE_NAMES:
        label = FEATURE_LABELS_FA[name]
        raw = raw_values[name]
        if not raw:
            raise ValueError("لطفاً همه فیلدها را تکمیل کنید.")
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"مقدار «{label}» یک عدد معتبر نیست.") from None
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"مقدار «{label}» باید عددی و غیرمنفی باشد.")
        sample.append(value)
    return sample


def build_warnings(sample):
    """Soft warnings (do not block the prediction) for out-of-range inputs."""
    messages = []
    for name in out_of_range_features(sample):
        rng = FEATURE_RANGES[name]
        value = sample[FEATURE_NAMES.index(name)]
        messages.append(
            f"مقدار «{FEATURE_LABELS_FA[name]}» ({value:g}) خارج از بازه‌ی داده‌های "
            f"آموزشی ({rng['min']:.4g} تا {rng['max']:.4g}) است؛ "
            "نتیجه‌ی مدل برای این مقدار قابل اتکا نیست."
        )
    return messages


@app.route("/health")
def health():
    """Used by cloud platforms to check that the service is alive."""
    return {"status": "ok"}


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    warnings = []
    values = {}
    if request.method == "POST":
        # Keep what the user typed so the form is not cleared on an error.
        values = {name: request.form.get(name, "").strip() for name in FEATURE_NAMES}
        try:
            sample = parse_values(values)
            warnings = build_warnings(sample)
            result = predict_sample(sample)
        except ValueError as exc:
            error = str(exc)
        except Exception:
            app.logger.exception("prediction failed")
            error = "در پردازش اطلاعات خطایی رخ داد. دوباره تلاش کنید."
    return render_template(
        "index.html",
        feature_names=FEATURE_NAMES,
        labels=FEATURE_LABELS_FA,
        ranges=FEATURE_RANGES,
        examples=EXAMPLE_SAMPLES,
        metrics=METRICS,
        result=result,
        error=error,
        warnings=warnings,
        values=values,
    )


if __name__ == "__main__":
    # Development server only. Debug mode is OFF by default; enable it locally
    # with the environment variable FLASK_DEBUG=1. Do not expose publicly
    # for real patient data.
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
