# ============================================================
# spotify_api.py — Spotify API Integration
# Searches for songs matching mood keywords using Spotipy
# Uses Client Credentials (no OAuth / browser redirect needed)
# ============================================================

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.spotify_config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

# Spotipy for Spotify Web API
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False


# ── Curated fallback songs per emotion ───────────────────────
# Used when API credentials are missing or API call fails
FALLBACK_SONGS = {
    "happy": [
        {"name": "Appadi Podu", "artist": "KK", "url": "https://open.spotify.com/search/Appadi%20Podu%20KK"},
        {"name": "Google Google", "artist": "Vijay", "url": "https://open.spotify.com/search/Google%20Google%20Vijay"},
        {"name": "Selfie Pulla", "artist": "Vijay", "url": "https://open.spotify.com/search/Selfie%20Pulla%20Vijay"},
        {"name": "Chellamma", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Chellamma%20Anirudh"},
        {"name": "Danga Maari Oodhari", "artist": "Dhanush", "url": "https://open.spotify.com/search/Danga%20Maari%20Dhanush"},
        {"name": "Why This Kolaveri Di", "artist": "Dhanush", "url": "https://open.spotify.com/search/Kolaveri%20Dhanush"},
        {"name": "Vaadi Pulla Vaadi", "artist": "Hip Hop Tamizha", "url": "https://open.spotify.com/search/Vaadi%20Pulla%20HipHop"},
        {"name": "Happy New Year", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/Happy%20New%20Year%20Yuvan"},
        {"name": "Aathichudi", "artist": "Hip Hop Tamizha", "url": "https://open.spotify.com/search/Aathichudi%20HipHop"},
        {"name": "Oru Kuchi Oru Kulfi", "artist": "G.V. Prakash", "url": "https://open.spotify.com/search/Oru%20Kuchi%20GV%20Prakash"},
        {"name": "Sodakku", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Sodakku%20Anirudh"},
        {"name": "Kutty Story", "artist": "Vijay", "url": "https://open.spotify.com/search/Kutty%20Story%20Vijay"},
        {"name": "Don'u Don'u Don'u", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Donu%20Donu%20Anirudh"},
        {"name": "Hey Mama", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Hey%20Mama%20Anirudh"},
        {"name": "Marana Mass", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Marana%20Mass%20Anirudh"},
        {"name": "Jolly O Gymkhana", "artist": "Vijay", "url": "https://open.spotify.com/search/Jolly%20Gymkhana%20Vijay"},
        {"name": "Private Party", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Private%20Party%20Anirudh"},
        {"name": "Pakkam Vanthu", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Pakkam%20Vanthu%20Anirudh"},
        {"name": "Boomi Enna Suthudhe", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Boomi%20Anirudh"},
        {"name": "Let's Take a Selfie", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Selfie%20Anirudh"},
        {"name": "Local Boys", "artist": "Dhanush", "url": "https://open.spotify.com/search/Local%20Boys%20Dhanush"},
        {"name": "Chennai City Gangsta", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Chennai%20Gangsta"},
        {"name": "Vaa Vaa Vaa", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Vaa%20Vaa%20Anirudh"},
        {"name": "Udhungada Sangu", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Udhungada%20Sangu"},
        {"name": "Aaluma Doluma", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Aaluma%20Doluma"},
        {"name": "Kutti Story", "artist": "Vijay", "url": "https://open.spotify.com/search/Kutti%20Story%20Vijay"},
        {"name": "Vaathi Raid", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Vaathi%20Raid"},
        {"name": "Arabic Kuthu", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Arabic%20Kuthu"},
        {"name": "Master the Blaster", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Master%20Blaster"},
        {"name": "Hukum", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Hukum"},
    ],
    "sad": [
        {"name": "Vennilave Vennilave", "artist": "Unnikrishnan", "url": "https://open.spotify.com/search/Vennilave%20Vennilave%20Unnikrishnan"},
        {"name": "Po Nee Po", "artist": "Dhanush", "url": "https://open.spotify.com/search/Po%20Nee%20Po%20Dhanush"},
        {"name": "Unna Nenachu", "artist": "Sid Sriram", "url": "https://open.spotify.com/search/Unna%20Nenachu%20Sid%20Sriram"},
        {"name": "Maruvaarthai", "artist": "Sid Sriram", "url": "https://open.spotify.com/search/Maruvaarthai%20Sid%20Sriram"},
        {"name": "Ennodu Nee Irundhaal", "artist": "Sid Sriram", "url": "https://open.spotify.com/search/Ennodu%20Nee%20Irundhaal%20Sid%20Sriram"},
        {"name": "Avalum Naanum", "artist": "Vijay Yesudas", "url": "https://open.spotify.com/search/Avalum%20Naanum%20Vijay%20Yesudas"},
        {"name": "Usure Pogudhey", "artist": "Karthik", "url": "https://open.spotify.com/search/Usure%20Pogudhey%20Karthik"},
        {"name": "Mun Andhi", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Mun%20Andhi%20Harris%20Jayaraj"},
        {"name": "Yaar Indha Saalai Oram", "artist": "G.V. Prakash", "url": "https://open.spotify.com/search/Yaar%20Indha%20Saalai%20Oram%20GV%20Prakash"},
        {"name": "Kannazhaga", "artist": "Dhanush", "url": "https://open.spotify.com/search/Kannazhaga%20Dhanush"},
        {"name": "Nenjukkul Peidhidum", "artist": "Hariharan", "url": "https://open.spotify.com/search/Nenjukkul%20Peidhidum%20Hariharan"},
        {"name": "Thalli Pogathey", "artist": "Sid Sriram", "url": "https://open.spotify.com/search/Thalli%20Pogathey%20Sid%20Sriram"},
        {"name": "Idhazhin Oram", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Idhazhin%20Oram%20Anirudh"},
        {"name": "Po Indru Neeyaga", "artist": "Dhanush", "url": "https://open.spotify.com/search/Po%20Indru%20Neeyaga%20Dhanush"},
        {"name": "Anbe En Anbe", "artist": "Harish Raghavendra", "url": "https://open.spotify.com/search/Anbe%20En%20Anbe%20Harish"},
        {"name": "Oru Naalil", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/Oru%20Naalil%20Yuvan"},
        {"name": "Kadhal Kan Kattudhe", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kadhal%20Kan%20Kattudhe%20Anirudh"},
        {"name": "Pookkal Pookkum", "artist": "G.V. Prakash", "url": "https://open.spotify.com/search/Pookkal%20Pookkum%20GV"},
        {"name": "New York Nagaram", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/New%20York%20Nagaram%20ARR"},
        {"name": "Vaseegara", "artist": "Bombay Jayashri", "url": "https://open.spotify.com/search/Vaseegara%20Bombay%20Jayashri"},
        {"name": "New York Nagaram", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/New%20York%20Nagaram"},
        {"name": "Po Nee Po", "artist": "Dhanush", "url": "https://open.spotify.com/search/Po%20Nee%20Po"},
        {"name": "Unakkenna Venum Sollu", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Unakkenna%20Venum"},
        {"name": "Kadhal Kan Kattudhe", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kadhal%20Kan%20Kattudhe"},
        {"name": "Kannazhaga", "artist": "Dhanush", "url": "https://open.spotify.com/search/Kannazhaga"},
        {"name": "Uyire Uyire", "artist": "Hariharan", "url": "https://open.spotify.com/search/Uyire%20Uyire"},
        {"name": "Thalli Pogathey", "artist": "Sid Sriram", "url": "https://open.spotify.com/search/Thalli%20Pogathey"},
        {"name": "Agaram Ippo", "artist": "Karthik", "url": "https://open.spotify.com/search/Agaram%20Ippo"},
        {"name": "Venmegam", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Venmegam"},
        {"name": "Pookal Pookum", "artist": "Harini", "url": "https://open.spotify.com/search/Pookal%20Pookum"},
    ],
    "anger": [
        {"name": "Aalaporan Thamizhan", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Aalaporan%20Thamizhan%20AR%20Rahman"},
        {"name": "Verithanam", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Verithanam%20AR%20Rahman"},
        {"name": "Chilla Chilla", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Chilla%20Chilla%20Anirudh%20Ravichander"},
        {"name": "Vaathi Raid", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Vaathi%20Raid%20Anirudh%20Ravichander"},
        {"name": "Arabic Kuthu", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Arabic%20Kuthu%20Anirudh%20Ravichander"},
        {"name": "Ranjithame", "artist": "Thaman S", "url": "https://open.spotify.com/search/Ranjithame%20Thaman%20S"},
        {"name": "Beast Mode", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Beast%20Mode%20Anirudh%20Ravichander"},
        {"name": "Petta Paraak", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Petta%20Paraak%20Anirudh%20Ravichander"},
        {"name": "Surviva", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Surviva%20Anirudh%20Ravichander"},
        {"name": "Thani Oruvan Theme", "artist": "Hiphop Tamizha", "url": "https://open.spotify.com/search/Thani%20Oruvan%20Theme%20Hiphop%20Tamizha"},
        {"name": "Otha Sollaala", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Otha%20Sollaala%20GV%20Prakash"},
        {"name": "Yathe Yathe", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Yathe%20Yathe%20GV%20Prakash"},
        {"name": "Kodi Parakkudha", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Kodi%20Parakkudha%20Santhosh%20Narayanan"},
        {"name": "Neruppu Da", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Neruppu%20Da%20Santhosh%20Narayanan"},
        {"name": "Semma Weightu", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Semma%20Weightu%20Santhosh%20Narayanan"},
        {"name": "Karuppu Vellai", "artist": "Sam C.S", "url": "https://open.spotify.com/search/Karuppu%20Vellai%20Sam%20CS"},
        {"name": "Danga Maari Oodhari", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Danga%20Maari%20Oodhari%20Anirudh"},
        {"name": "Maari Thara Local", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Maari%20Thara%20Local%20Anirudh"},
        {"name": "Local Boys", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Local%20Boys%20Anirudh"},
        {"name": "Sivuni Aana", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Sivuni%20Aana%20GV%20Prakash"},
        {"name": "Aambala Singam", "artist": "Hiphop Tamizha", "url": "https://open.spotify.com/search/Aambala%20Singam%20Hiphop%20Tamizha"},
        {"name": "Club Le Mabbu Le", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Club%20Le%20Mabbu%20Le%20Anirudh"},
        {"name": "Don'u Don'u Don'u", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Donu%20Donu%20Donu%20Anirudh"},
        {"name": "Marana Mass", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Marana%20Mass%20Anirudh"},
        {"name": "Tharam Maara Single", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Tharam%20Maara%20Single%20Anirudh"},
        {"name": "Sodakku", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Sodakku%20Santhosh%20Narayanan"},
        {"name": "Kabali Theme", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Kabali%20Theme%20Santhosh%20Narayanan"},
        {"name": "Kaasu Panam", "artist": "Hiphop Tamizha", "url": "https://open.spotify.com/search/Kaasu%20Panam%20Hiphop%20Tamizha"},
        {"name": "Vilayaadu Mankatha", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/Vilayaadu%20Mankatha%20Yuvan%20Shankar%20Raja"},
        {"name": "Mankatha Theme", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/Mankatha%20Theme%20Yuvan%20Shankar%20Raja"},
        {"name": "Arjunar Villu", "artist": "Mani Sharma", "url": "https://open.spotify.com/search/Arjunar%20Villu%20Mani%20Sharma"},
        {"name": "Vettaikaaran Theme", "artist": "Vijay Antony", "url": "https://open.spotify.com/search/Vettaikaaran%20Theme%20Vijay%20Antony"},
        {"name": "Naan Autokaran", "artist": "Deva", "url": "https://open.spotify.com/search/Naan%20Autokaran%20Deva"},
        {"name": "Pathala Pathala", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Pathala%20Pathala%20Anirudh"},
        {"name": "Jithu Jilladi", "artist": "D. Imman", "url": "https://open.spotify.com/search/Jithu%20Jilladi%20Imman"},
        {"name": "Sandakozhi Theme", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/Sandakozhi%20Theme%20Yuvan"},
        {"name": "Rowthiram Title", "artist": "Prakash Nikki", "url": "https://open.spotify.com/search/Rowthiram%20Title%20Prakash%20Nikki"},
        {"name": "Ethir Neechal Theme", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Ethir%20Neechal%20Theme%20Anirudh"},
        {"name": "Thalaivaa Title", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Thalaivaa%20Title%20GV%20Prakash"},
        {"name": "Master the Blaster", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Master%20the%20Blaster%20Anirudh"},
        {"name": "Sooravali", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Sooravali%20AR%20Rahman"},
        {"name": "Veeram Title", "artist": "Devi Sri Prasad", "url": "https://open.spotify.com/search/Veeram%20Title%20DSP"},
        {"name": "Singam Theme", "artist": "Devi Sri Prasad", "url": "https://open.spotify.com/search/Singam%20Theme%20DSP"},
        {"name": "NGK Theme", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/NGK%20Theme%20Yuvan"},
        {"name": "Karnan Theme", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Karnan%20Theme%20Santhosh"},
        {"name": "Asuran Theme", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Asuran%20Theme%20GV%20Prakash"},
        {"name": "Polladhavan Theme", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Polladhavan%20Theme%20GV%20Prakash"},
        {"name": "Theri Theme", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Theri%20Theme%20GV%20Prakash"},
        {"name": "Kaththi Theme", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kaththi%20Theme%20Anirudh"},
        {"name": "Vikram Title Track", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Vikram%20Title%20Track%20Anirudh"},
    ],
    "fear": [
        {"name": "Kaatru Veliyidai Theme", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Kaatru%20Veliyidai%20Theme%20AR%20Rahman"},
        {"name": "Aaromale", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Aaromale%20AR%20Rahman"},
        {"name": "Nenjukkul Peidhidum", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Nenjukkul%20Peidhidum%20Harris%20Jayaraj"},
        {"name": "New York Nagaram", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/New%20York%20Nagaram%20AR%20Rahman"},
        {"name": "En Kadhal Solla", "artist": "Yuvan Shankar Raja", "url": "https://open.spotify.com/search/En%20Kadhal%20Solla%20Yuvan%20Shankar%20Raja"},
        {"name": "Oru Deivam Thantha Poove", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Oru%20Deivam%20Thantha%20Poove%20Ilaiyaraaja"},
        {"name": "Thoongatha Vizhigal", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Thoongatha%20Vizhigal%20Ilaiyaraaja"},
        {"name": "Uyirin Uyire", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Uyirin%20Uyire%20Harris%20Jayaraj"},
        {"name": "Idhayathai Yedho Ondru", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Idhayathai%20Yedho%20Ondru%20Harris"},
        {"name": "Mannipaaya", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Mannipaaya%20AR%20Rahman"},
        {"name": "Po Nee Po", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Po%20Nee%20Po%20Anirudh"},
        {"name": "Kanave Kanave", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kanave%20Kanave%20Anirudh"},
        {"name": "Yaen Ennai Pirindhai", "artist": "Radhan", "url": "https://open.spotify.com/search/Yaen%20Ennai%20Pirindhai%20Radhan"},
        {"name": "Kadhal Kan Kattudhe", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kadhal%20Kan%20Kattudhe%20Anirudh"},
        {"name": "Neeyum Naanum Anbe", "artist": "Hiphop Tamizha", "url": "https://open.spotify.com/search/Neeyum%20Naanum%20Anbe%20Hiphop%20Tamizha"},
        {"name": "Thalli Pogathey", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Thalli%20Pogathey%20AR%20Rahman"},
        {"name": "Mazhai Vara Pogudhae", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Mazhai%20Vara%20Pogudhae%20Harris"},
        {"name": "Anbil Avan", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Anbil%20Avan%20AR%20Rahman"},
        {"name": "Usure Pogudhey", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Usure%20Pogudhey%20GV%20Prakash"},
        {"name": "Unakkenna Venum Sollu", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Unakkenna%20Venum%20Sollu%20Harris"},
        {"name": "Kannazhaga", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kannazhaga%20Anirudh"},
        {"name": "Venmegam", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Venmegam%20Harris%20Jayaraj"},
        {"name": "Ennamo Yedho", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Ennamo%20Yedho%20Harris"},
        {"name": "Suttrum Vizhi", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Suttrum%20Vizhi%20Harris"},
        {"name": "Ava Enna", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Ava%20Enna%20Harris"},
        {"name": "Lolita", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Lolita%20Harris"},
        {"name": "Oh Shanthi Shanthi", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Oh%20Shanthi%20Shanthi%20Harris"},
        {"name": "Mun Andhi", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Mun%20Andhi%20Harris"},
        {"name": "Vaseegara", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Vaseegara%20Harris"},
        {"name": "Pachchai Nirame", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Pachchai%20Nirame%20AR%20Rahman"},
        {"name": "Ennavale Adi Ennavale", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Ennavale%20Adi%20Ennavale%20AR%20Rahman"},
        {"name": "Snehithane", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Snehithane%20AR%20Rahman"},
        {"name": "Anjali Anjali", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Anjali%20Anjali%20Ilaiyaraaja"},
        {"name": "Thenpaandi Cheemayile", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Thenpaandi%20Cheemayile%20Ilaiyaraaja"},
        {"name": "Poongatru Thirumbuma", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Poongatru%20Thirumbuma%20Ilaiyaraaja"},
        {"name": "Kanne Kalaimane", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Kanne%20Kalaimane%20Ilaiyaraaja"},
        {"name": "Ilaya Nila", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Ilaya%20Nila%20Ilaiyaraaja"},
        {"name": "Nila Kaigirathu", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Nila%20Kaigirathu%20Ilaiyaraaja"},
        {"name": "Oru Naal Podhuma", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Oru%20Naal%20Podhuma%20Ilaiyaraaja"},
        {"name": "En Iniya Pon Nilave", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/En%20Iniya%20Pon%20Nilave%20Ilaiyaraaja"},
    ],
    "trust": [
        {"name": "Munbe Vaa", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Munbe%20Vaa%20AR%20Rahman"},
        {"name": "Anbil Avan", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Anbil%20Avan%20AR%20Rahman"},
        {"name": "Vinnaithaandi Varuvaayaa Theme", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/VTV%20Theme%20AR%20Rahman"},
        {"name": "Aaruyire", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Aaruyire%20AR%20Rahman"},
        {"name": "Nenjukul Peidhidum", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Nenjukul%20Peidhidum%20Harris"},
        {"name": "Unnale Unnale", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Unnale%20Unnale%20Harris"},
        {"name": "Hasili Fisili", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Hasili%20Fisili%20Harris"},
        {"name": "Ennai Konjam", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Ennai%20Konjam%20Harris"},
        {"name": "Uyire Uyire", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Uyire%20Uyire%20AR%20Rahman"},
        {"name": "Kadhal Sadugudu", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Kadhal%20Sadugudu%20AR%20Rahman"},
        {"name": "Thalli Pogathey", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Thalli%20Pogathey%20AR%20Rahman"},
        {"name": "Hosanna", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Hosanna%20AR%20Rahman"},
        {"name": "Azhagiye", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Azhagiye%20AR%20Rahman"},
        {"name": "Maruvaarthai", "artist": "Darbuka Siva", "url": "https://open.spotify.com/search/Maruvaarthai%20Darbuka%20Siva"},
        {"name": "Nenjukkul Peidhidum", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Nenjukkul%20Peidhidum%20Harris"},
        {"name": "Ava Enna", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Ava%20Enna%20Harris"},
        {"name": "Venmegam", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Venmegam%20Harris"},
        {"name": "Suttrum Vizhi", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Suttrum%20Vizhi%20Harris"},
        {"name": "Ennamo Yedho", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Ennamo%20Yedho%20Harris"},
        {"name": "Oh Shanthi Shanthi", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Oh%20Shanthi%20Shanthi%20Harris"},
        {"name": "Po Nee Po", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Po%20Nee%20Po%20Anirudh"},
        {"name": "Kanave Kanave", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kanave%20Kanave%20Anirudh"},
        {"name": "Idhazhin Oram", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Idhazhin%20Oram%20Anirudh"},
        {"name": "Yaanji", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/Yaanji%20Santhosh%20Narayanan"},
        {"name": "Kadhal Kan Kattudhe", "artist": "Anirudh Ravichander", "url": "https://open.spotify.com/search/Kadhal%20Kan%20Kattudhe%20Anirudh"},
        {"name": "Neeyum Naanum Anbe", "artist": "Hiphop Tamizha", "url": "https://open.spotify.com/search/Neeyum%20Naanum%20Anbe%20Hiphop"},
        {"name": "Aathangara Orathil", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Aathangara%20Orathil%20GV%20Prakash"},
        {"name": "Pookkal Pookkum", "artist": "G. V. Prakash Kumar", "url": "https://open.spotify.com/search/Pookkal%20Pookkum%20GV%20Prakash"},
        {"name": "En Jeevan", "artist": "Santhosh Narayanan", "url": "https://open.spotify.com/search/En%20Jeevan%20Santhosh%20Narayanan"},
        {"name": "Kannaana Kanney", "artist": "D. Imman", "url": "https://open.spotify.com/search/Kannaana%20Kanney%20Imman"},
        {"name": "Vaseegara", "artist": "Harris Jayaraj", "url": "https://open.spotify.com/search/Vaseegara%20Harris"},
        {"name": "Pachchai Nirame", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Pachchai%20Nirame%20AR%20Rahman"},
        {"name": "Ennavale Adi Ennavale", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Ennavale%20Adi%20Ennavale%20AR%20Rahman"},
        {"name": "Snehithane", "artist": "A.R. Rahman", "url": "https://open.spotify.com/search/Snehithane%20AR%20Rahman"},
        {"name": "Anjali Anjali", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Anjali%20Anjali%20Ilaiyaraaja"},
        {"name": "Thenpaandi Cheemayile", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Thenpaandi%20Cheemayile%20Ilaiyaraaja"},
        {"name": "Poongatru Thirumbuma", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Poongatru%20Thirumbuma%20Ilaiyaraaja"},
        {"name": "Ilaya Nila", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Ilaya%20Nila%20Ilaiyaraaja"},
        {"name": "Nila Kaigirathu", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/Nila%20Kaigirathu%20Ilaiyaraaja"},
        {"name": "En Iniya Pon Nilave", "artist": "Ilaiyaraaja", "url": "https://open.spotify.com/search/En%20Iniya%20Pon%20Nilave%20Ilaiyaraaja"},
    ],
}

# Emotion → search query mapping for Spotify API
EMOTION_QUERIES = {
    "happy":  "feel good upbeat happy songs",
    "sad":    "sad emotional heartbreak songs",
    "anger":  "rage intense rock angry songs",
    "fear":   "dark eerie haunting anxiety songs",
    "trust":  "calm soothing peaceful trust songs",
}


def _build_spotify_client():
    """Build and return an authenticated Spotipy client."""
    if not SPOTIPY_AVAILABLE:
        return None

    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        return None

    if SPOTIFY_CLIENT_ID == "7d9f5ecc33344e9cb4e92d8cb5a64db0":
        return None

    try:
        credentials = SpotifyClientCredentials(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
        )
        sp = spotipy.Spotify(auth_manager=credentials)
        # Test the connection with a lightweight call
        sp.search(q="test", limit=1, type="track")
        return sp
    except Exception:
        return None


def search_songs_by_emotion(emotion: str, limit: int = 5, prefer_fallback: bool = False, exclude_songs=None) -> dict:
    """
    Search Spotify for songs matching the detected emotion.
    Falls back to curated list if API is unavailable.

    Args:
        emotion (str): Detected emotion label
        limit   (int): Number of songs to return (max 5)
        prefer_fallback (bool): Whether to skip API and use curated list
        exclude_songs (list, optional): Song names to skip

    Returns:
        dict: {
            "songs"  : list of {name, artist, url},
            "source" : "spotify_api" | "fallback"
        }
    """
    if exclude_songs is None:
        exclude_songs = []
    exclude_lower = {str(s).lower().strip() for s in exclude_songs}

    emotion = emotion.lower().strip()
    query   = EMOTION_QUERIES.get(emotion, "feel good songs")
    sp      = _build_spotify_client()

    # helper to normalize fallback structure: extract dict entries from possibly nested lists
    def extract_dicts(x):
        out = []
        if isinstance(x, dict):
            out.append(x)
        elif isinstance(x, list):
            for item in x:
                out.extend(extract_dicts(item))
        return out

    def _filter_songs(songs):
        return [s for s in songs if str(s.get("name", "")).lower().strip() not in exclude_lower]

    # If the caller prefers the curated fallback (e.g., local Tamil lists), return cleaned fallback
    if prefer_fallback:
        fallback = FALLBACK_SONGS.get(emotion, FALLBACK_SONGS["happy"])
        cleaned = _filter_songs(extract_dicts(fallback))
        return {"songs": cleaned[:limit], "source": "fallback"}

    # ── Live Spotify API ──────────────────────────────────────
    if sp is not None:
        try:
            results = sp.search(q=query, limit=limit, type="track")
            tracks  = results.get("tracks", {}).get("items", [])

            songs = []
            for track in tracks:
                name    = track.get("name", "Unknown")
                artists = track.get("artists", [{}])
                artist  = artists[0].get("name", "Unknown") if artists else "Unknown"
                url     = track.get("external_urls", {}).get("spotify", "")

                songs.append({"name": name, "artist": artist, "url": url})

            songs = _filter_songs(songs)
            if songs:
                return {"songs": songs, "source": "spotify_api"}

        except Exception as e:
            # API call failed — fall through to fallback
            pass

    # ── Curated Fallback ──────────────────────────────────────
    fallback = FALLBACK_SONGS.get(emotion, FALLBACK_SONGS["happy"])
    cleaned = _filter_songs(extract_dicts(fallback))
    return {"songs": cleaned[:limit], "source": "fallback"}


# ── Quick test when run directly ─────────────────────────────
if __name__ == "__main__":
    result = search_songs_by_emotion("happy")
    print(f"Source: {result['source']}")
    for s in result["songs"]:
        print(f"  {s['name']} — {s['artist']}")
        print(f"  {s['url']}")

