# ============================================================
# preprocess.py — NLP Text Preprocessing Module
# Cleans raw text for ML model input
# Bundled stopwords — no network download required
# ============================================================

import re

# Bundled English stopwords (NLTK's list, no download needed)
STOP_WORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll",
    "m","o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn","weren",
    "won","wouldn","could","would","may","might","shall","need","dare","ought",
    "used","get","got","also","back","still","even","around","ever","much",
    "well","want","go","going","gone","come","came","think","know","see","look",
    "make","take","put","say","said","tell","told","feel","keep","let","seem",
    "turn","show","play","run","move","live","give","work","call","try","ask",
    "need","seem","hear","help","talk","start","found","left","never","always",
    "every","something","anything","nothing","everything","someone","anyone",
    "everyone","somewhere","already","really","actually","usually","often",
    "next","last","long","little","own","right","big","old","great","high",
    "small","large","new","good","bad","true","false","many","us","way","day",
    "man","woman","child","time","year","people","hand","part","place","case",
    "week","company","system","program","question","government","number","night",
    "point","home","water","room","mother","area","money","story","fact","month",
    "lot","right","study","book","eye","job","word","business","issue","side",
    "kind","head","house","service","friend","father","power","hour","game",
    "line","end","among","another","any","whatever","whenever","wherever",
    "whoever","however","although","though","unless","since","whether","whilst",
}


def clean_text(text: str) -> str:
    """
    Full NLP preprocessing pipeline:
      1. Lowercase
      2. Remove punctuation
      3. Remove stopwords
      4. Strip extra whitespace

    Args:
        text (str): Raw user input or dataset sentence

    Returns:
        str: Cleaned, normalized text ready for vectorization
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove punctuation using regex (handles unicode punctuation too)
    text = re.sub(r"[^\w\s]", "", text)

    # Step 3: Remove digits (optional but helps with noise)
    text = re.sub(r"\d+", "", text)

    # Step 4: Tokenize by splitting on whitespace
    tokens = text.split()

    # Step 5: Remove stopwords
    tokens = [word for word in tokens if word not in STOP_WORDS]

    # Step 6: Rejoin and strip extra spaces
    cleaned = " ".join(tokens).strip()

    return cleaned


def preprocess_batch(texts):
    """Preprocess a list of texts and return cleaned strings list.

    Args:
        texts (iterable): list/iterable of raw text strings

    Returns:
        list: cleaned text strings
    """
    if texts is None:
        return []
    cleaned = []
    for t in texts:
        try:
            cleaned.append(clean_text(t))
        except Exception:
            cleaned.append("")
    return cleaned


def preprocess_batch(texts: list) -> list:
    """
    Apply clean_text to a list of texts.

    Args:
        texts (list): List of raw text strings

    Returns:
        list: List of cleaned text strings
    """
    return [clean_text(t) for t in texts]


# ── Quick test when run directly ─────────────────────────────
if __name__ == "__main__":
    sample = "I'm feeling absolutely AMAZING today!! Everything is perfect."
    print(f"Original : {sample}")
    print(f"Cleaned  : {clean_text(sample)}")
