# ============================================================
# main.py — Mood-Based Music Recommender
# Entry point: run with `python main.py`
# ============================================================

import os
import sys
import time

# ── Path setup ───────────────────────────────────────────────
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR  = os.path.join(ROOT_DIR, "src")
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, ROOT_DIR)

from src.recommender import get_recommendations, EMOTION_META
from src.model       import load_model, train_model

# ── ANSI color codes for terminal styling ────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"

EMOTION_COLORS = {
    "happy":  C.YELLOW,
    "sad":    C.BLUE,
    "anger":  C.RED,
    "fear":   C.MAGENTA,
    "trust":  C.GREEN,
}


def banner():
    """Print the app banner."""
    print()
    print(C.CYAN + C.BOLD + "╔══════════════════════════════════════════════════════╗" + C.RESET)
    print(C.CYAN + C.BOLD + "║        🎵  MOOD-BASED MUSIC RECOMMENDER  🎵          ║" + C.RESET)
    print(C.CYAN + C.BOLD + "║     Powered by NLP + Machine Learning + Spotify      ║" + C.RESET)
    print(C.CYAN + C.BOLD + "╚══════════════════════════════════════════════════════╝" + C.RESET)
    print()


def divider(char="─", width=56):
    """Print a horizontal divider."""
    print(C.DIM + char * width + C.RESET)


def print_songs(songs: list, source: str):
    """Render the song list with clickable Spotify links."""
    source_label = (
        f"{C.GREEN}● Live Spotify API{C.RESET}"
        if source == "spotify_api"
        else f"{C.YELLOW}● Curated Recommendations{C.RESET}"
    )
    print(f"\n  Source: {source_label}\n")

    for i, song in enumerate(songs, 1):
        name   = song.get("name",   "Unknown Track")
        artist = song.get("artist", "Unknown Artist")
        url    = song.get("url",    "")

        print(f"  {C.BOLD}{C.CYAN}{i}.{C.RESET} {C.WHITE}{name}{C.RESET} {C.DIM}—{C.RESET} {C.MAGENTA}{artist}{C.RESET}")
        if url:
            print(f"     {C.DIM}🔗 {url}{C.RESET}")
        print()


def run_single_recommendation(model):
    """Get input, predict, and display recommendations."""
    divider()
    print()
    user_input = input(
        f"  {C.BOLD}💬 Describe how you're feeling:{C.RESET}\n  > "
    ).strip()

    if not user_input:
        print(f"\n  {C.RED}⚠  Please enter something about your mood.{C.RESET}\n")
        return

    # Thinking animation
    print(f"\n  {C.DIM}Analyzing your mood", end="", flush=True)
    for _ in range(3):
        time.sleep(0.3)
        print(".", end="", flush=True)
    print(f"{C.RESET}\n")

    # Get recommendations
    result = get_recommendations(user_input, model=model)

    # ── Error handling ────────────────────────────────────────
    if result.get("error"):
        print(f"  {C.RED}✗ Error: {result['error']}{C.RESET}\n")
        return

    emotion = result["emotion"]
    meta    = result["emotion_meta"]
    emoji   = meta.get("emoji", "🎵")
    label   = meta.get("label", emotion.title())
    color   = EMOTION_COLORS.get(emotion, C.WHITE)

    # ── Display detected emotion ──────────────────────────────
    print(f"  {C.BOLD}Detected Emotion:{C.RESET}  {color}{C.BOLD}{emoji} {label}{C.RESET}")
    print()

    # ── Display songs ─────────────────────────────────────────
    divider("·")
    print(f"\n  {C.BOLD}🎶 Recommended Songs for You:{C.RESET}")
    print_songs(result["songs"], result["source"])


def main():
    """Main application loop."""
    banner()

    # ── Load / train model ────────────────────────────────────
    print(f"  {C.DIM}Loading emotion detection model...{C.RESET}")
    try:
        model = load_model()
        print(f"  {C.GREEN}✓ Model ready{C.RESET}\n")
    except Exception as e:
        print(f"  {C.YELLOW}⚠  Could not load model. Training now...{C.RESET}\n")
        try:
            model = train_model(save=True)
        except Exception as train_err:
            print(f"  {C.RED}✗ Failed to train model: {train_err}{C.RESET}")
            sys.exit(1)

    # ── App loop ──────────────────────────────────────────────
    while True:
        try:
            run_single_recommendation(model)

        except KeyboardInterrupt:
            print(f"\n\n  {C.CYAN}Thanks for using the Mood Music Recommender! 🎵{C.RESET}\n")
            break

        divider()
        print()
        again = input(
            f"  {C.BOLD}Try another mood?{C.RESET} {C.DIM}(y/n){C.RESET} > "
        ).strip().lower()

        if again not in ("y", "yes"):
            print(f"\n  {C.CYAN}Thanks for using the Mood Music Recommender! 🎵{C.RESET}\n")
            break

    divider("═")
    print()


if __name__ == "__main__":
    main()
