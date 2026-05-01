import os
import sys
import pickle

# Ensure src is importable
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from model import load_dataset
from preprocess import clean_text
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split


def main():
    df = load_dataset()
    df["cleaned"] = df["text"].apply(clean_text)
    X = df["cleaned"].values
    y = df["emotion"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    model_path = os.path.join(ROOT, "data", "emotion_model_improved.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc * 100:.2f}%")
    print("Classification Report:\n", classification_report(y_test, y_pred))


if __name__ == "__main__":
    main()
