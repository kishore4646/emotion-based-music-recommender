# ============================================================
# recommender.py — Core Recommendation Orchestrator
# Wires together: preprocessing → model → Spotify API
# ============================================================

import os
import sys

# Ensure src/ is on the path regardless of working directory
SRC_DIR  = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from preprocess  import clean_text
from model       import load_model, predict_emotion
from spotify_api import search_songs_by_emotion

# ── Emotion metadata (emoji + description) ───────────────────
EMOTION_META = {
    "happy":  {"emoji": "😊", "label": "Happy",   "color": "YELLOW"},
    "sad":    {"emoji": "😢", "label": "Sad",      "color": "BLUE"},
    "anger":  {"emoji": "😠", "label": "Angry",    "color": "RED"},
    "fear":   {"emoji": "😨", "label": "Fearful",  "color": "MAGENTA"},
    "trust":  {"emoji": "🤝", "label": "Trusting", "color": "GREEN"},
}


def get_recommendations(
    user_input: str,
    model=None,
    exclude_songs=None,   # FIX [6]: accept exclude list from dashboard
) -> dict:
    """
    Full recommendation pipeline:
      1. Preprocess user text
      2. Predict emotion with ML model
      3. Fetch songs from Spotify (or fallback)

    Args:
        user_input    (str):            Raw mood text from the user
        model:                          Pre-loaded sklearn pipeline (auto-loaded if None)
        exclude_songs (list, optional): Song names to skip (for shuffle / variety)

    Returns:
        dict: {
            "raw_input"     : str,
            "cleaned_input" : str,
            "emotion"       : str,
            "emotion_meta"  : dict,
            "songs"         : list,
            "source"        : str,
            "error"         : str | None
        }
    """
    if exclude_songs is None:
        exclude_songs = []

    result = {
        "raw_input":     user_input,
        "cleaned_input": "",
        "emotion":       "",
        "emotion_meta":  {},
        "songs":         [],
        "source":        "",
        "error":         None,
    }

    # ── Guard: empty input ────────────────────────────────────
    if not user_input or not user_input.strip():
        result["error"] = "Please enter a non-empty emotion description."
        return result

    try:
        # Step 1: Preprocess
        cleaned = clean_text(user_input)
        result["cleaned_input"] = cleaned

        # Step 2: Predict emotion
        emotion = predict_emotion(user_input, pipeline=model)
        result["emotion"]      = emotion
        result["emotion_meta"] = EMOTION_META.get(emotion, {
            "emoji": "🎵", "label": emotion.title(), "color": "WHITE"
        })

        # Step 3: Fetch songs (pass exclude list for variety)
        api_result       = search_songs_by_emotion(emotion, limit=5,
                                                   exclude_songs=exclude_songs)
        result["songs"]  = api_result["songs"]
        result["source"] = api_result["source"]

    except Exception as e:
        result["error"] = f"An error occurred: {str(e)}"

    return result


# ── Quick test when run directly ─────────────────────────────
if __name__ == "__main__":
    test_input = "I'm feeling really happy and full of life today!"
    rec = get_recommendations(test_input)
    print(f"Emotion : {rec['emotion']}")
    print(f"Source  : {rec['source']}")
    for s in rec["songs"]:
        print(f"  🎵 {s['name']} — {s['artist']}")