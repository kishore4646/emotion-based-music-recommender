# 🎵 Emotion-Based Music Recommender 🎧

An AI-powered music recommendation system that detects user emotions from text input and suggests songs accordingly using Machine Learning and Spotify integration.

---

## 🚀 Features

- 🧠 Emotion Detection using Machine Learning
- 🎯 Predicts emotions: **Happy, Sad, Anger, Fear, Trust**
- 🎵 Recommends songs based on detected mood
- 🔗 Spotify search integration (opens songs instantly)
- 📊 Clean and interactive Streamlit dashboard
- ⚡ Fast and lightweight model (TF-IDF + ML)

---

## 🏗️ Project Structure
emotion_based_music_recommender/
│
├── config/
│ └── spotify_config.py
│
├── data/
│ ├── dataset.csv
│ └── emotion_model_improved.pkl
│
├── src/
│ ├── dashboard.py # Streamlit UI
│ ├── model.py # ML model loading & prediction
│ ├── preprocess.py # Text preprocessing
│ ├── recommender.py # Core logic
│ └── spotify_api.py # Song recommendation logic
│
├── README.md
├── requirements.txt
└── .gitignore

---

## 🧠 How It Works

1. User enters mood text  
2. Text is preprocessed  
3. ML model predicts emotion  
4. Songs are fetched based on emotion  
5. Results are displayed with Spotify links  

---

## ⚙️ Tech Stack

- Python 🐍
- Scikit-learn (ML Model)
- TF-IDF Vectorizer
- Streamlit (Frontend UI)
- Spotify Web Integration

---

## ▶️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/emotion-based-music-recommender.git
cd emotion-based-music-recommender
pip install -r requirements.txt

▶️ Run the App
cd src
streamlit run dashboard.py
📊 Model Details
Algorithm: Logistic Regression / ML Pipeline
Feature Extraction: TF-IDF
Dataset: Custom labeled emotion dataset
Accuracy: ~75–85% (depending on dataset)

📸 Demo

Add screenshots of your dashboard here

🚀 Future Improvements
🎧 AI Playlist Generator
📈 Mood History Tracking
🌍 Multi-language support
🤖 Deep Learning (BERT)
📱 Mobile App Integration
🤝 Contribution

Feel free to fork this repo and contribute!

📜 License

This project is open-source and available under the MIT License.

👨‍💻 Author

Kishore B S
