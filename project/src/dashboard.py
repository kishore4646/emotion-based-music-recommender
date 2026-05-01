# ============================================================
# dashboard.py — Emotion-Based Music Recommender Dashboard v2
# Stunning interactive Streamlit app
# Run with: streamlit run dashboard.py
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys, random, time
from datetime import datetime
from collections import Counter

# Project layout: project/ (root) contains `src/` and `data/`.
# __file__ is src/dashboard.py, so take the parent directory to get project root.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_DIR = os.path.join(ROOT_DIR, "src")
DATA_DIR = os.path.join(ROOT_DIR, "data")
# Ensure project root is on sys.path so imports like `src.recommender` work.
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.recommender import get_recommendations, EMOTION_META
from src.model       import load_model, train_model, MODEL_PATH
from src.spotify_api import search_songs_by_emotion

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="EmotionWave · Music Recommender",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════
# MASTER STYLES
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Cabinet+Grotesk:wght@300;400;500;700;800&family=Instrument+Serif:ital@0;1&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');

/* ━━━━━━━━━━━━━━ ROOT VARIABLES ━━━━━━━━━━━━━━ */
:root {
    --ink:        #04060f;
    --ink-2:      #090d1a;
    --surface:    rgba(255,255,255,0.035);
    --surface-2:  rgba(255,255,255,0.07);
    --border:     rgba(255,255,255,0.07);
    --border-lit: rgba(99,179,237,0.35);

    --violet:  #7c3aed;
    --indigo:  #4f46e5;
    --cyan:    #06b6d4;
    --teal:    #14b8a6;
    --rose:    #f43f5e;
    --amber:   #f59e0b;
    --lime:    #84cc16;

    --happy:   #f59e0b;
    --sad:     #38bdf8;
    --anger:   #ef4444;
    --fear:    #8b5cf6;
    --trust:   #10b981;

    --txt:     #e8eaf6;
    --txt-2:   rgba(232,234,246,0.55);
    --txt-3:   rgba(232,234,246,0.28);

    --glow-v:  0 0 60px rgba(124,58,237,0.35);
    --glow-c:  0 0 60px rgba(6,182,212,0.3);

    --r-sm: 10px;
    --r-md: 16px;
    --r-lg: 24px;
    --r-xl: 32px;
}

/* ━━━━━━━━━━━━━━ ANIMATED CANVAS BACKGROUND ━━━━━━━━━━━━━━ */
.stApp {
    background: var(--ink) !important;
    color: var(--txt) !important;
    font-family: 'Outfit', sans-serif;
    overflow-x: hidden;
}

/* Deep space gradient base */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(ellipse 100vw 80vh at -10% -5%,  rgba(79,70,229,0.22) 0%, transparent 55%),
        radial-gradient(ellipse 80vw  70vh at 110% 15%,  rgba(6,182,212,0.18)  0%, transparent 55%),
        radial-gradient(ellipse 70vw  60vh at 50%  110%, rgba(124,58,237,0.2)  0%, transparent 55%),
        radial-gradient(ellipse 50vw  40vh at 20%  60%,  rgba(244,63,94,0.08)  0%, transparent 55%),
        radial-gradient(ellipse 60vw  50vh at 80%  80%,  rgba(20,184,166,0.1)  0%, transparent 55%);
    animation: bgShift 25s ease-in-out infinite alternate;
    pointer-events: none;
}

@keyframes bgShift {
    0%   { transform: scale(1)    translate(0,0);       filter: hue-rotate(0deg);   }
    25%  { transform: scale(1.03) translate(2%,-1%);    filter: hue-rotate(8deg);   }
    50%  { transform: scale(0.98) translate(-1%, 2%);   filter: hue-rotate(-5deg);  }
    75%  { transform: scale(1.02) translate(1.5%, 1%);  filter: hue-rotate(12deg);  }
    100% { transform: scale(1.01) translate(-2%, -2%);  filter: hue-rotate(-8deg);  }
}

/* Animated grid lines */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: 0;
    background-image:
        linear-gradient(rgba(99,102,241,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,102,241,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
    animation: gridMove 40s linear infinite;
    pointer-events: none;
}

@keyframes gridMove {
    0%   { background-position: 0 0; }
    100% { background-position: 60px 60px; }
}

/* ━━━━━━━━━━━━━━ STAR PARTICLES ━━━━━━━━━━━━━━ */
#star-layer {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
}
.star {
    position: absolute;
    border-radius: 50%;
    background: white;
    animation: starPulse var(--dur, 4s) ease-in-out infinite var(--delay, 0s) alternate;
}
@keyframes starPulse {
    from { opacity: var(--min-op, 0.1); transform: scale(1); }
    to   { opacity: var(--max-op, 0.7); transform: scale(1.5); }
}

/* ━━━━━━━━━━━━━━ FLOATING ORBS ━━━━━━━━━━━━━━ */
.orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    z-index: 0;
    pointer-events: none;
    animation: orbFloat var(--dur2) ease-in-out infinite alternate;
    opacity: 0.15;
}
@keyframes orbFloat {
    0%   { transform: translate(0, 0)   scale(1); }
    100% { transform: translate(var(--tx, 40px), var(--ty, -30px)) scale(1.1); }
}

/* ━━━━━━━━━━━━━━ Z-INDEX LAYERING ━━━━━━━━━━━━━━ */
section[data-testid="stSidebar"],
.main .block-container { position: relative; z-index: 1; }

/* ━━━━━━━━━━━━━━ MAIN CONTAINER ━━━━━━━━━━━━━━ */
.main .block-container {
    max-width: 1280px;
    padding: 1.5rem 2.5rem 3rem;
}

/* ━━━━━━━━━━━━━━ SIDEBAR ━━━━━━━━━━━━━━ */
section[data-testid="stSidebar"] {
    background: rgba(4,6,15,0.92) !important;
    backdrop-filter: blur(32px) saturate(150%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--txt) !important; }
section[data-testid="stSidebar"] .stMetric {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    padding: 0.8rem 1rem !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--txt-3) !important;
}
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}

/* ━━━━━━━━━━━━━━ TYPOGRAPHY ━━━━━━━━━━━━━━ */
h1, h2, h3 {
    font-family: 'Outfit', sans-serif !important;
    letter-spacing: -0.03em;
    color: var(--txt) !important;
}

/* ━━━━━━━━━━━━━━ HERO HEADER ━━━━━━━━━━━━━━ */
.hero {
    position: relative;
    padding: 3rem 0 2rem;
    overflow: visible;
}
.hero-eyebrow {
    font-family: 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 0.6rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 28px; height: 2px;
    background: var(--cyan);
    border-radius: 1px;
}
.hero-title {
    font-family: 'Outfit', sans-serif;
    font-size: clamp(2.4rem, 5vw, 4.2rem);
    font-weight: 900;
    line-height: 1.0;
    letter-spacing: -0.04em;
    margin: 0 0 1rem;
    background: linear-gradient(135deg,
        #e0e7ff 0%, #c7d2fe 20%, #a5f3fc 45%, #6ee7b7 65%, #fde68a 85%, #fca5a5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 300% 300%;
    animation: titleGrad 8s ease infinite;
}
@keyframes titleGrad {
    0%, 100% { background-position: 0% 50%;   }
    50%       { background-position: 100% 50%; }
}
.hero-sub {
    font-size: 1rem;
    color: var(--txt-2);
    font-weight: 300;
    letter-spacing: 0.03em;
    max-width: 560px;
    line-height: 1.65;
}
.hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.2rem;
}
.hero-tag {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.28rem 0.8rem;
    border-radius: 100px;
    border: 1px solid;
    backdrop-filter: blur(8px);
    transition: all 0.25s ease;
}
.hero-tag:hover { transform: translateY(-2px); }
.ht-nlp  { background: rgba(124,58,237,0.12); border-color: rgba(124,58,237,0.4); color:#c4b5fd; }
.ht-ml   { background: rgba(6,182,212,0.12);  border-color: rgba(6,182,212,0.4);  color:#67e8f9; }
.ht-spot { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.4); color:#6ee7b7; }
.ht-py   { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.4); color:#fde68a; }
.ht-ai   { background: rgba(244,63,94,0.12);  border-color: rgba(244,63,94,0.4);  color:#fda4af; }

/* ━━━━━━━━━━━━━━ GLASS CARDS ━━━━━━━━━━━━━━ */
.gc {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1.4rem 1.6rem;
    backdrop-filter: blur(20px) saturate(120%);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
.gc::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.12), transparent);
}
.gc:hover {
    background: var(--surface-2);
    border-color: rgba(99,179,237,0.2);
    transform: translateY(-3px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), var(--glow-v);
}

/* ━━━━━━━━━━━━━━ KPIS ━━━━━━━━━━━━━━ */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
}
.kpi {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1.3rem 1.4rem 1.1rem;
    backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
}
.kpi::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0; height: 2px;
    background: var(--accent-bar, linear-gradient(90deg,#7c3aed,#06b6d4));
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.4s ease;
}
.kpi:hover::after  { transform: scaleX(1); }
.kpi:hover {
    background: var(--surface-2);
    transform: translateY(-4px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.35);
}
.kpi-icon  { font-size: 1.6rem; margin-bottom: 0.5rem; }
.kpi-val {
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--txt);
    line-height: 1;
    margin-bottom: 0.2rem;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--txt-3);
}

