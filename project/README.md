# 🎵 Mood-Based Music Recommender System

> **Final Year AI/ML Project**
> Uses NLP + Machine Learning to detect your emotion from text and recommends Spotify songs that match your mood.

---

## 📌 Features

- 🧠 **Emotion Detection** — TF-IDF + Naive Bayes classifier trained on 150+ labeled sentences
- 🎵 **Spotify Integration** — Live song search via Spotify Web API (Spotipy)
- 🛡️ **Fallback Mode** — Curated song list when API credentials are missing
- 🎨 **Clean Console UI** — Color-coded, emoji-enhanced terminal interface
- 🔗 **Clickable Links** — Direct Spotify URLs printed in the terminal
- 📦 **Modular Code** — Clean separation of preprocessing, model, API, and UI layers

---

## 🗂️ Project Structure

```
project/
│
├── data/
│   ├── dataset.csv          ← 150+ labeled emotion sentences
│   └── emotion_model.pkl    ← Trained model (auto-generated)
│
├── src/
│   ├── preprocess.py        ← NLP text cleaning (NLTK)
│   ├── model.py             ← TF-IDF + Naive Bayes training & inference
│   ├── recommender.py       ← Orchestration layer
│   └── spotify_api.py       ← Spotify Web API integration
│
├── config/
│   └── spotify_config.py    ← API credentials (edit this!)
│
├── main.py                  ← Entry point
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions (VS Code)

### 1. Clone / Download the Project

```bash
cd your-workspace-folder
```

### 2. Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Spotify API (Optional but recommended)

**Get free credentials in 2 minutes:**

1. Go to [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Log in → **Create App**
3. Fill in:
   - App Name: `MoodMusicRecommender`
   - Redirect URI: `http://localhost`
4. Copy your **Client ID** and **Client Secret**

**Add credentials** — open `config/spotify_config.py`:

```python
SPOTIFY_CLIENT_ID     = "paste_your_client_id_here"
SPOTIFY_CLIENT_SECRET = "paste_your_client_secret_here"
```

> **Without credentials:** The app runs perfectly using a curated fallback song list.

### 5. Run the Application

```bash
python main.py
```

---

## 🖥️ Sample Output

```
╔══════════════════════════════════════════════════════╗
║        🎵  MOOD-BASED MUSIC RECOMMENDER  🎵          ║
║     Powered by NLP + Machine Learning + Spotify      ║
╚══════════════════════════════════════════════════════╝

  ✓ Model ready

────────────────────────────────────────────────────────
  💬 Describe how you're feeling:
  > I just got promoted and I'm so happy today!

  Analyzing your mood...

  Detected Emotion:  😊 Happy

  ··············································
  🎶 Recommended Songs for You:

  Source: ● Live Spotify API

  1. Happy — Pharrell Williams
     🔗 https://open.spotify.com/track/...

  2. Can't Stop the Feeling — Justin Timberlake
     🔗 https://open.spotify.com/track/...
  ...
```

---

## 🤖 How It Works

| Step | Module | Description |
|------|--------|-------------|
| 1 | `preprocess.py` | Lowercase → Remove punctuation → Remove stopwords |
| 2 | `model.py` | TF-IDF vectorization + Naive Bayes classification |
| 3 | `spotify_api.py` | Emotion → search query → Spotify API → top 5 songs |
| 4 | `recommender.py` | Orchestrates all 3 steps |
| 5 | `main.py` | User interface + display loop |

---

## 🎯 Supported Emotions

| Emotion | Example Input |
|---------|--------------|
| 😊 Happy | "I feel amazing today!" |
| 😢 Sad | "I miss them so much, I can't stop crying" |
| 😠 Angry | "I'm furious, they betrayed my trust" |
| 😨 Fear | "I'm terrified of what comes next" |
| 🤝 Trust | "I know they'll always have my back" |

---

## 🛠️ Tech Stack

- **Python 3.8+**
- **scikit-learn** — TF-IDF + Naive Bayes
- **NLTK** — Stopword removal
- **Spotipy** — Spotify Web API client
- **pandas** — Dataset loading

---

## 📄 License

Free to use for academic and educational purposes.
