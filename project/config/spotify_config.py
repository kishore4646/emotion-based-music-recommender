# ============================================================
# spotify_config.py — Spotify API Credentials
# ============================================================

import os

# ── Hardcode credentials for local development only (override via env vars)
SPOTIFY_CLIENT_ID     = os.getenv("SPOTIFY_CLIENT_ID", "7d9f5ecc33344e9cb4e92d8cb5a64db0")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "084b2e96dc5f4b9db1f2f8f78de4fb96")