/* ━━━━━━━━━━━━━━ SECTION TITLES ━━━━━━━━━━━━━━ */
.sec-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: var(--txt);
    margin: 2.5rem 0 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    letter-spacing: -0.02em;
}
.sec-title .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 12px var(--cyan);
    flex-shrink: 0;
    animation: dotBlink 2s ease-in-out infinite alternate;
}
@keyframes dotBlink {
    from { box-shadow: 0 0 8px var(--cyan); opacity:1; }
    to   { box-shadow: 0 0 20px var(--cyan); opacity:0.6; }
}
.sec-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(99,179,237,0.25), transparent);
    margin-left: 0.3rem;
}

/* ━━━━━━━━━━━━━━ EMOTION PILLS ━━━━━━━━━━━━━━ */
.pill-row { display: flex; flex-wrap: wrap; gap: 0.75rem; margin: 1rem 0; }
.pill {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.5rem 1.15rem;
    border-radius: 100px;
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 0.82rem;
    letter-spacing: 0.04em;
    border: 1px solid transparent;
    cursor: default;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.pill::before {
    content: '';
    position: absolute;
    inset: 0;
    background: inherit;
    filter: blur(12px);
    opacity: 0;
    transition: opacity 0.3s;
    z-index: -1;
}
.pill:hover { transform: scale(1.07) translateY(-2px); }
.pill:hover::before { opacity: 0.6; }
.pill-count {
    font-size: 0.68rem;
    padding: 0.1rem 0.45rem;
    border-radius: 100px;
    background: rgba(255,255,255,0.12);
}
.p-happy { background:rgba(245,158,11,0.12); border-color:rgba(245,158,11,0.45); color:#fde68a; }
.p-sad   { background:rgba(56,189,248,0.12); border-color:rgba(56,189,248,0.45); color:#7dd3fc; }
.p-anger { background:rgba(239,68,68,0.12);  border-color:rgba(239,68,68,0.45);  color:#fca5a5; }
.p-fear  { background:rgba(139,92,246,0.12); border-color:rgba(139,92,246,0.45); color:#c4b5fd; }
.p-trust { background:rgba(16,185,129,0.12); border-color:rgba(16,185,129,0.45); color:#6ee7b7; }

/* ━━━━━━━━━━━━━━ SONG CARDS ━━━━━━━━━━━━━━ */
.song-list { display: flex; flex-direction: column; gap: 0.6rem; }
.song-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.9rem 1.1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-sm);
    backdrop-filter: blur(12px);
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    animation: songSlide 0.4s ease backwards;
    position: relative;
    overflow: hidden;
}
.song-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    background: var(--emotion-color, var(--violet));
    transform: scaleY(0);
    transform-origin: bottom;
    transition: transform 0.3s ease;
}
.song-card:hover::before { transform: scaleY(1); }
.song-card:hover {
    background: var(--surface-2);
    border-color: rgba(99,179,237,0.25);
    transform: translateX(6px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}
@keyframes songSlide {
    from { opacity:0; transform:translateX(-20px); }
    to   { opacity:1; transform:translateX(0); }
}
.song-num {
    width: 34px; height: 34px;
    border-radius: 8px;
    background: linear-gradient(135deg, var(--violet), var(--cyan));
    display: flex; align-items: center; justify-content: center;
    font-family: 'Outfit', sans-serif;
    font-size: 0.82rem; font-weight: 800;
    color: white; flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(124,58,237,0.3);
}
.song-info { flex: 1; min-width: 0; }
.song-name { font-weight: 600; font-size: 0.92rem; color: var(--txt); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.song-artist { font-size: 0.78rem; color: var(--txt-3); margin-top: 2px; }
.song-btns { display: flex; gap: 0.4rem; flex-shrink: 0; }
.song-btn {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.03em;
    padding: 0.28rem 0.7rem; border-radius: 100px; text-decoration: none;
    border: 1px solid; transition: all 0.2s ease; white-space: nowrap;
}
.song-btn:hover { transform: translateY(-2px); }
.sb-yt  { background:rgba(239,68,68,0.1);   border-color:rgba(239,68,68,0.35);  color:#fca5a5; }
.sb-yt:hover  { background:rgba(239,68,68,0.2);  }
.sb-sp  { background:rgba(16,185,129,0.1);  border-color:rgba(16,185,129,0.35); color:#6ee7b7; }
.sb-sp:hover  { background:rgba(16,185,129,0.2); }

/* ━━━━━━━━━━━━━━ DETECTED EMOTION BADGE ━━━━━━━━━━━━━━ */
.emotion-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.75rem 1.8rem;
    border-radius: 100px;
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    margin: 0.8rem 0;
    position: relative;
    overflow: hidden;
    animation: badgePop 0.5s cubic-bezier(0.34,1.56,0.64,1) backwards;
}
.emotion-badge::before {
    content: '';
    position: absolute;
    inset: 0;
    background: inherit;
    filter: blur(20px) opacity(0.6);
    z-index: -1;
    animation: glowPulse 2s ease-in-out infinite alternate;
}
@keyframes badgePop {
    from { opacity:0; transform:scale(0.7) translateY(10px); }
    to   { opacity:1; transform:scale(1) translateY(0); }
}
@keyframes glowPulse {
    from { opacity: 0.4; }
    to   { opacity: 0.9; }
}
.eb-happy{ background:rgba(245,158,11,0.18); border:1px solid rgba(245,158,11,0.6); color:#fde68a; box-shadow:0 0 30px rgba(245,158,11,0.2); }
.eb-sad  { background:rgba(56,189,248,0.18); border:1px solid rgba(56,189,248,0.6); color:#7dd3fc; box-shadow:0 0 30px rgba(56,189,248,0.2); }
.eb-anger{ background:rgba(239,68,68,0.18);  border:1px solid rgba(239,68,68,0.6);  color:#fca5a5; box-shadow:0 0 30px rgba(239,68,68,0.2); }
.eb-fear { background:rgba(139,92,246,0.18); border:1px solid rgba(139,92,246,0.6); color:#c4b5fd; box-shadow:0 0 30px rgba(139,92,246,0.2); }
.eb-trust{ background:rgba(16,185,129,0.18); border:1px solid rgba(16,185,129,0.6); color:#6ee7b7; box-shadow:0 0 30px rgba(16,185,129,0.2); }

/* ━━━━━━━━━━━━━━ CONFIDENCE BAR ━━━━━━━━━━━━━━ */
.conf-bar-wrap { margin: 1rem 0; }
.conf-label { display:flex; justify-content:space-between; margin-bottom:0.35rem; font-size:0.8rem; color:var(--txt-2); }
.conf-track {
    height: 7px; border-radius: 100px;
    background: rgba(255,255,255,0.06);
    overflow: hidden;
}
.conf-fill {
    height: 100%; border-radius: 100px;
    background: linear-gradient(90deg, var(--violet), var(--cyan));
    transition: width 1s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 0 12px rgba(6,182,212,0.4);
    animation: barGrow 1s cubic-bezier(0.4,0,0.2,1) backwards;
}
@keyframes barGrow { from { width: 0 !important; } }

/* ━━━━━━━━━━━━━━ PIPELINE STEPS ━━━━━━━━━━━━━━ */
.pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    margin: 1.5rem 0;
    overflow-x: auto;
    padding-bottom: 0.5rem;
}
.pipe-step {
    flex-shrink: 0;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1rem 1.3rem;
    text-align: center;
    min-width: 120px;
    transition: all 0.25s ease;
    position: relative;
}
.pipe-step:hover {
    background: var(--surface-2);
    border-color: var(--border-lit);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}
.pipe-step .ps-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.pipe-step .ps-name {
    font-family: 'Outfit', sans-serif;
    font-size: 0.78rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--txt-2);
}
.pipe-step .ps-tech {
    font-size: 0.68rem;
    color: var(--txt-3);
    margin-top: 2px;
}
.pipe-arrow {
    flex-shrink: 0;
    width: 40px;
    text-align: center;
    color: var(--txt-3);
    font-size: 1.1rem;
    position: relative;
}
.pipe-arrow::after {
    content: '';
    display: block;
    width: 100%; height: 1px;
    background: linear-gradient(90deg, rgba(99,179,237,0.3), rgba(99,179,237,0.1));
}

/* ━━━━━━━━━━━━━━ INFO PANELS ━━━━━━━━━━━━━━ */
.info-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-md);
    padding: 1.3rem 1.5rem;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.info-panel .ip-accent {
    position: absolute;
    top: 0; left: 0; bottom: 0; width: 3px;
    background: var(--accent, var(--cyan));
    border-radius: 3px 0 0 3px;
}
.info-panel h4 {
    font-family: 'Outfit', sans-serif;
    font-size: 0.88rem; font-weight: 700;
    letter-spacing: 0.04em; text-transform: uppercase;
    color: var(--txt-2); margin: 0 0 0.8rem 0;
}
.info-panel ul { margin: 0; padding-left: 1.2rem; }
.info-panel li { font-size: 0.85rem; color: var(--txt-2); line-height: 1.9; }
.info-panel li strong { color: var(--txt); }

/* ━━━━━━━━━━━━━━ TECH STACK GRID ━━━━━━━━━━━━━━ */
.tech-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.9rem;
    margin: 1rem 0;
}
.tech-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--r-sm);
    padding: 1rem;
    text-align: center;
    transition: all 0.25s ease;
    cursor: default;
}
.tech-card:hover {
    background: var(--surface-2);
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    border-color: var(--border-lit);
}
.tech-card .tc-icon { font-size: 2rem; margin-bottom: 0.4rem; }
.tech-card .tc-name {
    font-family: 'Outfit', sans-serif;
    font-size: 0.82rem; font-weight: 700;
    color: var(--txt); letter-spacing: 0.03em;
}
.tech-card .tc-role {
    font-size: 0.7rem; color: var(--txt-3); margin-top: 2px;
}

/* ━━━━━━━━━━━━━━ HISTORY LOG ━━━━━━━━━━━━━━ */
.history-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.75rem 1rem;
    border-radius: var(--r-sm);
    background: var(--surface);
    border: 1px solid var(--border);
    margin-bottom: 0.5rem;
    transition: all 0.2s ease;
    animation: histFade 0.3s ease backwards;
}
.history-item:hover {
    background: var(--surface-2);
    transform: translateX(4px);
}
@keyframes histFade {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
}
.hi-dot {
    width: 8px; height: 8px; border-radius: 50%;
    flex-shrink: 0;
}
.hi-text { flex: 1; font-size: 0.84rem; color: var(--txt-2); }
.hi-em { font-size: 0.72rem; font-weight: 700; letter-spacing: 0.06em; text-transform: uppercase; }
.hi-time { font-size: 0.68rem; color: var(--txt-3); }

/* ━━━━━━━━━━━━━━ WAVEFORM VISUAL ━━━━━━━━━━━━━━ */
.waveform {
    display: flex;
    align-items: center;
    gap: 3px;
    height: 36px;
    margin: 0.5rem 0;
}
.wave-bar {
    width: 4px;
    border-radius: 2px;
    background: linear-gradient(to top, var(--violet), var(--cyan));
    animation: waveDance var(--dur3, 0.8s) ease-in-out infinite alternate;
    animation-delay: var(--delay2, 0s);
    opacity: 0.7;
}
@keyframes waveDance {
    from { height: 4px;  opacity: 0.4; }
    to   { height: var(--peak, 28px); opacity: 1; }
}

/* ━━━━━━━━━━━━━━ INPUT OVERRIDES ━━━━━━━━━━━━━━ */
.stTextArea textarea {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--txt) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.95rem !important;
    resize: none !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
.stTextArea textarea:focus {
    border-color: rgba(124,58,237,0.5) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12),
                0 0 40px rgba(124,58,237,0.08) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: var(--txt-3) !important; }

/* ━━━━━━━━━━━━━━ BUTTON OVERRIDES ━━━━━━━━━━━━━━ */
.stButton > button {
    background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(6,182,212,0.15)) !important;
    border: 1px solid rgba(124,58,237,0.35) !important;
    color: var(--txt) !important;
    border-radius: var(--r-sm) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    font-size: 0.85rem !important;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1) !important;
    backdrop-filter: blur(8px) !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.08));
    opacity: 0;
    transition: opacity 0.25s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, rgba(124,58,237,0.4), rgba(6,182,212,0.3)) !important;
    border-color: rgba(124,58,237,0.7) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.25), 0 0 0 1px rgba(124,58,237,0.2) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ━━━━━━━━━━━━━━ METRIC OVERRIDES ━━━━━━━━━━━━━━ */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-md) !important;
    padding: 1.1rem 1.3rem !important;
    backdrop-filter: blur(12px) !important;
    transition: all 0.25s ease !important;
}
[data-testid="stMetric"]:hover {
    background: var(--surface-2) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important; letter-spacing: 0.1em !important;
    text-transform: uppercase !important; color: var(--txt-3) !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.9rem !important; font-weight: 800 !important;
    color: var(--txt) !important;
}

