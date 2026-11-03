"""Prints the model evaluation numbers (handy for copying into the report).

Run:  python evaluate.py
"""
from sklearn.model_selection import StratifiedKFold, cross_val_score

from model import METRICS, MODEL, X, y


def main():
    cm = METRICS["confusion_matrix"]
    print(f"Test samples: {METRICS['n_test']}")
    print("Confusion matrix (rows = actual, columns = predicted)")
    print("                 pred malignant  pred benign")
    print(f"actual malignant {cm[0][0]:>14}  {cm[0][1]:>11}")
    print(f"actual benign    {cm[1][0]:>14}  {cm[1][1]:>11}")
    print(f"Accuracy            : {METRICS['accuracy']:.4f}")
    print(f"Precision (malignant): {METRICS['precision_malignant']:.4f}")
    print(f"Recall    (malignant): {METRICS['recall_malignant']:.4f}")
    print(f"F1        (malignant): {METRICS['f1_malignant']:.4f}")

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = cross_val_score(MODEL, X, y, cv=cv, scoring="accuracy")
    print(f"5-fold CV accuracy  : {scores.mean():.4f} +/- {scores.std():.4f}")


if __name__ == "__main__":
    main()
