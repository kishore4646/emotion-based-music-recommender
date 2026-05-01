import os
import sys
# Ensure src is importable
ROOT = os.path.join(os.path.dirname(__file__), '..', 'src')
ROOT = os.path.normpath(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from model import load_dataset, load_model
from preprocess import preprocess_batch
from sklearn.metrics import accuracy_score

if __name__ == '__main__':
    print('Loading dataset...')
    try:
        df = load_dataset()
    except Exception as e:
        print('Failed to load dataset:', e)
        raise SystemExit(1)

    print(f'Found {len(df)} samples')
    texts = df['text'].astype(str).tolist()
    y_true = df['emotion'].astype(str).str.strip().str.lower().tolist()

    print('Preprocessing texts...')
    X = preprocess_batch(texts)

    print('Loading model (will train if missing)...')
    model = load_model()

    print('Predicting... this may take a moment')
    y_pred = model.predict(X)

    acc = accuracy_score(y_true, y_pred)
    print(f'Full dataset accuracy: {acc*100:.2f}%')
    # Optionally save to a small file for dashboard to pick up
    out = os.path.join(os.path.dirname(__file__), '..', 'data', 'full_accuracy.txt')
    with open(out, 'w') as f:
        f.write(f'{acc:.6f}\n')
    print('Saved accuracy to', out)
