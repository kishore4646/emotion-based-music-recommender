# ============================================================
# model.py — Emotion Classification Model
# Trains a TF-IDF + Naive Bayes classifier and saves it
# ============================================================

import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import Pipeline

# Import our custom preprocessing
import sys
sys.path.insert(0, os.path.dirname(__file__))
from preprocess import clean_text

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "data", "emotion_model.pkl")

# Prefer the larger dataset if it exists
_alt = os.path.join(BASE_DIR, "data", "dataset_108k.csv")
if os.path.exists(_alt):
    DATASET_PATH = _alt


def load_dataset(path: str = DATASET_PATH) -> pd.DataFrame:
    """Load and validate the dataset CSV."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dataset not found at: {path}")

    df = pd.read_csv(path)

    # Basic validation
    required_cols = {"text", "emotion"}
    if not required_cols.issubset(df.columns):
        raise ValueError(f"Dataset must contain columns: {required_cols}")

    # Drop rows with missing values
    df = df.dropna(subset=["text", "emotion"])
    df["text"] = df["text"].astype(str)
    df["emotion"] = df["emotion"].str.strip().str.lower()

    return df


def train_model(save: bool = True) -> Pipeline:
    """
    Full training pipeline:
      - Load dataset
      - Preprocess text
      - Build TF-IDF + Naive Bayes pipeline
      - Evaluate on test split
      - Save model to disk

    Args:
        save (bool): Whether to save the trained model to disk

    Returns:
        sklearn.pipeline.Pipeline: Trained pipeline
    """
    print("─" * 50)
    print(" Loading dataset...")
    df = load_dataset()
    print(f" Found {len(df)} samples across {df['emotion'].nunique()} emotions")
    print(f" Emotions: {sorted(df['emotion'].unique())}")

    # Apply text preprocessing
    print("\n Preprocessing text...")
    df["cleaned"] = df["text"].apply(clean_text)

    X = df["cleaned"].values
    y = df["emotion"].values

    # Train / test split (80/20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Build sklearn pipeline: vectorizer → classifier
    print("\n Training TF-IDF + Naive Bayes model...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),   # unigrams + bigrams for richer features
            max_features=5000,
            sublinear_tf=True,    # log scaling for better performance
        )),
        ("clf", MultinomialNB(alpha=0.5)),  # Laplace smoothing
    ])

    pipeline.fit(X_train, y_train)

    # Evaluate
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n Test Accuracy: {acc * 100:.1f}%")
    print("\n Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save model
    if save:
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(pipeline, f)
        print(f" Model saved → {MODEL_PATH}")

    print("─" * 50)
    return pipeline


def load_model() -> Pipeline:
    """
    Load trained model from disk.
    Trains a new model if none exists.

    Returns:
        sklearn.pipeline.Pipeline: Loaded (or freshly trained) pipeline
    """
    if not os.path.exists(MODEL_PATH):
        print(" No saved model found. Training now...")
        return train_model(save=True)

    with open(MODEL_PATH, "rb") as f:
        pipeline = pickle.load(f)

    return pipeline


def predict_emotion(text: str, pipeline: Pipeline = None) -> str:
    """
    Predict the emotion of a given text string.

    Args:
        text (str): Raw user input
        pipeline: Pre-loaded model pipeline (loads from disk if None)

    Returns:
        str: Predicted emotion label
    """
    if pipeline is None:
        pipeline = load_model()

    cleaned = clean_text(text)
    if not cleaned:
        return "happy"  # Safe fallback

    emotion = pipeline.predict([cleaned])[0]
    # Normalize output to plain python str
    try:
        return str(emotion).strip().lower()
    except Exception:
        return "happy"


# ── Train when run directly ───────────────────────────────────
if __name__ == "__main__":
    train_model()
