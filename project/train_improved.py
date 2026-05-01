# Improved training: TF-IDF (word+char n-grams) + Logistic Regression tuning
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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import accuracy_score, classification_report


def main():
    print("Loading dataset...")
    df = load_dataset()
    print(f"Loaded {len(df)} samples")

    df["cleaned"] = df["text"].apply(clean_text)
    X = df["cleaned"].values
    y = df["emotion"].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # If dataset is large, sample a portion for quick hyperparameter tuning
    tune_size = 20000
    if len(X_train) > tune_size:
        print(f"Sampling {tune_size} rows for hyperparameter search...")
        X_tune, _, y_tune, _ = train_test_split(
            X_train, y_train, train_size=tune_size, stratify=y_train, random_state=42
        )
    else:
        X_tune, y_tune = X_train, y_train

    pipeline = Pipeline([
        ("vect", TfidfVectorizer()),
        ("clf", LogisticRegression(solver="saga", max_iter=2000))
    ])

    param_grid = {
        "vect__ngram_range": [(1,1), (1,2)],
        "vect__max_df": [0.9, 0.95],
        "vect__min_df": [2, 5],
        "vect__max_features": [20000, 50000],
        "clf__C": [0.1, 1.0]
    }

    print("Starting GridSearchCV (this may take a while)...")
    gs = GridSearchCV(pipeline, param_grid, cv=3, n_jobs=-1, verbose=2)
    gs.fit(X_tune, y_tune)

    print("Best params:", gs.best_params_)

    # Refit best pipeline on full training set
    print("Refitting best model on full training set...")
    best = gs.best_estimator_
    best.fit(X_train, y_train)

    print("Evaluating on test set...")
    y_pred = best.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {acc * 100:.2f}%")
    print("Classification Report:\n", classification_report(y_test, y_pred))

    out_path = os.path.join(ROOT, "data", "emotion_model_improved.pkl")
    with open(out_path, "wb") as f:
        pickle.dump(best, f)
    print("Saved improved model to:", out_path)


if __name__ == "__main__":
    main()