/* ━━━━━━━━━━━━━━ DATAFRAME OVERRIDE ━━━━━━━━━━━━━━ */
.stDataFrame { border-radius: var(--r-md) !important; overflow: hidden !important; border: 1px solid var(--border) !important; }

/* ━━━━━━━━━━━━━━ EXPANDER OVERRIDES ━━━━━━━━━━━━━━ */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r-sm) !important;
    color: var(--txt) !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
    color: var(--txt) !important;
}

/* ━━━━━━━━━━━━━━ RADIO OVERRIDE ━━━━━━━━━━━━━━ */
.stRadio label span { color: var(--txt) !important; font-size: 0.88rem !important; }
[data-testid="stMarkdownContainer"] p { color: var(--txt-2) !important; }

/* ━━━━━━━━━━━━━━ PROGRESS METER ━━━━━━━━━━━━━━ */
.radial-meter {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.3rem;
}
.rm-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--txt-3); }

/* ━━━━━━━━━━━━━━ SPARKLINE ━━━━━━━━━━━━━━ */
.sparkline-row { display: flex; flex-direction: column; gap: 0.5rem; }
.spark-item { display: flex; align-items: center; gap: 0.8rem; }
.spark-name { font-size: 0.8rem; color: var(--txt-2); width: 60px; flex-shrink: 0; }
.spark-track { flex: 1; height: 6px; border-radius: 100px; background: rgba(255,255,255,0.05); overflow: hidden; }
.spark-fill { height: 100%; border-radius: 100px; transition: width 1.2s cubic-bezier(0.4,0,0.2,1); }
.spark-pct { font-size: 0.75rem; font-weight: 700; color: var(--txt-2); width: 36px; text-align: right; }

/* ━━━━━━━━━━━━━━ SCROLLBAR ━━━━━━━━━━━━━━ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124,58,237,0.6); }

/* ━━━━━━━━━━━━━━ FOOTER ━━━━━━━━━━━━━━ */
.footer {
    text-align: center;
    padding: 2.5rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}
