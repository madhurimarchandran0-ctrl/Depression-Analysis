import base64
import html
import json
import os
import pickle
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pymysql
import streamlit as st

st.set_page_config(page_title="Child Depression Risk Analysis", layout="wide",
                   initial_sidebar_state="collapsed")

# =====================================================================
# STYLES  (dark Typeform look, big type, fills a desktop screen)
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&family=Noto+Sans:wght@400;500;600&display=swap');

html { font-size: 20px; }
html, body, .stApp { font-family: 'Inter', 'Noto Sans', sans-serif; color: #f4f1f7; }
h1, h2, h3, h4 { font-family: 'Fraunces', serif !important; font-weight: 400 !important; color: #fff; letter-spacing: -0.01em; }

.stApp {
    background:
        radial-gradient(ellipse 130% 55% at 15% 105%, rgba(226,160,255,0.95) 0%, rgba(138,64,206,0.70) 38%, transparent 72%),
        radial-gradient(ellipse 70% 45% at 105% 75%, rgba(150,70,230,0.55), transparent 70%),
        #252224 !important;
    background-attachment: fixed !important;
}
header[data-testid="stHeader"], footer, #MainMenu { display: none !important; }
.block-container { max-width: 100% !important; padding: 1.6rem 4.5rem 3rem 4.5rem !important; }

/* ---------- top bar ---------- */
.brand { display: flex; align-items: center; gap: 0.7rem; font-size: 1.7rem; font-weight: 500; color: #fff; }
.brand .logo { width: 2.1rem; height: 1.4rem; background: #fff; border-radius: 0.45rem; display: inline-block; }
.pill { background: #fff; color: #1d1b1e; padding: 0.55rem 1.5rem; border-radius: 0.7rem; font-weight: 500; font-size: 1.05rem; text-align: center; }
.progress { height: 6px; background: rgba(255,255,255,0.16); border-radius: 6px; margin-bottom: 1.6rem; }
.progress > div { height: 100%; background: #fff; border-radius: 6px; }

/* ---------- hero ---------- */
.hero h1 { font-size: clamp(3.4rem, 6.2vw, 6.4rem); line-height: 1.02; margin: 0.4rem 0 1.4rem 0; }
.hero p { font-size: 1.5rem; line-height: 1.55; max-width: 44rem; color: #f1eaf6; margin-bottom: 1.8rem; }
.mock {
    background: #f7f9df; color: #1c2a1a; border-radius: 1.6rem; padding: 2rem; border: 6px solid #3a373b;
    font-size: 1.2rem; line-height: 1.5; box-shadow: 0 20px 60px rgba(0,0,0,0.35);
}
.mock b { font-family: 'Fraunces', serif; font-size: 2rem; font-weight: 600; display: block; margin-bottom: 0.6rem; }
.hero-img { width: 100%; max-height: 26rem; object-fit: cover; border-radius: 1.6rem; }

.section-title { font-size: 2.3rem; margin: 2.6rem 0 1.2rem 0; }

/* ---------- numbered cards (whole card is clickable) ---------- */
.qcard {
    background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(28,10,48,0.62) 100%);
    border: 1px solid rgba(255,255,255,0.20); border-radius: 1.6rem;
    padding: 1.5rem 1.8rem 1.6rem 1.8rem; min-height: 15rem; transition: border-color .2s, transform .2s;
}
.qcard .num { font-size: 1.05rem; opacity: 0.85; margin-bottom: 2.4rem; }
.qcard h3 { font-size: 2.3rem; margin: 0 0 0.5rem 0; }
.qcard p { font-size: 1.2rem; line-height: 1.45; margin: 0; color: #efe7f5; }
.qcard.static { background: rgba(255,255,255,0.92); color: #1d1b1e; }
.qcard.static h3, .qcard.static p, .qcard.static .num { color: #1d1b1e; }

[class*="st-key-card_"] { position: relative; margin-bottom: 1.2rem; }
[class*="st-key-card_"] [data-testid="stElementContainer"] { position: static; }
[class*="st-key-card_"] div.stButton { position: absolute; inset: 0; z-index: 5; }
[class*="st-key-card_"] div.stButton > button { width: 100%; height: 100%; opacity: 0; cursor: pointer; }
[class*="st-key-card_"]:hover .qcard { border-color: #fff; transform: translateY(-4px); }

/* ---------- question page ---------- */
.crumb { font-size: 1.15rem; opacity: 0.85; margin-bottom: 0.4rem; }
.page-title { font-size: clamp(3rem, 5vw, 5.2rem); line-height: 1.05; margin: 0 0 1.6rem 0; }
.essay { margin-bottom: 2rem; max-width: 62rem; }
.essay h3 { font-size: 1.9rem; margin: 0 0 0.6rem 0; }
.essay p { font-size: 1.3rem; line-height: 1.75; color: #f1eaf6; margin: 0; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr)); gap: 1.1rem; margin-top: 0.6rem; }
.stat { background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.20); border-radius: 1.3rem; padding: 1.3rem 1.5rem; }
.stat .big { font-family: 'Fraunces', serif; font-size: 3.2rem; line-height: 1.05; color: #f0cfff; margin-bottom: 0.5rem; }
.stat .cap { font-size: 1.05rem; line-height: 1.5; color: #f1eaf6; }
.source { font-size: 0.9rem; opacity: 0.7; margin-top: 0.9rem; }

.st-key-inputpanel, .st-key-resultpanel {
    background: rgba(20,8,36,0.55); border: 1px solid rgba(255,255,255,0.22);
    border-radius: 1.6rem; padding: 1.8rem 2rem; backdrop-filter: blur(6px);
}
.panel-title { font-family: 'Fraunces', serif; font-size: 1.9rem; margin-bottom: 0.4rem; }
.quote { font-family: 'Fraunces', serif; font-size: 1.45rem; line-height: 1.5; border-left: 5px solid #e3b6ff; padding: 0.3rem 0 0.3rem 1.2rem; margin: 1.6rem 0 0.4rem 0; }
.side-img { width: 100%; border-radius: 1.3rem; margin-top: 1.2rem; }
.small { font-size: 1rem; opacity: 0.85; line-height: 1.5; }
.phq-q { font-size: 1.25rem; margin: 1.1rem 0 0.1rem 0; }

/* ---------- widgets ---------- */
label p, [data-testid="stWidgetLabel"] p { font-size: 1.2rem !important; font-weight: 500; }
div[data-testid="stRadio"] label p { font-size: 1.05rem !important; }
div[data-baseweb="input"], div[data-baseweb="select"] > div, div[data-baseweb="base-input"] {
    background-color: rgba(255,255,255,0.10) !important; border-radius: 0.8rem !important; border-color: rgba(255,255,255,0.28) !important;
}
input { font-size: 1.3rem !important; color: #fff !important; }

div.stButton > button {
    border-radius: 999px; font-weight: 500; font-size: 1.1rem; padding: 0.7rem 2rem;
    background: rgba(255,255,255,0.10); color: #fff; border: 1px solid rgba(255,255,255,0.35); transition: 0.2s;
}
div.stButton > button:hover { background: rgba(255,255,255,0.22); border-color: #fff; color: #fff; }
div.stButton > button[kind="primary"] { background: #fff; color: #1d1b1e; border: none; }
div.stButton > button[kind="primary"]:hover { background: #f0cfff; color: #1d1b1e; }
div.stButton > button:disabled { opacity: 0.4; }

/* ---------- scale help ---------- */
[data-testid="stExpander"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    border-radius: 1rem !important;
    margin-top: 0.8rem;
}
[data-testid="stExpander"] summary p { font-size: 1.1rem !important; font-weight: 500; color: #f0cfff; }
.scale-title { font-family: 'Fraunces', serif; font-size: 1.35rem; margin: 1rem 0 0.4rem 0; color: #fff; }
.scale-intro { font-size: 1.05rem; line-height: 1.55; margin-bottom: 0.7rem; }
.scale { width: 100%; border-collapse: collapse; font-size: 1.05rem; }
.scale td { padding: 0.5rem 0.3rem; border-bottom: 1px solid rgba(255,255,255,0.16); vertical-align: top; line-height: 1.4; }
.scale td:first-child { font-weight: 600; color: #f0cfff; white-space: nowrap; padding-right: 0.8rem; }
.scale-note { font-size: 0.95rem; opacity: 0.8; margin-top: 0.7rem; line-height: 1.5; }

/* ---------- analysis ---------- */
.review { width: 100%; border-collapse: collapse; font-size: 1.25rem; }
.review td { padding: 0.8rem 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.16); }
.review td:last-child { text-align: right; font-weight: 600; color: #f0cfff; }
.result { border-radius: 1.4rem; padding: 1.6rem; text-align: center; margin-top: 1rem; }
.result .score { font-family: 'Fraunces', serif; font-size: 5.5rem; line-height: 1; }
.result .msg { font-size: 1.35rem; margin-top: 0.6rem; line-height: 1.5; }
.safe { background: rgba(46,204,113,0.18); border: 1px solid #2ecc71; color: #8df0b4; }
.moderate { background: rgba(241,196,15,0.18); border: 1px solid #f1c40f; color: #ffe27a; }
.danger { background: rgba(231,76,60,0.20); border: 1px solid #e74c3c; color: #ff9d92; }

/* ---------- care guide ---------- */
.care-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(22rem, 1fr)); gap: 1.2rem; margin-bottom: 1.4rem; }
.care { background: rgba(255,255,255,0.10); border: 1px solid rgba(255,255,255,0.22); border-radius: 1.4rem; padding: 1.5rem 1.7rem; }
.care h3 { font-size: 1.7rem; margin: 0 0 0.7rem 0; }
.care ul { margin: 0; padding-left: 1.2rem; font-size: 1.15rem; line-height: 1.7; }
.care.avoid { border-color: rgba(255,157,146,0.7); }
.urgent { background: rgba(231,76,60,0.22); border: 1px solid #e74c3c; border-radius: 1.4rem; padding: 1.4rem 1.8rem; font-size: 1.3rem; line-height: 1.6; margin-bottom: 1.4rem; }
.helplines { background: #fff; color: #1d1b1e; border-radius: 1.4rem; padding: 1.4rem 1.8rem; font-size: 1.25rem; line-height: 1.7; margin-top: 0.6rem; }
.helplines b { font-family: 'Fraunces', serif; font-size: 1.5rem; font-weight: 600; }

.footer { margin-top: 3rem; font-size: 1rem; line-height: 1.7; color: #e6dcee; border-top: 1px solid rgba(255,255,255,0.22); padding-top: 1.2rem; }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# LANGUAGES  (every language Google Translate supports, shown in its own script)
# Translation uses only the Python standard library, so nothing extra to install.
# =====================================================================
LANGS = {
    "en": "English", "af": "Afrikaans", "sq": "Shqip (Albanian)", "am": "አማርኛ (Amharic)", "ar": "العربية (Arabic)",
    "hy": "Հայերեն (Armenian)", "az": "Azərbaycan (Azerbaijani)", "eu": "Euskara (Basque)", "be": "Беларуская (Belarusian)",
    "bn": "বাংলা (Bengali)", "bs": "Bosanski (Bosnian)", "bg": "Български (Bulgarian)", "ca": "Català (Catalan)",
    "ceb": "Cebuano", "zh-CN": "中文 简体 (Chinese Simplified)", "zh-TW": "中文 繁體 (Chinese Traditional)",
    "co": "Corsu (Corsican)", "hr": "Hrvatski (Croatian)", "cs": "Čeština (Czech)", "da": "Dansk (Danish)",
    "nl": "Nederlands (Dutch)", "eo": "Esperanto", "et": "Eesti (Estonian)", "fi": "Suomi (Finnish)",
    "fr": "Français (French)", "fy": "Frysk (Frisian)", "gl": "Galego (Galician)", "ka": "ქართული (Georgian)",
    "de": "Deutsch (German)", "el": "Ελληνικά (Greek)", "gu": "ગુજરાતી (Gujarati)", "ht": "Kreyòl Ayisyen (Haitian Creole)",
    "ha": "Hausa", "haw": "ʻŌlelo Hawaiʻi (Hawaiian)", "iw": "עברית (Hebrew)", "hi": "हिन्दी (Hindi)", "hmn": "Hmong",
    "hu": "Magyar (Hungarian)", "is": "Íslenska (Icelandic)", "ig": "Igbo", "id": "Bahasa Indonesia (Indonesian)",
    "ga": "Gaeilge (Irish)", "it": "Italiano (Italian)", "ja": "日本語 (Japanese)", "jw": "Basa Jawa (Javanese)",
    "kn": "ಕನ್ನಡ (Kannada)", "kk": "Қазақша (Kazakh)", "km": "ខ្មែរ (Khmer)", "rw": "Kinyarwanda", "ko": "한국어 (Korean)",
    "ku": "Kurdî (Kurdish)", "ky": "Кыргызча (Kyrgyz)", "lo": "ລາວ (Lao)", "la": "Latina (Latin)", "lv": "Latviešu (Latvian)",
    "lt": "Lietuvių (Lithuanian)", "lb": "Lëtzebuergesch (Luxembourgish)", "mk": "Македонски (Macedonian)",
    "mg": "Malagasy", "ms": "Bahasa Melayu (Malay)", "ml": "മലയാളം (Malayalam)", "mt": "Malti (Maltese)",
    "mi": "Māori", "mr": "मराठी (Marathi)", "mn": "Монгол (Mongolian)", "my": "မြန်မာ (Myanmar Burmese)",
    "ne": "नेपाली (Nepali)", "no": "Norsk (Norwegian)", "ny": "Chichewa", "or": "ଓଡ଼ିଆ (Odia)", "ps": "پښتو (Pashto)",
    "fa": "فارسی (Persian)", "pl": "Polski (Polish)", "pt": "Português (Portuguese)", "pa": "ਪੰਜਾਬੀ (Punjabi)",
    "ro": "Română (Romanian)", "ru": "Русский (Russian)", "sm": "Gagana Samoa (Samoan)", "gd": "Gàidhlig (Scots Gaelic)",
    "sr": "Српски (Serbian)", "st": "Sesotho", "sn": "Shona", "sd": "سنڌي (Sindhi)", "si": "සිංහල (Sinhala)",
    "sk": "Slovenčina (Slovak)", "sl": "Slovenščina (Slovenian)", "so": "Soomaali (Somali)", "es": "Español (Spanish)",
    "su": "Basa Sunda (Sundanese)", "sw": "Kiswahili (Swahili)", "sv": "Svenska (Swedish)", "tl": "Filipino (Tagalog)",
    "tg": "Тоҷикӣ (Tajik)", "ta": "தமிழ் (Tamil)", "tt": "Татар (Tatar)", "te": "తెలుగు (Telugu)", "th": "ไทย (Thai)",
    "tr": "Türkçe (Turkish)", "tk": "Türkmen (Turkmen)", "uk": "Українська (Ukrainian)", "ur": "اردو (Urdu)",
    "ug": "ئۇيغۇرچە (Uyghur)", "uz": "Oʻzbek (Uzbek)", "vi": "Tiếng Việt (Vietnamese)", "cy": "Cymraeg (Welsh)",
    "xh": "isiXhosa (Xhosa)", "yi": "ייִדיש (Yiddish)", "yo": "Yorùbá", "zu": "isiZulu (Zulu)",
}
RTL = {"ar", "fa", "ur", "iw", "ps", "sd", "ug", "yi"}
LANG_CODE = st.session_state.get("lang_code", "en")
TR_DIR = "translations"


@st.cache_resource
def tr_store(code):
    try:
        with open(f"{TR_DIR}/{code}.json", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


STORE = tr_store(LANG_CODE)
PENDING = set()
FAILED = st.session_state.get("tr_fail") == LANG_CODE


def t(s, **kw):
    """English text -> selected language (saved on disk after the first time). Plain text only."""
    s = str(s)
    if LANG_CODE != "en" and not FAILED and any(c.isalpha() for c in s):
        if s in STORE:
            s = STORE[s]
        else:
            PENDING.add(s)
    if kw:
        s = re.sub(r"\{\s*(\w+)\s*\}", lambda m: str(kw.get(m.group(1), m.group(0))), s)
    return s


def th(s, **kw):
    """Translated and safe to place inside HTML."""
    return html.escape(t(s, **kw), quote=False)


def _translate_one(s):
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": LANG_CODE, "dt": "t", "q": s})
    for _ in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode("utf-8"))
            return "".join(seg[0] for seg in data[0] if seg[0])
        except Exception:
            time.sleep(0.4)
    return None


def flush_pending():
    """Translate whatever the page needed and did not have yet, save it, refresh once."""
    if not PENDING:
        return
    todo = list(PENDING)
    with st.spinner("🌐 Translating..."):
        with ThreadPoolExecutor(8) as ex:
            results = list(ex.map(_translate_one, todo))
    ok = {s: r for s, r in zip(todo, results) if r}
    for s in todo:
        STORE[s] = ok.get(s, s)
    if not ok:
        st.session_state.tr_fail = LANG_CODE
        st.warning("The translation service could not be reached, so English is shown. Check the internet connection.")
        return
    os.makedirs(TR_DIR, exist_ok=True)
    with open(f"{TR_DIR}/{LANG_CODE}.json", "w", encoding="utf-8") as f:
        json.dump({k: v for k, v in STORE.items() if v != k}, f, ensure_ascii=False)
    st.rerun()


if LANG_CODE in RTL:
    st.markdown("<style>.block-container{direction:rtl;text-align:right}"
                ".review td:last-child{text-align:left}</style>", unsafe_allow_html=True)

# =====================================================================
# DATABASE + MODEL
# =====================================================================
@st.cache_resource
def get_db():
    return pymysql.connect(host=os.getenv("DB_HOST", "localhost"), user=os.getenv("DB_USER", "root"),
                           password=os.getenv("DB_PASS", "1234"), db=os.getenv("DB_NAME", "depression_db"))


@st.cache_resource
def load_models():
    with open('rf_depression_model.sav', 'rb') as f:
        rf = pickle.load(f)
    with open('scaler_depression.sav', 'rb') as f:
        scaler = pickle.load(f)
    return rf, scaler


COUNTRIES = ['Argentina', 'Bangladesh', 'Brazil', 'India', 'Indonesia', 'Jordan', 'Kenya', 'Philippines']
COUNTRY_OPTIONS = COUNTRIES + ["Other"]   # "Other" switches on no country column, so the model is less certain

# (organisation, what it offers, number). Please confirm every number locally before publishing.
HELP = {
    "India": {"emergency": "112", "lines": [("Tele-MANAS", "free mental health support, 24x7", "14416"),
                                            ("Childline", "free helpline for children", "1098")]},
    "Bangladesh": {"emergency": "999", "lines": [("Child Helpline", "free helpline for children", "1098")]},
    "Brazil": {"emergency": "192", "lines": [("CVV", "free emotional support", "188"),
                                             ("Disque 100", "child rights helpline", "100")]},
    "Argentina": {"emergency": "911", "lines": [("Línea 135", "crisis support (Buenos Aires area)", "135"),
                                                ("Línea 102", "children's rights helpline", "102")]},
    "Indonesia": {"emergency": "112", "lines": [("Healing 119", "mental health support (ext. 8)", "119"),
                                                ("SAPA", "child protection helpline", "129")]},
    "Jordan": {"emergency": "911", "lines": [("Family Protection", "child and family protection", "110")]},
    "Kenya": {"emergency": "999", "lines": [("Childline Kenya", "free helpline for children", "116"),
                                            ("Kenya Red Cross", "free counselling", "1199")]},
    "Philippines": {"emergency": "911", "lines": [("NCMH Crisis Hotline", "mental health crisis support", "1553"),
                                                  ("Bantay Bata", "child helpline", "163")]},
}
HELP_OTHER = {"emergency": "your local emergency number", "lines": []}
FIND_HELP = "findahelpline.com"

# =====================================================================
# IMAGES (optional). Paste a web URL, or leave empty to use the local jpg.
# =====================================================================
WEB_IMAGES = {"hero": "", "right": ""}
LOCAL_IMAGES = {"hero": "depression1.jpg", "right": "depression3.jpg"}


@st.cache_data
def img_tag(key, css_class="side-img"):
    url = WEB_IMAGES[key].strip()
    if not url:
        try:
            with open(LOCAL_IMAGES[key], "rb") as f:
                url = "data:image/jpeg;base64," + base64.b64encode(f.read()).decode()
        except Exception:
            return ""
    return f'<img src="{url}" class="{css_class}">'


# =====================================================================
# CONTENT  (edit the English text here, every language is made from it)
# =====================================================================
QUESTIONS = [
    {"key": "Gender", "label": "Gender",
     "short": "Depression can look different in girls and boys.",
     "why": "Depression does not look the same in every child. After puberty, girls report depression more often and tend to describe sadness, worry and low self-worth. Boys are more likely to show irritability, anger or withdrawal, which adults often mistake for bad behaviour. Asking about gender lets the screening read the other answers in the right context, and reminds the caregiver which signs to look for.",
     "how": "Gender is passed to the model as a simple 0 or 1 value. The KNN model then compares the child with the closest matching records in its training data, so patterns that are typical for girls or for boys are compared like with like.",
     "stats": [("1 in 7", "children and teenagers aged 10 to 19 live with a mental disorder (WHO)"),
               ("Up to 2x", "girls report depressive symptoms about twice as often as boys after puberty in many national surveys"),
               ("Boys", "die by suicide more often than girls in most regions, even though girls report more depression (WHO)")],
     "quote": "Care that listens to the child, not the stereotype, heals faster."},
    {"key": "Age", "label": "Age",
     "short": "Half of all mental health conditions begin by age 14.",
     "why": "Needs and risks change a great deal between 10 and 17. A ten-year-old and a sixteen-year-old face very different pressures, from early school transitions to exams, identity and social media. Because most mental health conditions start in these years, age is one of the most important parts of reading risk correctly.",
     "how": "Age is rescaled by the trained scaler so that it sits on the same numeric range as the other measurements. The KNN model then finds children of a similar age in the training data and checks how many of them were classed as depressed.",
     "stats": [("50%", "of all mental health conditions start by age 14 (WHO)"),
               ("75%", "start by the mid-20s, so the teenage years are the window for early help"),
               ("3rd", "leading cause of death among 15 to 29 year olds is suicide (WHO)")],
     "quote": "Early care costs a conversation. Late care costs years."},
    {"key": "Country", "label": "Country",
     "short": "Culture, schools and access to care differ by country.",
     "why": "Family structure, school systems, stigma and access to care are very different from one country to another. A child in Kerala, in Nairobi and in Buenos Aires may show the same sadness but have very different support around them. The model was trained on data from eight countries, so location lets it compare the child with peers who live in a similar setting.",
     "how": "The country is turned into eight yes/no columns, one for each country in the training data. The selected country is marked 1 and the others 0, so the KNN model prefers neighbours from the same country when it measures distance.",
     "stats": [("~90%", "of the world's children and adolescents live in low and middle income countries (UNICEF, WHO)"),
               ("~2%", "of government health budgets goes to mental health in the median country (WHO Mental Health Atlas)"),
               ("13", "mental health workers per 100,000 people worldwide, and far fewer in poorer countries (WHO)")],
     "quote": "Mental health has no borders."},
    {"key": "Sleep", "label": "Sleep Hours",
     "short": "Sleep changes are often the earliest warning sign.",
     "why": "Sleep and mood are tightly linked. Too little sleep weakens focus, emotional control and immunity, and sleeping far too much can signal low mood or withdrawal. Parents usually notice a change in sleep long before a child says anything about how they feel, which makes it one of the most useful early signals.",
     "how": "Sleep hours are rescaled and compared with those of the children in the training data. Children who sleep far outside the usual range for their age tend to sit closer to neighbours who were labelled as depressed, which raises the risk score.",
     "stats": [("8 to 10 h", "of sleep recommended for teenagers aged 13 to 17 (American Academy of Sleep Medicine)"),
               ("9 to 12 h", "recommended for children aged 6 to 12"),
               ("2x", "higher risk of later depression in people with persistent insomnia (meta-analysis)")],
     "quote": "When sleep disappears, small worries become big ones."},
    {"key": "ParentRelationship", "label": "Parent Relationship",
     "short": "A warm bond at home is a strong protection.",
     "why": "A warm, open bond with parents or caregivers is one of the strongest protections for a child's mental health. Children who feel heard at home are more likely to speak up early. Constant conflict, harsh discipline or emotional distance can quietly raise the risk of depression, even when everything looks fine from outside.",
     "how": "The 1 to 10 score is rescaled and used directly as a feature. A low score moves the child closer to training records with weaker family bonds, and in the data those records were more often labelled as depressed.",
     "stats": [("Strongest", "family connectedness is among the strongest protective factors against teenage depression and suicidal thoughts (CDC)"),
               ("Proven", "parenting programmes reduce harsh parenting and child maltreatment (WHO INSPIRE)")],
     "quote": "Children don't need perfect parents. They need present ones."},
    {"key": "SocialSupport", "label": "Social Support",
     "short": "Friends, relatives and teachers form a safety net.",
     "why": "Friends, relatives, teachers and neighbours form a safety net around a child. Children who feel supported by the people around them cope better with stress and recover faster from hard times. Loneliness does the opposite: it makes small problems feel permanent.",
     "how": "The 1 to 10 social support score is rescaled and fed to the model. Higher support pulls the child toward neighbours in the training data who were not depressed, which lowers the risk score.",
     "stats": [("17 to 21%", "of 13 to 29 year olds feel lonely, the highest rate of any age group (WHO Commission on Social Connection)"),
               ("1 in 6", "people worldwide are affected by loneliness (WHO)")],
     "quote": "One kind friend can change a hard year."},
    {"key": "AceHousehold", "label": "ACE Household",
     "short": "Hard experiences at home raise later risk.",
     "why": "Adverse Childhood Experiences, or ACEs, are stressful events at home such as violence, substance misuse, or a parent with mental illness. The more ACEs a child has faced, the higher the lifetime risk of depression. The risk is not a sentence: one stable, caring adult and early support can greatly reduce the impact.",
     "how": "The ACE household count is rescaled and used by the model together with the other ACE values. A higher count moves the child toward training records of children who went through similar hardship and were more often depressed.",
     "stats": [("44%", "of adult depression cases could potentially be avoided by preventing ACEs (CDC)"),
               ("Up to 1 billion", "children aged 2 to 17 experience violence every year (WHO)")],
     "quote": "What happens to a child is not who the child is."},
    {"key": "Bullied", "label": "Bullied in last 30 days",
     "short": "Repeated bullying is a major risk factor.",
     "why": "Bullying damages self-worth, sleep and school life. Repeated bullying is a major risk factor for depression, anxiety and self-harm, and many children never tell an adult. Asking about the last 30 days shows whether the harm is happening right now and still needs to be stopped.",
     "how": "The bullying value is passed to the model as entered. A higher value puts the child closer to training records of children who were bullied and who more often had a depression label.",
     "stats": [("1 in 3", "students were bullied at least once in the past month (UNESCO)"),
               ("1 in 6", "school-aged children have experienced cyberbullying (WHO / HBSC)"),
               ("Higher", "bullied children have a clearly higher risk of depression and self-harm (meta-analyses)")],
     "quote": "Silence protects the bully. Speaking up protects the child."},
    {"key": "TrustedAdult", "label": "Has Trusted Adult",
     "short": "One trusted adult can change the outcome.",
     "why": "Having at least one adult to talk to is among the most powerful protective factors in childhood. It gives a child someone to turn to before small struggles become serious ones. This can be a parent, a teacher, a relative or a counsellor. What matters is that the child believes this person will listen.",
     "how": "The value is passed to the model as entered. In the training data, children with a trusted adult were less often labelled depressed, so a higher value moves the child toward the lower risk group.",
     "stats": [("1 adult", "is enough to buffer the effects of childhood adversity (Harvard Center on the Developing Child)")],
     "quote": "Be the person you needed when you were young."},
]
QMAP = {q["key"]: q for q in QUESTIONS}
ORDER = [q["key"] for q in QUESTIONS] + ["Clinical", "Analysis", "Care"]
STAT_NOTE = "Figures are rounded and summarised from WHO, UNICEF, UNESCO and CDC publications. Please check the latest reports before quoting them."

# ---------------------------------------------------------------------
# What do the numbers mean?  (shown in the "What do these numbers mean?" box)
# NOTE: check the Bullied and TrustedAdult ranges against how those
# columns were encoded in your training data and edit the text to match.
# ---------------------------------------------------------------------
SCALE_HELP = {
    "Age": {
        "intro": "The child's age in completed years. The screening is designed for ages 10 to 17.",
        "rows": [("10 to 12", "Younger child, early school years"),
                 ("13 to 15", "Early teenage years"),
                 ("16 to 17", "Older teenager")],
    },
    "Sleep": {
        "intro": "Average hours the child actually sleeps per night on school days. You can use half hours (for example 6.5).",
        "rows": [("Below 6", "Very little sleep"),
                 ("7 to 9", "Usually healthy for most children"),
                 ("10 or more", "Sleeping a lot, which can also be a warning sign")],
    },
    "ParentRelationship": {
        "intro": "How close and open is the child's relationship with their parents or main caregivers? Rate it from 1 to 10.",
        "rows": [("1 to 2", "Very poor. Constant conflict, fear or no communication"),
                 ("3 to 4", "Weak. Often tense, or the child rarely talks to them"),
                 ("5 to 6", "Average. Some good days and some difficult ones"),
                 ("7 to 8", "Good. The child usually feels heard and supported"),
                 ("9 to 10", "Very strong. Warm, open and trusting")],
    },
    "SocialSupport": {
        "intro": "How many people (friends, relatives, teachers, neighbours) does the child feel they can count on? Rate it from 1 to 10.",
        "rows": [("1 to 2", "Almost no one. The child feels alone"),
                 ("3 to 4", "One or two people, but not very reliable"),
                 ("5 to 6", "A few friends or relatives to turn to"),
                 ("7 to 8", "Several people who care and help"),
                 ("9 to 10", "A strong circle of support")],
    },
    "AceHousehold": {
        "intro": "Count how many of these hard experiences have happened at home. Add 1 for each one that applies.",
        "rows": [("Examples", "Violence at home, a parent with mental illness, drug or alcohol misuse, a parent in jail, "
                              "separation or divorce, the death of a parent, serious conflict"),
                 ("0", "None of these"),
                 ("1 to 2", "Some hardship"),
                 ("3 or more", "A lot of hardship. Raises the risk and needs extra support")],
    },
    "Bullied": {
        "intro": "How much has the child been bullied in the last 30 days (teased, hit, excluded or threatened)?",
        "rows": [("0", "Not bullied at all"),
                 ("1 to 30", "Rarely or mildly"),
                 ("31 to 70", "Often"),
                 ("71 to 100", "Almost every day, or very severe")],
    },
    "TrustedAdult": {
        "intro": "Does the child have an adult they can talk to when something is wrong (a parent, teacher, relative or counsellor)?",
        "rows": [("0", "No. The child has nobody to talk to"),
                 ("1 to 50", "Maybe. Someone, but the child is not sure they would listen"),
                 ("51 to 100", "Yes. The child clearly has someone they trust")],
    },
}

SCALE_NOTE = "If you are unsure, pick the closest value. An honest estimate is better than leaving the default."

CARE = {
    "Low": {
        "title": "Keep protecting their wellbeing",
        "intro": "The screening did not find strong warning signs. This is the best time to build habits that keep it that way.",
        "home": ["Eat at least one meal together each day, without phones.",
                 "Ask open questions such as \"What was the best and hardest part of your day?\"",
                 "Keep a steady sleep time, and keep screens out of the bedroom at night.",
                 "Make time for play, sport and friends every week."],
        "school": ["Tell a teacher or school counsellor who the child can go to.",
                   "Watch for changes in marks, attendance or friendships.",
                   "Support clubs and activities the child enjoys."],
        "pro": ["No treatment is needed from this screening alone.",
                "Repeat the screening if you notice changes in mood, sleep or behaviour.",
                "Visit a paediatrician or counsellor if you are worried at any time."],
        "avoid": ["Ignoring a sudden change because the score was low.",
                  "Comparing the child with other children."],
    },
    "Moderate": {
        "title": "Early warning signs: act now, gently",
        "intro": "Some risk factors are present. Children at this stage often recover well when adults notice early and respond with care.",
        "home": ["Choose a calm moment and say what you have noticed, for example \"You seem tired lately. I'm here if you want to talk.\"",
                 "Listen without fixing, judging or lecturing. Let the child finish.",
                 "Rebuild routines: regular sleep, meals, daylight and movement.",
                 "Reduce pressure for a few weeks and celebrate small efforts.",
                 "Check in every day for a few minutes, even when the child says nothing is wrong."],
        "school": ["Meet the class teacher or school counsellor and share your concern.",
                   "Ask whether bullying, exam stress or a friendship problem is involved.",
                   "Agree a quiet plan for support at school, such as a person to approach when upset."],
        "pro": ["Book a visit with a paediatrician, child psychologist or counsellor within the next few weeks.",
                "Call a local helpline for free advice on what to do next (the numbers are shown on this page).",
                "Repeat this screening in 2 to 4 weeks to see if things are improving."],
        "avoid": ["Saying \"it's just a phase\" or \"be strong\".",
                  "Punishing low mood, tiredness or falling marks.",
                  "Waiting for the child to ask for help on their own."],
    },
    "High": {
        "title": "High risk: get professional help soon",
        "intro": "Several strong risk indicators are present. This is not a diagnosis, but it is a clear signal that the child should be seen by a professional as soon as possible.",
        "home": ["Stay close and calm. Tell the child: \"I'm worried about you, I love you, and we will get help together.\"",
                 "Ask directly and kindly whether the child has thoughts of self-harm. Asking does not put the idea in their head.",
                 "Do not leave the child alone for long periods while you arrange help.",
                 "Safely lock away medicines, sharp objects and anything else that could be used to self-harm.",
                 "Keep routines simple: sleep, food, water and company."],
        "school": ["Inform the school counsellor or a trusted teacher so that the child is supported during the day.",
                   "Ask for flexibility with homework and exams while the child is being treated.",
                   "Report any bullying to the school in writing."],
        "pro": ["Book an appointment with a child psychiatrist, psychologist or doctor this week.",
                "Call a local helpline for guidance and referrals (the numbers are shown on this page).",
                "Treatment may include talking therapy, family support and, when a doctor decides, medicine.",
                "Follow the treatment plan and go to every follow-up."],
        "avoid": ["Leaving the child alone with their thoughts.",
                  "Blaming the child, or blaming yourself. Blame delays help.",
                  "Waiting to see if it passes by itself.",
                  "Giving any medicine that was not prescribed for the child."],
    },
}

# =====================================================================
# CLINICAL QUESTIONNAIRE  (PHQ-A style, adapted from the PHQ-9 used with teenagers)
# =====================================================================
PHQ_INTRO = ("This is a short clinical screening questionnaire based on the PHQ-9 and its teenage version, the PHQ-A. "
             "Doctors and schools around the world use it. The child can answer it, or a parent can answer it together "
             "with the child. Think about the last 2 weeks.")
PHQ_ITEMS = [
    "Little interest or pleasure in doing things",
    "Feeling down, sad, irritable or hopeless",
    "Trouble falling asleep or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite, or eating much more than usual",
    "Feeling bad about yourself, or feeling like a failure or that you let people down",
    "Trouble concentrating on things such as schoolwork, reading or watching TV",
    "Moving or speaking so slowly that others noticed, or being so restless that you move around much more than usual",
    "Thoughts that you would be better off dead, or of hurting yourself in some way",
]
PHQ_OPTS = ["Not at all", "Several days", "More than half the days", "Nearly every day"]
PHQ_DIFF = ["Not difficult at all", "Somewhat difficult", "Very difficult", "Extremely difficult"]
PHQ_DIFF_Q = "How difficult have these problems made it to do schoolwork, take care of things at home or get along with people?"
PHQ_BANDS = [(4, "Minimal or no symptoms"), (9, "Mild symptoms"), (14, "Moderate symptoms"),
             (19, "Moderately severe symptoms"), (27, "Severe symptoms")]
RANK = {"Low": 0, "Moderate": 1, "High": 2}
CSS_OF = {"Low": "safe", "Moderate": "moderate", "High": "danger"}

# =====================================================================
# SESSION STATE
# =====================================================================
st.session_state.setdefault("page", "home")
st.session_state.setdefault("result", None)
st.session_state.setdefault("phq_done", False)
st.session_state.setdefault("answers", {
    "Gender": "Female", "Age": 13, "Country": "Argentina", "Sleep": 7.0,
    "ParentRelationship": 3, "SocialSupport": 3, "AceHousehold": 0,
    "Bullied": 0, "TrustedAdult": 1, "phq": [0] * 9, "phq_diff": 0})
ans = st.session_state.answers


def go(page):
    st.session_state.page = page


def go_step(step):
    i = ORDER.index(st.session_state.page) + step
    st.session_state.page = ORDER[max(0, min(len(ORDER) - 1, i))]


def finish_clinical():
    st.session_state.phq_done = True
    go("Analysis")


# =====================================================================
# CLINICAL + HELPLINE LOGIC
# =====================================================================
def phq_total():
    return sum(ans["phq"])


def phq_band():
    return next(label for top, label in PHQ_BANDS if phq_total() <= top)


def clinical_risk():
    """None until the questionnaire has been completed."""
    if not st.session_state.phq_done:
        return None
    if phq_total() >= 15 or ans["phq"][8] > 0:
        return "High"
    return "Moderate" if phq_total() >= 10 else "Low"


def final_risk(res):
    c = clinical_risk()
    return max(res["risk"], c, key=RANK.get) if c else res["risk"]


def helpinfo():
    return HELP.get(ans["Country"], HELP_OTHER)


def help_text():
    info = helpinfo()
    parts = [f'{html.escape(o)} <b>{n}</b> ({th(d)})' for o, d, n in info["lines"]]
    parts.append(f'{th("Emergency")} <b>{html.escape(info["emergency"])}</b>')
    return " | ".join(parts)


# =====================================================================
# INPUT WIDGETS
# =====================================================================
def render_input(key):
    k = f"w_{key}"
    if key == "Gender":
        opts = ['Female', 'Male']
        ans[key] = st.selectbox(t('Gender'), opts, index=opts.index(ans[key]), key=k, format_func=t)
    elif key == "Age":
        ans[key] = st.number_input(t('Age (10 to 17)'), 10, 17, int(ans[key]), key=k)
    elif key == "Country":
        ans[key] = st.selectbox(t('Country'), COUNTRY_OPTIONS, index=COUNTRY_OPTIONS.index(ans[key]), key=k, format_func=t)
        if ans[key] == "Other":
            st.caption(t("This country is not in the training data, so the result is less certain."))
    elif key == "Sleep":
        ans[key] = st.number_input(t('Sleep hours per night'), 2.0, 12.0, float(ans[key]), step=0.5, key=k)
    elif key == "ParentRelationship":
        ans[key] = st.number_input(t('Parent relationship (1 to 10)'), 1, 10, int(ans[key]), key=k)
    elif key == "SocialSupport":
        ans[key] = st.number_input(t('Social support (1 to 10)'), 1, 10, int(ans[key]), key=k)
    elif key == "AceHousehold":
        ans[key] = st.number_input(t('ACE household (0 to 10)'), 0, 10, int(ans[key]), key=k)
    elif key == "Bullied":
        ans[key] = st.number_input(t('Bullied in last 30 days (0 to 100)'), 0, 100, int(ans[key]), key=k)
    elif key == "TrustedAdult":
        ans[key] = st.number_input(t('Has trusted adult (0 to 100)'), 0, 100, int(ans[key]), key=k)


def scale_html(key, title=None):
    """HTML explaining what the numbers for one question mean."""
    h = SCALE_HELP.get(key)
    if not h:
        return ""
    out = f'<div class="scale-title">{th(title)}</div>' if title else ""
    out += f'<div class="scale-intro">{th(h["intro"])}</div>'
    if h["rows"]:
        out += '<table class="scale">' + "".join(
            f"<tr><td>{th(a)}</td><td>{th(b)}</td></tr>" for a, b in h["rows"]) + "</table>"
    return out


def scale_help(key):
    """Collapsible 'What do these numbers mean?' box under an input."""
    if key not in SCALE_HELP:
        return
    with st.expander("ℹ️ " + t("What do these numbers mean?")):
        st.markdown(scale_html(key) + f'<div class="scale-note">{th(SCALE_NOTE)}</div>', unsafe_allow_html=True)


def scale_help_all():
    """One box listing every question's scale (used on the analysis page)."""
    with st.expander("ℹ️ " + t("What do these numbers mean?")):
        body = "".join(scale_html(q["key"], q["label"]) for q in QUESTIONS)
        st.markdown(body + f'<div class="scale-note">{th(SCALE_NOTE)}</div>', unsafe_allow_html=True)


# =====================================================================
# ANALYSIS
# =====================================================================
def run_analysis():
    knn, scaler = load_models()

    Gender = 0 if ans["Gender"] == 'Female' else 1
    Age, Sleep = ans["Age"], ans["Sleep"]
    ParentRelationship, SocialSupport = ans["ParentRelationship"], ans["SocialSupport"]
    AceHousehold = ans["AceHousehold"]
    Bullied, TrustedAdult = ans["Bullied"], ans["TrustedAdult"]

    # not asked, so typical values are used
    AcademicPressure = 3
    FoodInsecurity = 0
    Income = 1
    AceNeglect = 1
    AceAbuse = 1
    HousingInsecure = 0
    Suicidal = 0
    Cyberbullied = 0
    Discrimination = 0
    SuicidalMissing = 0

    (Age, Sleep, AcademicPressure, SocialSupport, ParentRelationship, FoodInsecurity,
     Income, AceNeglect, AceAbuse, AceHousehold) = scaler.transform(
        [[Age, Sleep, AcademicPressure, SocialSupport, ParentRelationship, FoodInsecurity,
          Income, AceNeglect, AceAbuse, AceHousehold]])[0]

    country = [1 if c == ans["Country"] else 0 for c in COUNTRIES]

    feature = [Gender, AcademicPressure, HousingInsecure, Income, AceNeglect, Suicidal, AceAbuse,
               SocialSupport, Cyberbullied, FoodInsecurity, TrustedAdult, ParentRelationship,
               Age, Sleep, Discrimination, Bullied, AceHousehold, SuicidalMissing] + country

    proba = knn.predict_proba([feature])[0][1]
    percent = round(proba * 100)
    risk = 'Low' if proba < 0.40 else 'Moderate' if proba < 0.70 else 'High'

    base = [ans["Gender"], ans["Age"], ans["Country"], ans["Sleep"], ans["ParentRelationship"],
            ans["SocialSupport"], ans["AceHousehold"], ans["Bullied"], ans["TrustedAdult"], percent, risk]
    # Optional: ALTER TABLE prediction_history ADD COLUMN phq_score INT NULL, ADD COLUMN phq_item9 INT NULL;
    new_sql = '''insert into prediction_history(gender, age, country, sleep, parent_rel, social_support,
                 ace_household, bullied, trusted_adult, probability, risk, phq_score, phq_item9)
                 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    old_sql = '''insert into prediction_history(gender, age, country, sleep, parent_rel, social_support,
                 ace_household, bullied, trusted_adult, probability, risk)
                 values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    saved, error = False, ""
    try:
        conn = get_db()
        conn.ping(reconnect=True)
        cursor = conn.cursor()
        done = st.session_state.phq_done
        try:
            cursor.execute(new_sql, base + [phq_total() if done else None, ans["phq"][8] if done else None])
        except Exception:
            cursor.execute(old_sql, base)
        conn.commit()
        saved = True
    except Exception as e:
        error = str(e)

    st.session_state.result = {"percent": percent, "risk": risk, "saved": saved, "error": error}


RESULT_TEXT = {
    "Low": ("safe", "✅", "Low risk", "No strong signs of depression were found."),
    "Moderate": ("moderate", "⚠️", "Moderate risk", "The child may be moving toward depression. Early warning signs were found."),
    "High": ("danger", "🚨", "High risk", "Strong signs of depression were found. Please see a professional soon."),
}


def result_html(res, risk=None):
    css, icon, name, msg = RESULT_TEXT[risk or res["risk"]]
    return (f'<div class="result {css}"><div>{icon} {th(name)}</div>'
            f'<div class="score">{res["percent"]}%</div><div class="msg">{th(msg)}</div></div>')


def clinical_html():
    risk = clinical_risk()
    if risk is None:
        return f'<p class="small">{th("The clinical questionnaire has not been completed. The result above uses the model only.")}</p>'
    return (f'<div class="result {CSS_OF[risk]}"><div>🩺 {th("Clinical questionnaire (PHQ-A style)")}</div>'
            f'<div class="score">{phq_total()}/27</div><div class="msg">{th(phq_band())}</div></div>')


def urgent_html():
    return (f'<div class="urgent"><b>{th("If the child talks about wanting to die or hurting themselves,")}</b> '
            f'{th("stay with them and call a helpline or the emergency number now. Do not wait for an appointment.")}'
            f'<br>{help_text()}</div>')


def focus_points():
    pts = []
    if ans["Sleep"] < 7 or ans["Sleep"] > 10:
        pts.append("Sleep is outside the healthy range. Set a fixed bedtime, cut screens an hour before sleep and talk to a doctor if it continues.")
    if ans["ParentRelationship"] <= 4:
        pts.append("The bond with parents is weak. Spend short, regular one-to-one time with the child and listen more than you advise.")
    if ans["SocialSupport"] <= 4:
        pts.append("Social support is low. Help the child reconnect with a friend, relative or group activity.")
    if ans["AceHousehold"] >= 2:
        pts.append("Several difficult experiences at home were reported. A trained counsellor can help the child work through them.")
    if ans["Bullied"] > 0:
        pts.append("Bullying was reported. Document it, tell the school and make sure the child knows it is not their fault.")
    if ans["TrustedAdult"] == 0:
        pts.append("The child has no trusted adult. Help them find one: a relative, teacher or counsellor.")
    if clinical_risk() in ("Moderate", "High"):
        pts.append("The clinical questionnaire score is in the moderate range or higher. Share these answers with a doctor or counsellor.")
    return pts


# =====================================================================
# SHARED PIECES
# =====================================================================
def topbar(pct=None):
    c1, c2, c3 = st.columns([3.2, 1, 1], vertical_alignment="center", gap="medium")
    with c1:
        st.markdown(f'<div class="brand"><span class="logo"></span>{th("Child Depression Risk Analysis")}</div>',
                    unsafe_allow_html=True)
    with c2:
        st.selectbox("🌐 Language", list(LANGS), key="lang_code", format_func=lambda c: "🌐 " + LANGS[c],
                     label_visibility="collapsed")
    with c3:
        info = helpinfo()
        num = info["lines"][0][2] if info["lines"] else info["emergency"]
        st.markdown(f'<div class="pill">{th("Helpline")}: {html.escape(num)}</div>', unsafe_allow_html=True)
    if pct is not None:
        st.markdown(f'<div class="progress"><div style="width:{pct}%"></div></div>', unsafe_allow_html=True)


def footer():
    st.markdown(f"""
<div class="footer">
<b>{th("If a child is in danger or talking about self-harm, act right away.")}</b><br>
{help_text()}<br>
{th("Helplines in other countries:")} {FIND_HELP}. {th("Numbers can change. Please confirm them locally.")}<br>
{th("This tool is a screening aid for awareness only. It does not diagnose and does not replace a doctor or counsellor.")}
</div>""", unsafe_allow_html=True)


def card(key, num, title, text):
    with st.container(key=f"card_{key}"):
        st.markdown(f'<div class="qcard"><div class="num">{num}</div><h3>{th(title)}</h3><p>{th(text)}</p></div>',
                    unsafe_allow_html=True)
        st.button(t("Open"), key=f"open_{key}", on_click=go, args=(key,), use_container_width=True)


# =====================================================================
# PAGES
# =====================================================================
def page_home():
    topbar()
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown(f"""
<div class="hero">
<h1>{th("Spot the signs of child depression early")}</h1>
<p>{th("Answer nine short questions and a short clinical questionnaire. For each question, learn why it matters, how the model uses it and what the world's data says. Then get a risk score and a plan for what to do next.")}</p>
</div>""", unsafe_allow_html=True)
        st.button(t("Start the screening"), type="primary", on_click=go, args=(ORDER[0],))
    with right:
        hero_img = img_tag("hero", "hero-img")
        if hero_img:
            st.markdown(hero_img, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="mock"><b>{th("How has sleep been?")}</b>'
                        f'{th("Children rarely say \"I feel low\". They say \"I am tired\".")}</div>',
                        unsafe_allow_html=True)

    st.markdown(f'<div class="section-title">{th("Choose a question to begin")}</div>', unsafe_allow_html=True)
    for r in range(0, len(QUESTIONS), 3):
        cols = st.columns(3, gap="large")
        for c, q in zip(cols, QUESTIONS[r:r + 3]):
            with c:
                card(q["key"], ORDER.index(q["key"]) + 1, q["label"], q["short"])
    cols = st.columns(3, gap="large")
    extra = [("Clinical", "Clinical questionnaire", "Nine standard questions used by doctors worldwide."),
             ("Analysis", "Analysis and result", "Review the answers and get the risk score."),
             ("Care", "Care guide", "What to do next, based on the result.")]
    for c, (k, title, text) in zip(cols, extra):
        with c:
            card(k, ORDER.index(k) + 1, title, text)
    info = helpinfo()
    big = info["lines"][0][2] if info["lines"] else info["emergency"]
    st.markdown(f'<div class="qcard static"><div class="num">{th("Need help now?")}</div>'
                f'<h3>{th("Call")} {html.escape(big)}</h3><p>{help_text()}<br>'
                f'{th("Helplines in other countries:")} {FIND_HELP}</p></div>', unsafe_allow_html=True)
    footer()


def page_question(key):
    q = QMAP[key]
    idx = ORDER.index(key)
    topbar((idx + 1) / len(ORDER) * 100)

    main, side = st.columns([2.1, 1], gap="large")
    with main:
        st.markdown(f'<div class="crumb">{th("Question {i} of {n}", i=idx + 1, n=len(QUESTIONS))}</div>'
                    f'<div class="page-title">{th(q["label"])}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="essay"><h3>{th("Why it is needed")}</h3><p>{th(q["why"])}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="essay"><h3>{th("How it works")}</h3><p>{th(q["how"])}</p></div>', unsafe_allow_html=True)
        cells = "".join(f'<div class="stat"><div class="big">{th(b)}</div><div class="cap">{th(c)}</div></div>'
                        for b, c in q["stats"])
        st.markdown(f'<div class="essay" style="max-width:none"><h3>{th("The world today")}</h3>'
                    f'<div class="stats">{cells}</div><div class="source">{th(STAT_NOTE)}</div></div>',
                    unsafe_allow_html=True)
    with side:
        with st.container(key="inputpanel"):
            st.markdown(f'<div class="panel-title">{th("Your answer")}</div>', unsafe_allow_html=True)
            render_input(key)
            scale_help(key)
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                if idx == 0:
                    st.button(t("All questions"), key="b_home", on_click=go, args=("home",), use_container_width=True)
                else:
                    st.button(t("Back"), key="b_back", on_click=go_step, args=(-1,), use_container_width=True)
            with c2:
                nxt = "Next" if idx < len(QUESTIONS) - 1 else "Go to clinical questionnaire"
                st.button(t(nxt), key="b_next", type="primary", on_click=go_step, args=(1,), use_container_width=True)
            st.markdown(f'<div class="quote">{th(q["quote"])}</div>', unsafe_allow_html=True)
        st.markdown(img_tag("right"), unsafe_allow_html=True)
    footer()


def page_clinical():
    idx = ORDER.index("Clinical")
    topbar((idx + 1) / len(ORDER) * 100)
    st.markdown(f'<div class="crumb">{th("Step {i} of {n}", i=idx + 1, n=len(ORDER))}</div>'
                f'<div class="page-title">{th("Clinical questionnaire")}</div>', unsafe_allow_html=True)
    main, side = st.columns([1.6, 1], gap="large")
    with main:
        st.markdown(f'<div class="essay"><h3>{th("Over the last 2 weeks, how often has the child been bothered by the following?")}</h3>'
                    f'<p>{th(PHQ_INTRO)}</p></div>', unsafe_allow_html=True)
        with st.container(key="inputpanel"):
            for i, item in enumerate(PHQ_ITEMS):
                st.markdown(f'<div class="phq-q">{i + 1}. {th(item)}</div>', unsafe_allow_html=True)
                ans["phq"][i] = st.radio(item, range(4), index=ans["phq"][i], horizontal=True, key=f"phq_{i}",
                                         format_func=lambda v: t(PHQ_OPTS[v]), label_visibility="collapsed")
            st.markdown(f'<div class="phq-q">{th(PHQ_DIFF_Q)}</div>', unsafe_allow_html=True)
            ans["phq_diff"] = st.radio(PHQ_DIFF_Q, range(4), index=ans["phq_diff"], horizontal=True, key="phq_diff",
                                       format_func=lambda v: t(PHQ_DIFF[v]), label_visibility="collapsed")
    with side:
        with st.container(key="resultpanel"):
            st.markdown(f'<div class="panel-title">{th("Score so far")}</div>', unsafe_allow_html=True)
            tot = phq_total()
            css = CSS_OF["High" if tot >= 15 else "Moderate" if tot >= 10 else "Low"]
            st.markdown(f'<div class="result {css}"><div class="score">{tot}/27</div>'
                        f'<div class="msg">{th(phq_band())}</div></div>', unsafe_allow_html=True)
            ranges = ["0–4", "5–9", "10–14", "15–19", "20–27"]
            st.markdown("<br>".join(f'<span class="small">{r}: {th(lbl)}</span>'
                                    for r, (_, lbl) in zip(ranges, PHQ_BANDS)), unsafe_allow_html=True)
            if ans["phq"][8] > 0:
                st.markdown(urgent_html(), unsafe_allow_html=True)
            st.markdown(f'<p class="small">{th("A score of 10 or more is the usual point at which a doctor or counsellor should look more closely. This questionnaire screens, it does not diagnose.")}</p>',
                        unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.button(t("Back"), key="p_back", on_click=go_step, args=(-1,), use_container_width=True)
            with c2:
                st.button(t("Save and continue"), key="p_next", type="primary", on_click=finish_clinical,
                          use_container_width=True)
    footer()


def page_analysis():
    idx = ORDER.index("Analysis")
    topbar((idx + 1) / len(ORDER) * 100)
    st.markdown(f'<div class="crumb">{th("Step {i} of {n}", i=idx + 1, n=len(ORDER))}</div>'
                f'<div class="page-title">{th("Analysis and result")}</div>', unsafe_allow_html=True)
    main, side = st.columns([1.2, 1], gap="large")
    with main:
        st.markdown(f'<div class="essay"><h3>{th("Review the answers")}</h3>'
                    f'<p>{th("Check the answers below. To change one, open it from the question list, then come back and press Analyse.")}</p></div>',
                    unsafe_allow_html=True)
        rows = "".join(f"<tr><td>{th(q['label'])}</td><td>{th(ans[q['key']]) if isinstance(ans[q['key']], str) else ans[q['key']]}</td></tr>"
                       for q in QUESTIONS)
        if st.session_state.phq_done:
            rows += f"<tr><td>{th('Clinical questionnaire (PHQ-A style)')}</td><td>{phq_total()}/27</td></tr>"
        st.markdown(f'<table class="review">{rows}</table>', unsafe_allow_html=True)
        scale_help_all()
        st.write("")
        c1, c2, _ = st.columns([1, 1, 1])
        with c1:
            st.button(t("Edit answers"), on_click=go, args=("home",), use_container_width=True)
        with c2:
            if st.button(t("Analyse"), type="primary", use_container_width=True):
                try:
                    run_analysis()
                except Exception as e:
                    st.error(f"{t('Could not run the model:')} {e}")
    with side:
        with st.container(key="resultpanel"):
            st.markdown(f'<div class="panel-title">{th("Result")}</div>', unsafe_allow_html=True)
            res = st.session_state.result
            if res is None:
                st.markdown(f'<p style="font-size:1.25rem;line-height:1.6">{th("Press Analyse to see the risk score for this child.")}</p>',
                            unsafe_allow_html=True)
            else:
                st.markdown(result_html(res), unsafe_allow_html=True)
                st.markdown(clinical_html(), unsafe_allow_html=True)
                if st.session_state.phq_done and ans["phq"][8] > 0:
                    st.markdown(urgent_html(), unsafe_allow_html=True)
                if res["saved"]:
                    st.caption(t("Saved to the database."))
                else:
                    st.error(f"{t('Could not save to database:')} {res['error']}")
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.button(t("Back"), key="a_back", on_click=go_step, args=(-1,), use_container_width=True)
            with c2:
                st.button(t("How to help"), key="a_next", type="primary", on_click=go_step, args=(1,),
                          disabled=res is None, use_container_width=True)
    footer()


def page_care():
    topbar(100)
    st.markdown(f'<div class="crumb">{th("Step {i} of {n}", i=len(ORDER), n=len(ORDER))}</div>'
                f'<div class="page-title">{th("Care guide")}</div>', unsafe_allow_html=True)
    res = st.session_state.result
    if res is None:
        st.warning(t("Run the analysis first so the guide can match the result."))
        st.button(t("Go to analysis"), type="primary", on_click=go, args=("Analysis",))
        footer()
        return

    risk = final_risk(res)          # the higher of the model result and the clinical questionnaire
    g = CARE[risk]
    top, score = st.columns([2, 1], gap="large")
    with top:
        st.markdown(f'<div class="essay"><h3>{th(g["title"])}</h3><p>{th(g["intro"])}</p></div>', unsafe_allow_html=True)
    with score:
        st.markdown(result_html(res, risk), unsafe_allow_html=True)

    if risk == "High" or (st.session_state.phq_done and ans["phq"][8] > 0):
        st.markdown(urgent_html(), unsafe_allow_html=True)

    def block(title, items, extra=""):
        li = "".join(f"<li>{th(i)}</li>" for i in items)
        return f'<div class="care {extra}"><h3>{th(title)}</h3><ul>{li}</ul></div>'

    st.markdown('<div class="care-grid">' + block("At home", g["home"]) + block("At school", g["school"])
                + block("Professional help", g["pro"]) + '</div>', unsafe_allow_html=True)

    pts = focus_points() or ["No single answer stood out. Keep the daily routines and open conversations going."]
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(block("Focus areas from these answers", pts), unsafe_allow_html=True)
    with right:
        st.markdown(block("What to avoid", g["avoid"], "avoid"), unsafe_allow_html=True)

    st.markdown(f'<div class="helplines"><b>{th("Who to call")}</b><br>{help_text()}<br>'
                f'{th("Helplines in other countries:")} {FIND_HELP}</div>', unsafe_allow_html=True)
    st.write("")
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        st.button(t("Back"), key="c_back", on_click=go_step, args=(-1,), use_container_width=True)
    with c2:
        st.button(t("Start over"), key="c_home", type="primary", on_click=go, args=("home",), use_container_width=True)
    footer()


# =====================================================================
# ROUTER
# =====================================================================
page = st.session_state.page
if page == "home":
    page_home()
elif page == "Clinical":
    page_clinical()
elif page == "Analysis":
    page_analysis()
elif page == "Care":
    page_care()
else:
    page_question(page)

flush_pending()   # translate anything new, save it to disk, and refresh once