.footer-logo {
    font-family: 'Outfit', sans-serif;
    font-size: 1.5rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    background: linear-gradient(90deg, #c4b5fd, #67e8f9, #6ee7b7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.footer-sub { font-size: 0.76rem; color: var(--txt-3); margin-top: 0.3rem; letter-spacing: 0.05em; }

/* ━━━━━━━━━━━━━━ ANIMATION UTILITIES ━━━━━━━━━━━━━━ */
.fade-up { animation: fadeUp 0.5s ease backwards; }
.fade-up-d1 { animation: fadeUp 0.5s 0.1s ease backwards; }
.fade-up-d2 { animation: fadeUp 0.5s 0.2s ease backwards; }
.fade-up-d3 { animation: fadeUp 0.5s 0.3s ease backwards; }
@keyframes fadeUp {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}

/* ━━━━━━━━━━━━━━ TOOLTIP-STYLE BADGES ━━━━━━━━━━━━━━ */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 0.2rem 0.6rem;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge-new { background: rgba(16,185,129,0.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,0.3); }
.badge-hot { background: rgba(239,68,68,0.15);  color: #fca5a5; border: 1px solid rgba(239,68,68,0.3); }

/* ━━━━━━━━━━━━━━ SNAKE ━━━━━━━━━━━━━━ */
.snake-grid {
    display: grid;
    grid-template-columns: repeat(20, 22px);
    gap: 2px;
    background: rgba(0,0,0,0.7);
    border: 1px solid rgba(99,102,241,0.2);
    border-radius: var(--r-md);
    padding: 12px;
    width: fit-content;
    margin: 1.5rem auto;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 60px rgba(124,58,237,0.1), inset 0 0 30px rgba(0,0,0,0.5);
}
.snake-cell { width: 22px; height: 22px; border-radius: 4px; }
.sc-snake { background: linear-gradient(135deg,#4ade80,#22c55e); box-shadow: 0 0 8px rgba(74,222,128,0.5); }
.sc-head  { background: linear-gradient(135deg,#86efac,#4ade80); box-shadow: 0 0 14px rgba(74,222,128,0.8); }
.sc-food  { background: radial-gradient(circle,#fb923c,#ef4444); box-shadow: 0 0 10px rgba(251,146,60,0.8); animation: foodPulse 0.8s ease infinite alternate; }
.sc-empty { background: rgba(255,255,255,0.018); }
@keyframes foodPulse { from { transform:scale(0.85); } to { transform:scale(1.1); } }
</style>

<!-- Starfield + Orbs via JS -->
<script>
(function(){
  // Inject stars
  const layer = document.createElement('div');
  layer.id = 'star-layer';
  document.body.appendChild(layer);
  for(let i=0;i<120;i++){
    const s=document.createElement('div');
    const sz = Math.random()*2+0.5;
    s.className='star';
    s.style.cssText=`
      left:${Math.random()*100}%;top:${Math.random()*100}%;
      width:${sz}px;height:${sz}px;
      --dur:${2+Math.random()*5}s;
      --delay:${-Math.random()*6}s;
      --min-op:${0.05+Math.random()*0.15};
      --max-op:${0.4+Math.random()*0.5};
    `;
    layer.appendChild(s);
  }
  // Inject orbs
  const orbs=[
    {w:500,h:500,t:'-10%',l:'-5%',c:'124,58,237', dur:'18s', tx:'60px',ty:'-40px'},
    {w:400,h:400,t:'60%',l:'80%',c:'6,182,212',   dur:'22s', tx:'-50px',ty:'30px'},
    {w:350,h:350,t:'40%',l:'30%',c:'16,185,129',  dur:'15s', tx:'40px',ty:'50px'},
    {w:300,h:300,t:'80%',l:'10%',c:'244,63,94',   dur:'20s', tx:'-30px',ty:'-60px'},
  ];
  orbs.forEach(o=>{
    const el=document.createElement('div');
    el.className='orb';
    el.style.cssText=`width:${o.w}px;height:${o.h}px;top:${o.t};left:${o.l};
      background:rgba(${o.c},0.35);--dur2:${o.dur};--tx:${o.tx};--ty:${o.ty};`;
    document.body.appendChild(el);
  });
})();
</script>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════

EMOTION_UI = {
    'happy': {'icon':'😊','pill':'p-happy','badge':'eb-happy','color':'#f59e0b','hex':'245,158,11'},
    'sad':   {'icon':'😢','pill':'p-sad',  'badge':'eb-sad',  'color':'#38bdf8','hex':'56,189,248'},
    'anger': {'icon':'😤','pill':'p-anger','badge':'eb-anger','color':'#ef4444','hex':'239,68,68'},
    'fear':  {'icon':'😨','pill':'p-fear', 'badge':'eb-fear', 'color':'#8b5cf6','hex':'139,92,246'},
    'trust': {'icon':'🤝','pill':'p-trust','badge':'eb-trust','color':'#10b981','hex':'16,185,129'},
}

PLOTLY_DARK = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#e8eaf6', family='Outfit'),
    xaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.08)'),
    yaxis=dict(gridcolor='rgba(255,255,255,0.05)', zerolinecolor='rgba(255,255,255,0.08)'),
    title_font=dict(family='Outfit', size=15),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#e8eaf6')),
    margin=dict(l=10, r=10, t=40, b=10),
)

COLOR_MAP = {
    'happy':'#f59e0b','sad':'#38bdf8','anger':'#ef4444','fear':'#8b5cf6','trust':'#10b981'
}

def hex_to_rgba(hex_color, alpha=0.4):
    h = str(hex_color).lstrip('#')
    if len(h) == 6:
        r = int(h[0:2], 16)
        g = int(h[2:4], 16)
        b = int(h[4:6], 16)
        return f'rgba({r},{g},{b},{alpha})'
    return hex_color

@st.cache_data(show_spinner=False)
def load_df():
    # Prefer the larger dataset if present
    path_large = os.path.join(DATA_DIR, "dataset_108k.csv")
    path_small = os.path.join(DATA_DIR, "dataset.csv")
    path = path_large if os.path.exists(path_large) else path_small
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    df['text_length'] = df['text'].str.split().apply(len)
    df['char_length'] = df['text'].str.len()
    return df

@st.cache_resource(show_spinner=False)
def get_model():
    try:
        return load_model()
    except Exception:
        return None

def waveform_html(n=22):
    bars = ""
    for i in range(n):
        peak = random.randint(10, 32)
        dur  = round(0.5 + random.random() * 0.8, 2)
        dly  = round(random.random() * 0.5, 2)
        bars += f'<div class="wave-bar" style="--peak:{peak}px;--dur3:{dur}s;--delay2:{dly}s;"></div>'
    return f'<div class="waveform">{bars}</div>'

def sec(icon, label):
    return f'<div class="sec-title"><span class="dot"></span>{icon} {label}</div>'

def pill_html(emotion, label, count=None):
    ui = EMOTION_UI.get(emotion, EMOTION_UI['trust'])
    cnt = f'<span class="pill-count">{count:,}</span>' if count else ''
    return f'<div class="pill {ui["pill"]}">{ui["icon"]} {label}{cnt}</div>'


def compute_dataset_metrics(sample_size=5000):
    """Return dataset-derived metrics: samples, unique emotions, avg words, accuracy estimate."""
    df = load_df()
    metrics = {
        'samples': 0,
        'unique_emotions': 0,
        'avg_words': 0.0,
        'avg_chars': 0.0,
        'total_words': 0,
        'unique_texts': 0,
        'accuracy': None,
        'model_size_bytes': None,
        'model_trained_at': None,
    }
    if df is None:
        return metrics

    metrics['samples'] = len(df)
    metrics['unique_emotions'] = int(df['emotion'].nunique())
    metrics['avg_words'] = float(df['text_length'].mean())
    metrics['total_words'] = int(df['text_length'].sum())
    metrics['unique_texts'] = int(df['text'].nunique())
    metrics['avg_chars'] = float(df['char_length'].mean())

    # Try to compute a lightweight accuracy estimate using the loaded model
    try:
        model = get_model()
        if model is not None and len(df) > 0:
            # model file info (if available)
            try:
                if MODEL_PATH and os.path.exists(MODEL_PATH):
                    metrics['model_size_bytes'] = os.path.getsize(MODEL_PATH)
                    metrics['model_trained_at'] = os.path.getmtime(MODEL_PATH)
            except Exception:
                pass

            n = min(sample_size, len(df))
            sample = df.sample(n=n, random_state=0)
            from preprocess import preprocess_batch
            X = preprocess_batch(sample['text'].tolist())
            y_true = sample['emotion'].str.strip().str.lower().tolist()
            try:
                y_pred = model.predict(X)
                from sklearn.metrics import accuracy_score
                metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
            except Exception:
                metrics['accuracy'] = None
    except Exception:
        metrics['accuracy'] = None

    return metrics

# Optional override when the model/dataset has changed — set dashboard KPI defaults here
# Use these to force the displayed values without changing the underlying dataset.
OVERRIDE_METRICS = {
    'samples': None,
    'unique_emotions': None,
    'avg_words': None,
    # accuracy as a fraction (e.g. 0.767 -> 76.7%)
    'accuracy': None,
}

def song_card_html(i, song, emotion_color):
    name   = song.get("name",   "Unknown Track")
    artist = song.get("artist", "Unknown Artist")
    yt_url = f"https://www.youtube.com/results?search_query={name.replace(' ','+')}+{artist.replace(' ','+')}"
    sp_url = song.get("url","")
    sp_btn = f'<a href="{sp_url}" target="_blank" class="song-btn sb-sp">♫ Spotify</a>' if sp_url else ''
    return f"""
    <div class="song-card" style="--emotion-color:{emotion_color};animation-delay:{(i-1)*0.07}s">
        <div class="song-num">{i}</div>
        <div class="song-info">
            <div class="song-name">{name}</div>
            <div class="song-artist">{artist}</div>
        </div>
        <div class="song-btns">
            <a href="{yt_url}" target="_blank" class="song-btn sb-yt">▶ YouTube</a>
            {sp_btn}
        </div>
    </div>"""


# ════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding:0.8rem 0 1.2rem;">
        <div style="font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:900;
                    letter-spacing:-0.04em;background:linear-gradient(135deg,#c4b5fd,#67e8f9,#6ee7b7);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
             EmotionWave
        </div>
        <div style="font-size:0.72rem;letter-spacing:0.14em;text-transform:uppercase;
                    color:rgba(232,234,246,0.35);margin-top:2px;">
            Music Recommender Dashboard
        </div>
    </div>
    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.07);margin:0.5rem 0 1rem;"/>
    """, unsafe_allow_html=True)

    pages = {
        " Overview":           "Home · Stats · Quick glance",
        " Recommender":        "Test the AI in real-time",
        " Dataset Explorer":   "Deep-dive the training data",
        " Model Architecture": "How the ML pipeline works",
        " Analytics":          "Charts, trends, insights",
        " Snake Game":         "Take a fun break",
    }
    page = st.radio("", list(pages.keys()), label_visibility="collapsed")

    st.markdown(f"""
    <div style="background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.18);
                border-radius:8px;padding:0.6rem 0.85rem;font-size:0.8rem;
                color:rgba(232,234,246,0.5);line-height:1.5;margin-top:0.4rem;">
        {pages[page]}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:1rem 0;'/>", unsafe_allow_html=True)

    df_s = load_df()
    metrics = compute_dataset_metrics()
    if df_s is not None:
        st.markdown("<p style='font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:rgba(232,234,246,0.3);margin-bottom:0.6rem;'>Live Stats</p>", unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1: st.metric("Samples", f"{len(df_s):,}")
        with c2: st.metric("Emotions", df_s['emotion'].nunique())

    st.markdown("""
    <hr style='border:none;border-top:1px solid rgba(255,255,255,0.07);margin:1rem 0;'/>
    <div style="font-size:0.7rem;color:rgba(232,234,246,0.2);text-align:center;letter-spacing:0.06em;">
        NLP · ML · Spotify · Python
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# HERO — shown on every page
# ════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="hero fade-up">
    <!-- Hero eyebrow removed per user request -->
    <h1 class="hero-title">Emotion-Based<br/>Music Recommender</h1>
    <p class="hero-sub">
        Detects your emotion from plain text using NLP + Machine Learning,
        then curates a Spotify playlist that matches exactly how you feel.
    </p>
    <div class="hero-tags">
        <span class="hero-tag ht-nlp">NLP</span>
        <span class="hero-tag ht-ml">Machine Learning</span>
        <span class="hero-tag ht-spot">Spotify API</span>
        <span class="hero-tag ht-py">Python</span>
        <span class="hero-tag ht-ai">Emotion AI</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:0.5rem 0 1.5rem;'/>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ════════════════════════════════════════════════════════════
if "Overview" in page:
    df = load_df()
    model = get_model()
    # KPI grid (enhanced)
    metrics = compute_dataset_metrics()
    samples_val = f"{metrics['samples']:,}" if metrics['samples'] else "0"
    emotions_val = f"{metrics['unique_emotions']}" if metrics['unique_emotions'] else "0"
    avg_words_val = f"{metrics['avg_words']:.1f}" if metrics['avg_words'] else "0.0"
    avg_chars_val = f"{metrics['avg_chars']:.1f}" if metrics.get('avg_chars') else "0.0"
    if metrics.get('accuracy') is not None:
        acc_val = f"{metrics['accuracy']*100:.1f}%"
    else:
        acc_val = "N/A"

    st.markdown(f"""
    <div class="kpi-grid fade-up-d1">
        <div class="kpi" style="--accent-bar:linear-gradient(90deg,#7c3aed,#4f46e5)">
            <div class="kpi-icon">🗂️</div>
            <div class="kpi-val">{samples_val}</div>
            <div class="kpi-label">Total Samples</div>
        </div>
        <div class="kpi" style="--accent-bar:linear-gradient(90deg,#06b6d4,#14b8a6)">
            <div class="kpi-val">{emotions_val}</div>
            <div class="kpi-label">Emotions</div>
        </div>
        <div class="kpi" style="--accent-bar:linear-gradient(90deg,#f59e0b,#ef4444)">
            <div class="kpi-val">{avg_words_val}</div>
            <div class="kpi-label">Avg Words</div>
        </div>
        <div class="kpi" style="--accent-bar:linear-gradient(90deg,#10b981,#84cc16)">
            <div class="kpi-val">{avg_chars_val}</div>
            <div class="kpi-label">Avg Chars</div>
        </div>
        <div class="kpi" style="--accent-bar:linear-gradient(90deg,#f43f5e,#f59e0b)">
            <div class="kpi-val">{acc_val}</div>
            <div class="kpi-label">Model Accuracy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Emotion pills with counts
    if df is not None:
        st.markdown(sec("🎭","Emotion Categories"), unsafe_allow_html=True)
        counts = df['emotion'].value_counts()
        pills = '<div class="pill-row">'
        for em, ui in EMOTION_UI.items():
            label = EMOTION_META.get(em,{}).get("label", em.title())
            cnt   = counts.get(em, 0)
            pills += pill_html(em, label, cnt)
        pills += '</div>'
        st.markdown(pills, unsafe_allow_html=True)

    # (Removed) Live Audio Visualizer (Demo)

    if df is not None:
        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown(sec("📊","Distribution"), unsafe_allow_html=True)
            ec = df['emotion'].value_counts().reset_index()
            ec.columns = ['emotion','count']
            fig = px.donut = go.Figure(data=[go.Pie(
                labels=ec['emotion'], values=ec['count'],
                hole=0.52,
                marker=dict(colors=[COLOR_MAP[e] for e in ec['emotion']],
                            line=dict(color='rgba(0,0,0,0.3)', width=2)),
                textfont=dict(family='Outfit', size=12, color='white'),
            )])
            fig.update_layout(**PLOTLY_DARK, title="Emotion Share")
            fig.update_layout(showlegend=True, legend=dict(
                orientation='h', y=-0.12,
                font=dict(color='rgba(232,234,246,0.7)', size=11)
            ))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown(sec("📏","Emotion Bars"), unsafe_allow_html=True)
            fig2 = px.bar(
                ec, x='emotion', y='count', color='emotion',
                color_discrete_map=COLOR_MAP,
                title="Sample Count per Emotion",
                text='count',
            )
            fig2.update_traces(textposition='outside',
                               textfont=dict(size=11, color='rgba(232,234,246,0.8)'),
                               marker_line_color='rgba(0,0,0,0.3)', marker_line_width=1)
            layout = PLOTLY_DARK.copy()
            layout.update(dict(
                showlegend=False,
                bargap=0.3,
                xaxis=dict(title='', tickfont=dict(size=12)),
                yaxis=dict(title=''),
            ))
            fig2.update_layout(**layout)
            st.plotly_chart(fig2, use_container_width=True)

    # Project intro cards
    st.markdown(sec("🚀","What This Project Does"), unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col,(icon,title,desc) in zip([c1,c2,c3],[
        ("🧠","Emotion Detection","Classifies free-text emotion into 5 categories using TF-IDF features and a Multinomial Naive Bayes classifier trained on 100k+ samples."),
        ("🎵","Music Mapping","Maps the detected emotion to a tailored Spotify search query, returning 5 recommended tracks with artist info and direct links."),
        ("📊","Data Analytics","Explore the training dataset, visualise emotion distributions, analyse text length patterns, and inspect model performance metrics."),
    ]):
        with col:
            st.markdown(f"""
            <div class="gc fade-up-d2" style="text-align:center;padding:1.6rem 1.2rem;">
                <div style="font-size:2.2rem;margin-bottom:0.7rem;">{icon}</div>
                <div style="font-family:'Outfit',sans-serif;font-size:0.95rem;font-weight:700;
                            color:var(--txt);margin-bottom:0.5rem;">{title}</div>
                <div style="font-size:0.82rem;color:var(--txt-3);line-height:1.65;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE 2 — RECOMMENDER
# ════════════════════════════════════════════════════════════
elif "Recommender" in page:
    model = get_model()

    if 'history' not in st.session_state: st.session_state.history = []
    if 'result'  not in st.session_state: st.session_state.result  = None

    col_main, col_hist = st.columns([3, 2], gap="large")

    with col_main:
        st.markdown(sec("🎙","Describe Your Emotion"), unsafe_allow_html=True)

        if model is None:
            st.error("Model not found — run `python src/model.py` first.")
        else:
            metrics = compute_dataset_metrics()
            samples_val = f"{metrics['samples']:,}" if metrics['samples'] else "0"
            emotions_val = f"{metrics['unique_emotions']}" if metrics['unique_emotions'] else "0"
            avg_words_val = f"{metrics['avg_words']:.1f}" if metrics['avg_words'] else "0.0"
            if metrics.get('accuracy') is not None:
                model_status_val = f"{metrics['accuracy']*100:.1f}%"
            else:
                model_status_val = "Ready ✓" if model is not None else "Loading"



            if "emotion_text" not in st.session_state: 
                st.session_state.emotion_text = ""

            user_text = st.text_area(
                "How are you feeling right now?",
                placeholder='Type your emotion, then click Generate... (e.g. "happy", "anxious", "I feel unstoppable")',
                height=120,
                label_visibility="collapsed",
                key="emotion_text",
                value=st.session_state.emotion_text,
            )


            # Generate button
            if st.button("✨ Generate Recommendations", use_container_width=True, disabled=not st.session_state.emotion_text.strip()):
                with st.spinner("Analyzing emotion and generating playlist..."):
                    model = get_model()
                    if model:
                        result = get_recommendations(st.session_state.emotion_text, model=model)
                        st.session_state.result = result
                        if result and result.get('emotion'):
                            st.session_state.history.insert(0, {
                                'text': st.session_state.emotion_text[:55] + ('...' if len(st.session_state.emotion_text) > 55 else ''),
                                'emotion': result['emotion'],
                                'time': datetime.now().strftime("%H:%M")
                            })
                            st.session_state.history = st.session_state.history[:12]
                        st.rerun()

            # Show results if available
            if st.session_state.result:
                r = st.session_state.result
                em = r.get('emotion', '')
                meta = EMOTION_META.get(em, {})
                ui = EMOTION_UI.get(em, EMOTION_UI['trust'])
                lbl = meta.get('label', em.title())

                st.markdown(f"""
                <div class="fade-up" style="margin:1.2rem 0;">
                    <p style="font-size:0.7rem;letter-spacing:0.14em;text-transform:uppercase;
                              color:rgba(232,234,246,0.35);margin-bottom:0.4rem;">Detected Emotion</p>
                    <div class="emotion-badge {ui['badge']}">{ui['icon']} {lbl}</div>
                    <p style="font-size:0.78rem;color:rgba(232,234,246,0.3);margin-top:0.4rem;">
                        Processed: <em>\\"{r.get('cleaned_input','')}\\"</em>
                    </p>
                </div>
                """, unsafe_allow_html=True)


                # Confidence-style bars — use model probabilities when available
                st.markdown('<div class="conf-bar-wrap">', unsafe_allow_html=True)

                cleaned_input = r.get('cleaned_input', '').strip().lower()
                # If user input exactly matches an emotion keyword, force 100/0 display
                force_one_hot = False
                if cleaned_input:
                    tokens = cleaned_input.split()
                    if len(tokens) == 1 and tokens[0] in EMOTION_UI:
                        force_one_hot = True
                        forced = tokens[0]

                probs_map = {}
                if not force_one_hot and model is not None:
                    try:
                        if hasattr(model, 'predict_proba'):
                            classes = [str(c).strip().lower() for c in model.classes_]
                            proba = model.predict_proba([cleaned_input])[0]
                            for cls, p in zip(classes, proba):
                                probs_map[cls] = float(p)
                    except Exception:
                        probs_map = {}

                scores = {}
                if force_one_hot:
                    for emo2 in EMOTION_UI:
                        scores[emo2] = 100 if emo2 == forced else 0
                elif probs_map:
                    # Map probabilities to EMOTION_UI keys (ensure sum 100)
                    total = 0
                    for emo2 in EMOTION_UI:
                        val = int(round(probs_map.get(emo2, 0.0) * 100))
                        scores[emo2] = val
                        total += val
                    # Adjust rounding error
                    if total != 100:
                        diff = 100 - total
                        # add diff to predicted emotion
                        pred = em if em in scores else max(scores, key=scores.get)
                        scores[pred] = max(0, scores.get(pred, 0) + diff)
                else:
                    # Fallback: keep the detected emotion high and others low
                    for emo2 in EMOTION_UI:
                        scores[emo2] = 100 if emo2 == em else 0

                for emo2, ui2 in EMOTION_UI.items():
                    score = scores.get(emo2, 0)
                    st.markdown(f"""
                    <div style="margin-bottom:0.5rem;">
                        <div class="conf-label">
                            <span>{ui2['icon']} {EMOTION_META.get(emo2,{}).get('label',emo2.title())}</span>
                            <span style="color:{ui2['color']}">{score}%</span>
                        </div>
                        <div class="conf-track">
                            <div class="conf-fill"
                                 style="width:{score}%;
                                        background:linear-gradient(90deg,{ui2['color']},{ui2['color']}88);">
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown(f"<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:1.2rem 0;'/>", unsafe_allow_html=True)
                st.markdown(sec("🎶","Your Playlist"), unsafe_allow_html=True)

                src = r.get('source', '')
                src_lbl = "🟢 Live Spotify API" if src == "spotify_api" else "🟡 Curated Recommendations"
                st.markdown(f"<p style='font-size:0.78rem;color:rgba(232,234,246,0.35);margin-bottom:0.6rem;'>Source: {src_lbl}</p>", unsafe_allow_html=True)

                cards = ""
                for i, s in enumerate(r.get('songs', []), 1):
                    cards += song_card_html(i, s, ui['color'])
                st.markdown(f'<div class="song-list">{cards}</div>', unsafe_allow_html=True)

                st.markdown("<br/>", unsafe_allow_html=True)
                if st.button("🔀  Shuffle New Songs"):
                    with st.spinner(""):
                        st.session_state.result = get_recommendations(r.get('raw_input',''), model=model)
                    st.rerun()
            else:
                st.markdown("""
                    <div class="gc" style="text-align:center;padding:3rem 2rem;margin-top:1rem;">
                        <div style="font-size:3rem;margin-bottom:1rem;opacity:0.6;">🎧</div>
                        <div style="font-family:'Outfit',sans-serif;font-size:1rem;font-weight:600;
                                    color:rgba(232,234,246,0.5);margin-bottom:0.4rem;">
                            Enter your emotion to get started
                        </div>
                        <div style="font-size:0.82rem;color:rgba(232,234,246,0.28);max-width:280px;margin:0 auto;">
                            Try a single word like "happy" or a full sentence about how you feel right now.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    # ── History panel ──
    with col_hist:
        st.markdown(sec("🕒","Session History"), unsafe_allow_html=True)

        if st.session_state.history:
            for i, h in enumerate(st.session_state.history):
                ui = EMOTION_UI.get(h['emotion'], EMOTION_UI['trust'])
                st.markdown(f"""
                <div class="history-item" style="animation-delay:{i*0.05}s">
                    <div class="hi-dot" style="background:{ui['color']};box-shadow:0 0 8px {ui['color']};"></div>
                    <div style="flex:1;min-width:0;">
                        <div class="hi-text" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{h['text']}</div>
                        <div class="hi-em" style="color:{ui['color']};margin-top:2px;">{ui['icon']} {h['emotion']}</div>
                    </div>
                    <div class="hi-time">{h['time']}</div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑  Clear History", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        else:
            st.markdown("""
            <div class="gc" style="text-align:center;padding:2rem;">
                <div style="font-size:1.8rem;opacity:0.4;margin-bottom:0.5rem;">📋</div>
                <div style="font-size:0.82rem;color:rgba(232,234,246,0.3);">Your searches will appear here</div>
            </div>
            """, unsafe_allow_html=True)

        # Emotion frequency from history
        if len(st.session_state.history) > 1:
            st.markdown(sec("📊","Emotion Frequency"), unsafe_allow_html=True)
            freq = Counter(h['emotion'] for h in st.session_state.history)
            total = sum(freq.values())
            sparklines = ""
            for em, ui in EMOTION_UI.items():
                cnt = freq.get(em, 0)
                pct = int(cnt / total * 100) if total else 0
                sparklines += f"""
                <div class="spark-item">
                    <span class="spark-name">{ui['icon']} {em}</span>
                    <div class="spark-track">
                        <div class="spark-fill" style="width:{pct}%;background:{ui['color']};"></div>
                    </div>
                    <span class="spark-pct" style="color:{ui['color']}">{pct}%</span>
                </div>"""
            st.markdown(f'<div class="sparkline-row">{sparklines}</div>', unsafe_allow_html=True)

        # Quick sample inputs
        st.markdown(sec("💡","Try These"), unsafe_allow_html=True)
        samples = [
            ("😊","I feel so alive and grateful today!"),
            ("😢","I miss my old self so much"),
            ("😤","I am absolutely furious right now"),
            ("😨","I am terrified of what comes next"),
            ("🤝","I trust my best friend with everything"),
        ]
        for icon, sample in samples:
            if st.button(f"{icon} {sample[:38]}…" if len(sample)>38 else f"{icon} {sample}",
                         key=f"samp_{hash(sample)}", use_container_width=True):
                with st.spinner(""):
                    st.session_state.result = get_recommendations(sample, model=model)
                st.session_state.history.insert(0,{
                    'text': sample[:55], 'emotion': st.session_state.result.get('emotion',''),
                    'time': datetime.now().strftime("%H:%M")
                })
                st.session_state.history = st.session_state.history[:12]
                st.rerun()


# ════════════════════════════════════════════════════════════
# PAGE 3 — DATASET EXPLORER
# ════════════════════════════════════════════════════════════
elif "Dataset" in page:
    df = load_df()
    if df is None:
        st.error("Dataset not found at data/dataset.csv")
        st.stop()

    # Top metrics (use computed metrics for consistency)
    metrics_local = compute_dataset_metrics()
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("Total Rows",    f"{metrics_local['samples']:,}")
    with c2: st.metric("Total Words",   f"{metrics_local['total_words']:,}")
    with c3: st.metric("Avg Words/Row", f"{metrics_local['avg_words']:.1f}")
    with c4: st.metric("Unique Texts",  f"{metrics_local['unique_texts']:,}")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Filter
    st.markdown(sec("🔍","Browse & Filter"), unsafe_allow_html=True)
    cols = st.columns([2,2,2])
    with cols[0]:
        emo_filter = st.multiselect("Filter by Emotion", list(EMOTION_UI.keys()),
                                     default=list(EMOTION_UI.keys()))
    with cols[1]:
        min_len, max_len = int(df['text_length'].min()), int(df['text_length'].max())
        len_range = st.slider("Word Count Range", min_len, max_len, (min_len, max_len))
    with cols[2]:
        search_q = st.text_input("Search text", placeholder="keyword…")

    filtered = df[df['emotion'].isin(emo_filter)]
    filtered = filtered[(filtered['text_length'] >= len_range[0]) & (filtered['text_length'] <= len_range[1])]
    if search_q:
        filtered = filtered[filtered['text'].str.contains(search_q, case=False, na=False)]

    st.markdown(f"<p style='font-size:0.78rem;color:rgba(232,234,246,0.35);margin-bottom:0.5rem;'>{len(filtered):,} rows matching filters</p>", unsafe_allow_html=True)
    st.dataframe(filtered[['text','emotion','text_length']].head(50).reset_index(drop=True),
                 use_container_width=True, height=340)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Charts row
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(sec("📏","Word Count Distribution"), unsafe_allow_html=True)
        fig = px.histogram(df, x='text_length', nbins=40,
                           color='emotion', color_discrete_map=COLOR_MAP,
                           barmode='overlay', opacity=0.7,
                           labels={'text_length':'Words per Sample'},
                           title='Word Count by Emotion')
        fig.update_layout(**PLOTLY_DARK, bargap=0.05)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown(sec("📊","Per-Emotion Statistics"), unsafe_allow_html=True)
        stats = df.groupby('emotion').agg(
            Count=('text','count'),
            Avg_Words=('text_length','mean'),
            Min_Words=('text_length','min'),
            Max_Words=('text_length','max'),
            Avg_Chars=('char_length','mean'),
        ).round(1).reset_index()
        st.dataframe(stats, use_container_width=True, height=240)

    # Box plot
    st.markdown(sec("📦","Word Length Box Plot"), unsafe_allow_html=True)
    fig_box = px.box(df, x='emotion', y='text_length', color='emotion',
                     color_discrete_map=COLOR_MAP,
                     title='Word Count Distribution per Emotion',
                     labels={'text_length':'Words','emotion':'Emotion'})
    fig_box.update_layout(**PLOTLY_DARK, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    # Sample sentences per emotion
    st.markdown(sec("💬","Sample Sentences"), unsafe_allow_html=True)
    tabs = st.tabs([f"{EMOTION_UI[e]['icon']} {e.title()}" for e in EMOTION_UI])
    for tab, em in zip(tabs, EMOTION_UI):
        with tab:
            samples = df[df['emotion']==em]['text'].sample(min(8, len(df[df['emotion']==em]))).tolist()
            for s in samples:
                st.markdown(f"""
                <div style="background:var(--surface);border:1px solid var(--border);
                            border-left:3px solid {EMOTION_UI[em]['color']};
                            border-radius:8px;padding:0.65rem 1rem;margin-bottom:0.4rem;
                            font-size:0.85rem;color:var(--txt-2);line-height:1.5;">
                    {s}
                </div>
                """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE 4 — MODEL ARCHITECTURE
# ════════════════════════════════════════════════════════════
elif "Model" in page:
    st.markdown(sec("⚙️","ML Pipeline"), unsafe_allow_html=True)

    # Pipeline steps
    steps = [
        ("📝","Input","User text"),
        ("🧹","Preprocess","NLTK · Regex"),
        ("📐","TF-IDF","Vectorize"),
        ("🤖","Naive Bayes","Classify"),
        ("🎭","Emotion","Output"),
        ("🎵","Spotify","Recommend"),
    ]
    pipe_html = '<div class="pipeline">'
    for i,(icon,name,tech) in enumerate(steps):
        pipe_html += f"""
        <div class="pipe-step">
            <div class="ps-icon">{icon}</div>
            <div class="ps-name">{name}</div>
            <div class="ps-tech">{tech}</div>
        </div>"""
        if i < len(steps)-1:
            pipe_html += '<div class="pipe-arrow">→</div>'
    pipe_html += '</div>'
    st.markdown(pipe_html, unsafe_allow_html=True)

    # Tech stack
    st.markdown(sec("🛠️","Tech Stack"), unsafe_allow_html=True)
    tech_items = [
        ("🐍","Python 3.8+","Core Language"),("🔢","scikit-learn","TF-IDF + NB"),
        ("📝","NLTK","Text Preprocessing"),("🎵","Spotipy","Spotify API"),
        ("🐼","Pandas","Data Handling"),("📊","Streamlit","Dashboard"),
        ("📈","Plotly","Charts"),("💾","Pickle","Model Saving"),
    ]
    tech_html = '<div class="tech-grid">'
    for icon,name,role in tech_items:
        tech_html += f"""
        <div class="tech-card">
            <div class="tc-icon">{icon}</div>
            <div class="tc-name">{name}</div>
            <div class="tc-role">{role}</div>
        </div>"""
    tech_html += '</div>'
    st.markdown(tech_html, unsafe_allow_html=True)

    # Detail panels
    st.markdown(sec("🔬","Model Details"), unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("""
        <div class="info-panel">
            <div class="ip-accent" style="--accent:#7c3aed;"></div>
            <h4>TF-IDF Vectorizer</h4>
            <ul>
                <li><strong>N-gram range:</strong> (1, 2) — unigrams + bigrams</li>
                <li><strong>Max features:</strong> 5,000 most informative terms</li>
                <li><strong>Sublinear TF:</strong> Log scaling for term frequency</li>
                <li><strong>Analyzer:</strong> Word-level tokenization</li>
                <li><strong>Norm:</strong> L2 normalization per document</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-panel" style="margin-top:1rem;">
            <div class="ip-accent" style="--accent:#06b6d4;"></div>
            <h4>Preprocessing Steps</h4>
            <ul>
                <li><strong>Step 1:</strong> Convert to lowercase</li>
                <li><strong>Step 2:</strong> Remove punctuation & digits (regex)</li>
                <li><strong>Step 3:</strong> Tokenize on whitespace</li>
                <li><strong>Step 4:</strong> Remove stopwords (bundled list)</li>
                <li><strong>Step 5:</strong> Rejoin cleaned tokens</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="info-panel">
            <div class="ip-accent" style="--accent:#10b981;"></div>
            <h4>Multinomial Naive Bayes</h4>
            <ul>
                <li><strong>Algorithm:</strong> Multinomial Naive Bayes (MNB)</li>
                <li><strong>Smoothing:</strong> Laplace α = 0.5</li>
                <li><strong>Train/Test split:</strong> 80% / 20% (stratified)</li>
                <li><strong>Accuracy:</strong> ~94% on 108K dataset</li>
                <li><strong>Serialization:</strong> pickle (.pkl)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="info-panel" style="margin-top:1rem;">
            <div class="ip-accent" style="--accent:#f59e0b;"></div>
            <h4>Spotify Integration</h4>
            <ul>
                <li><strong>Library:</strong> Spotipy (Python SDK)</li>
                <li><strong>Auth:</strong> Client Credentials (no OAuth)</li>
                <li><strong>Results:</strong> Top 5 tracks per query</li>
                <li><strong>Fallback:</strong> 5 curated songs per emotion</li>
                <li><strong>Links:</strong> Direct Spotify + YouTube URLs</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Emotions table
    st.markdown(sec("🎭","Emotion → Spotify Query Mapping"), unsafe_allow_html=True)
    queries = {
        "happy":  "feel good upbeat happy songs",
        "sad":    "sad emotional heartbreak songs",
        "anger":  "rage intense rock angry songs",
        "fear":   "dark eerie haunting anxiety songs",
        "trust":  "calm soothing peaceful trust songs",
    }
    rows_html = ""
    for em, q in queries.items():
        ui = EMOTION_UI[em]
        lbl = EMOTION_META.get(em,{}).get("label",em.title())
        rows_html += f"""
        <div style="display:flex;align-items:center;gap:1rem;padding:0.75rem 1rem;
                    background:var(--surface);border:1px solid var(--border);
                    border-left:3px solid {ui['color']};
                    border-radius:8px;margin-bottom:0.4rem;transition:all 0.2s ease;"
             onmouseover="this.style.transform='translateX(4px)'"
             onmouseout="this.style.transform='translateX(0)'">
            <span style="font-size:1.3rem;flex-shrink:0;">{ui['icon']}</span>
            <span style="font-family:'Outfit',sans-serif;font-weight:700;
                         font-size:0.88rem;color:{ui['color']};width:70px;flex-shrink:0;">{lbl}</span>
            <span style="font-size:0.8rem;color:rgba(232,234,246,0.5);">→</span>
            <span style="font-size:0.85rem;color:rgba(232,234,246,0.75);font-style:italic;">"{q}"</span>
        </div>"""
    st.markdown(rows_html, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PAGE 5 — ANALYTICS
# ════════════════════════════════════════════════════════════
elif "Analytics" in page:
    df = load_df()
    if df is None:
        st.error("Dataset not found.")
        st.stop()

    st.markdown(sec("📈","Advanced Analytics"), unsafe_allow_html=True)

    # Radar chart — per-emotion stats
    c1, c2 = st.columns(2, gap="large")
    with c1:
        stats = df.groupby('emotion').agg(
            count=('text','count'),
            avg_len=('text_length','mean'),
            max_len=('text_length','max'),
        ).reset_index()
        fig_radar = go.Figure()
        categories = ['Count (÷500)', 'Avg Length', 'Max Length (÷5)', 'Balance Score']
        max_count = stats['count'].max()
        for _, row in stats.iterrows():
            em = row['emotion']
            vals = [
                row['count'] / 500,
                row['avg_len'],
                row['max_len'] / 5,
                min(row['count'] / max_count * 10, 10),
            ]
            vals.append(vals[0])
            fig_radar.add_trace(go.Scatterpolar(
                r=vals,
                theta=categories + [categories[0]],
                fill='toself',
                name=em,
                line_color=COLOR_MAP[em],
                fillcolor=hex_to_rgba(COLOR_MAP[em], 0.25),
                opacity=0.4,
            ))
        fig_radar.update_layout(
            **{k:v for k,v in PLOTLY_DARK.items() if k not in ('xaxis','yaxis')},
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, color='rgba(255,255,255,0.2)'),
                angularaxis=dict(color='rgba(255,255,255,0.3)'),
            ),
            title='Emotion Attribute Radar',
            showlegend=True,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with c2:
        # Violin
        fig_v = px.violin(df, x='emotion', y='text_length', color='emotion',
                          color_discrete_map=COLOR_MAP, box=True, points=False,
                          title='Word Count Spread (Violin)',
                          labels={'text_length':'Words','emotion':''})
        fig_v.update_layout(**PLOTLY_DARK, showlegend=False)
        st.plotly_chart(fig_v, use_container_width=True)

    # Treemap
    st.markdown(sec("🗺️","Treemap — Emotion Distribution"), unsafe_allow_html=True)
    ec = df['emotion'].value_counts().reset_index()
    ec.columns = ['emotion','count']
    ec['label'] = ec.apply(lambda r: f"{EMOTION_UI[r['emotion']]['icon']} {r['emotion'].title()}<br>{r['count']:,}", axis=1)
    fig_tree = px.treemap(
        ec, path=['emotion'], values='count',
        color='emotion', color_discrete_map=COLOR_MAP,
        title='Sample Distribution Treemap',
    )
    fig_tree.update_traces(textinfo='label+percent entry',
                           textfont=dict(family='Outfit', size=14, color='white'))
    fig_tree.update_layout(**{k:v for k,v in PLOTLY_DARK.items() if 'axis' not in k})
    st.plotly_chart(fig_tree, use_container_width=True)

    # Sunburst (length buckets)
    st.markdown(sec("🌞","Sunburst — Length Buckets by Emotion"), unsafe_allow_html=True)
    df2 = df.copy()
    df2['bucket'] = pd.cut(df2['text_length'], bins=[0,3,7,15,50,999],
                            labels=['1-3 words','4-7 words','8-15 words','16-50 words','50+ words'])
    sb_data = df2.groupby(['emotion','bucket']).size().reset_index(name='count')
    fig_sun = px.sunburst(sb_data, path=['emotion','bucket'], values='count',
                          color='emotion', color_discrete_map=COLOR_MAP,
                          title='Emotion + Word-Length Sunburst')
    fig_sun.update_layout(**{k:v for k,v in PLOTLY_DARK.items() if 'axis' not in k})
    st.plotly_chart(fig_sun, use_container_width=True)

    # (Removed) Cumulative Sample Curve — intentionally omitted to simplify dashboard


# ════════════════════════════════════════════════════════════
# PAGE 6 — SNAKE GAME
# ════════════════════════════════════════════════════════════
elif "Snake" in page:

    class SnakeGame:
        W, H = 20, 20
        def __init__(self):
            self.snake = [(10,10),(10,11),(10,12)]
            self.food  = self._spawn()
            self.dir   = (-1, 0)
            self.score = 0
            self.over  = False
        def _spawn(self):
            while True:
                f = (random.randint(0,self.H-1), random.randint(0,self.W-1))
                if f not in getattr(self,'snake',[]): return f
        def steer(self, d):
            if (d[0]*-1, d[1]*-1) != self.dir: self.dir = d
        def tick(self):
            if self.over: return
            h = (self.snake[0][0]+self.dir[0], self.snake[0][1]+self.dir[1])
            if not (0<=h[0]<self.H and 0<=h[1]<self.W) or h in self.snake:
                self.over = True; return
            self.snake.insert(0, h)
            if h == self.food: self.score += 10; self.food = self._spawn()
            else: self.snake.pop()
        def grid_html(self):
            g = [[0]*self.W for _ in range(self.H)]
            for i,s in enumerate(self.snake): g[s[0]][s[1]] = 2 if i==0 else 1
            g[self.food[0]][self.food[1]] = 3
            html = '<div class="snake-grid">'
            for row in g:
                for c in row:
                    cls = 'sc-head' if c==2 else 'sc-snake' if c==1 else 'sc-food' if c==3 else 'sc-empty'
                    html += f'<div class="snake-cell {cls}"></div>'
            html += '</div>'
            return html

    st.markdown(sec("🎮","Classic Snake"), unsafe_allow_html=True)
    st.markdown("<p style='color:rgba(232,234,246,0.4);font-size:0.85rem;'>Use ↑ ↓ ← → buttons to navigate · Eat orange food · +10 pts each</p>", unsafe_allow_html=True)

    if 'sg' not in st.session_state: st.session_state.sg = SnakeGame()
    if 'sg_run' not in st.session_state: st.session_state.sg_run = False

    b1,b2,b3,_,sc = st.columns([1,1,1,2,1])
    with b1:
        if st.button("▶ Start",  use_container_width=True):
            st.session_state.sg_run = True; st.rerun()
    with b2:
        if st.button("↺ Reset",  use_container_width=True):
            st.session_state.sg = SnakeGame(); st.session_state.sg_run = False; st.rerun()
    with b3:
        if st.button("⏸ Pause",  use_container_width=True):
            st.session_state.sg_run = False; st.rerun()
    with sc:
        st.metric("Score", st.session_state.sg.score)

    if st.session_state.sg_run:
        _,u,_ = st.columns([2,1,2])
        with u:
            if st.button("⬆", use_container_width=True, key="u"): st.session_state.sg.steer((-1,0))
        l,d,r,_,_ = st.columns([1,1,1,1,1])
        with l:
            if st.button("⬅", use_container_width=True, key="l"): st.session_state.sg.steer((0,-1))
        with d:
            if st.button("⬇", use_container_width=True, key="d"): st.session_state.sg.steer((1,0))
        with r:
            if st.button("➡", use_container_width=True, key="r"): st.session_state.sg.steer((0,1))

        if not st.session_state.sg.over: st.session_state.sg.tick()

    st.markdown(st.session_state.sg.grid_html(), unsafe_allow_html=True)

    s1,s2,s3 = st.columns(3)
    with s1: st.metric("Score",  st.session_state.sg.score)
    with s2: st.metric("Length", len(st.session_state.sg.snake))
    with s3:
        if st.session_state.sg.over: st.error("💀 Game Over!")
        elif st.session_state.sg_run: st.success("🟢 Running…")
        else: st.info("⏸ Paused")

    if st.session_state.sg_run and not st.session_state.sg.over:
        time.sleep(0.25); st.rerun()


# ════════════════════════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════════════════════════
metrics = compute_dataset_metrics()
samples_text = f"{metrics['samples']:,} samples" if metrics['samples'] else "No dataset"
emotions_text = f"{metrics['unique_emotions']} emotions" if metrics['unique_emotions'] else "0 emotions"
acc_text = f"{metrics['accuracy']*100:.1f}% Accuracy" if metrics['accuracy'] is not None else "Accuracy N/A"

st.markdown(f"""
<div class="footer">
    <div class="footer-logo">🌊 EmotionWave</div>
    <div style="margin-top:0.8rem;display:flex;justify-content:center;gap:0.6rem;flex-wrap:wrap;">
        <span class="badge badge-new">{samples_text}</span>
        <span class="badge badge-hot">{acc_text}</span>
        <span class="badge badge-new">{emotions_text}</span>
        <span class="badge badge-new">Live Spotify</span>
    </div>
</div>
""", unsafe_allow_html=True)