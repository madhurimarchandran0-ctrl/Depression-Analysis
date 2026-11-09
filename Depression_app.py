import base64
import pickle

import pymysql
import streamlit as st

st.set_page_config(page_title="Child Depression Risk Analysis", layout="wide",
                   initial_sidebar_state="collapsed")

# =====================================================================
# STYLES  (dark Typeform look, big type, fills a desktop screen)
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600&family=Inter:wght@400;500;600&display=swap');

html { font-size: 20px; }
html, body, .stApp { font-family: 'Inter', sans-serif; color: #f4f1f7; }
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
.topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.4rem; }
.brand { display: flex; align-items: center; gap: 0.7rem; font-size: 1.7rem; font-weight: 500; color: #fff; }
.brand .logo { width: 2.1rem; height: 1.4rem; background: #fff; border-radius: 0.45rem; display: inline-block; }
.pill { background: #fff; color: #1d1b1e; padding: 0.55rem 1.5rem; border-radius: 0.7rem; font-weight: 500; font-size: 1.05rem; }
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
.mock .chip { display: inline-block; border: 2px solid #1c2a1a; border-radius: 0.5rem; padding: 0.25rem 0.9rem; margin: 0.6rem 0.5rem 0 0; font-size: 1rem; }
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

/* ---------- widgets ---------- */
label p, [data-testid="stWidgetLabel"] p { font-size: 1.2rem !important; font-weight: 500; }
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
# DATABASE + MODEL
# =====================================================================
@st.cache_resource
def get_db():
    return pymysql.connect(host='localhost', user='root', password='1234', db='depression_db')


@st.cache_resource
def load_models():
    rf = pickle.load(open('rf_depression_model.sav', 'rb'))
    scaler = pickle.load(open('scaler_depression.sav', 'rb'))
    return rf, scaler


COUNTRIES = ['Argentina', 'Bangladesh', 'Brazil', 'India', 'Indonesia', 'Jordan', 'Kenya', 'Philippines']

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
# CONTENT  (edit the text and statistics here)
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
     "stats": [("1 adult", "is enough to buffer the effects of childhood adversity (Harvard Center on the Developing Child)"),
               ("14416", "Tele-MANAS, India's free 24x7 mental health helpline"),
               ("1098", "Childline, India's free helpline for children")],
     "quote": "Be the person you needed when you were young."},
]
QMAP = {q["key"]: q for q in QUESTIONS}
ORDER = [q["key"] for q in QUESTIONS] + ["Analysis", "Care"]
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
                "Call Tele-MANAS 14416 for free advice on what to do next.",
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
                "Call Tele-MANAS 14416 (free, 24x7) for guidance and referrals.",
                "Treatment may include talking therapy, family support and, when a doctor decides, medicine.",
                "Follow the treatment plan and go to every follow-up."],
        "avoid": ["Leaving the child alone with their thoughts.",
                  "Blaming the child, or blaming yourself. Blame delays help.",
                  "Waiting to see if it passes by itself.",
                  "Giving any medicine that was not prescribed for the child."],
    },
}

# =====================================================================
# SESSION STATE
# =====================================================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "answers" not in st.session_state:
    st.session_state.answers = {
        "Gender": "Female", "Age": 13, "Country": "Argentina", "Sleep": 7.0,
        "ParentRelationship": 3, "SocialSupport": 3, "AceHousehold": 0,
        "Bullied": 0, "TrustedAdult": 1,
    }
if "result" not in st.session_state:
    st.session_state.result = None
ans = st.session_state.answers


def go(page):
    st.session_state.page = page


def go_step(step):
    i = ORDER.index(st.session_state.page) + step
    st.session_state.page = ORDER[max(0, min(len(ORDER) - 1, i))]


# =====================================================================
# INPUT WIDGETS
# =====================================================================
def render_input(key):
    k = f"w_{key}"
    if key == "Gender":
        opts = ['Female', 'Male']
        ans[key] = st.selectbox('Gender', opts, index=opts.index(ans[key]), key=k)
    elif key == "Age":
        ans[key] = st.number_input('Age (10 to 17)', 10, 17, int(ans[key]), key=k)
    elif key == "Country":
        ans[key] = st.selectbox('Country', COUNTRIES, index=COUNTRIES.index(ans[key]), key=k)
    elif key == "Sleep":
        ans[key] = st.number_input('Sleep hours per night', 2.0, 12.0, float(ans[key]), step=0.5, key=k)
    elif key == "ParentRelationship":
        ans[key] = st.number_input('Parent relationship (1 to 10)', 1, 10, int(ans[key]), key=k)
    elif key == "SocialSupport":
        ans[key] = st.number_input('Social support (1 to 10)', 1, 10, int(ans[key]), key=k)
    elif key == "AceHousehold":
        ans[key] = st.number_input('ACE household (0 to 10)', 0, 10, int(ans[key]), key=k)
    elif key == "Bullied":
        ans[key] = st.number_input('Bullied in last 30 days (0 to 100)', 0, 100, int(ans[key]), key=k)
    elif key == "TrustedAdult":
        ans[key] = st.number_input('Has trusted adult (0 to 100)', 0, 100, int(ans[key]), key=k)


def scale_html(key, title=None):
    """HTML explaining what the numbers for one question mean."""
    h = SCALE_HELP.get(key)
    if not h:
        return ""
    html = f'<div class="scale-title">{title}</div>' if title else ""
    html += f'<div class="scale-intro">{h["intro"]}</div>'
    if h["rows"]:
        rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in h["rows"])
        html += f'<table class="scale">{rows}</table>'
    return html


def scale_help(key):
    """Collapsible 'What do these numbers mean?' box under an input."""
    if key not in SCALE_HELP:
        return
    with st.expander("ℹ️ What do these numbers mean?"):
        st.markdown(scale_html(key) + f'<div class="scale-note">{SCALE_NOTE}</div>',
                    unsafe_allow_html=True)


def scale_help_all():
    """One box listing every question's scale (used on the analysis page)."""
    with st.expander("ℹ️ What do these numbers mean?"):
        html = "".join(scale_html(q["key"], q["label"]) for q in QUESTIONS)
        html += f'<div class="scale-note">{SCALE_NOTE}</div>'
        st.markdown(html, unsafe_allow_html=True)


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

    saved, error = False, ""
    try:
        conn = get_db()
        conn.ping(reconnect=True)
        cursor = conn.cursor()
        cursor.execute(
            '''insert into prediction_history(gender, age, country, sleep, parent_rel, social_support,
               ace_household, bullied, trusted_adult, probability, risk)
               values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            [ans["Gender"], ans["Age"], ans["Country"], ans["Sleep"], ans["ParentRelationship"],
             ans["SocialSupport"], ans["AceHousehold"], ans["Bullied"], ans["TrustedAdult"], percent, risk])
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


def result_html(res):
    css, icon, name, msg = RESULT_TEXT[res["risk"]]
    return (f'<div class="result {css}"><div>{icon} {name}</div>'
            f'<div class="score">{res["percent"]}%</div><div class="msg">{msg}</div></div>')


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
    return pts


# =====================================================================
# SHARED PIECES
# =====================================================================
def topbar(pct=None):
    st.markdown("""
<div class="topbar">
  <div class="brand"><span class="logo"></span>Child Depression Risk Analysis</div>
  <div class="pill">Child helpline: 1098</div>
</div>""", unsafe_allow_html=True)
    if pct is not None:
        st.markdown(f'<div class="progress"><div style="width:{pct}%"></div></div>', unsafe_allow_html=True)


def footer():
    st.markdown("""
<div class="footer">
<b>If a child is in danger or talking about self-harm, act right away.</b>
India: Tele-MANAS 14416 (free, 24x7) | Childline 1098 | Emergency 112<br>
This tool is a screening aid for awareness only. It does not diagnose and does not replace a doctor or counsellor.
</div>""", unsafe_allow_html=True)


def card(key, num, title, text):
    with st.container(key=f"card_{key}"):
        st.markdown(f'<div class="qcard"><div class="num">{num}</div><h3>{title}</h3><p>{text}</p></div>',
                    unsafe_allow_html=True)
        st.button("Open", key=f"open_{key}", on_click=go, args=(key,), use_container_width=True)


# =====================================================================
# PAGES
# =====================================================================
def page_home():
    topbar()
    left, right = st.columns([1.35, 1], gap="large")
    with left:
        st.markdown("""
<div class="hero">
<h1>Spot the signs of child depression early</h1>
<p>Answer nine short questions. For each one, learn why it matters, how the model uses it and what the world's data says. Then get a risk score and a plan for what to do next.</p>
</div>""", unsafe_allow_html=True)
        st.button("Start the screening", type="primary", on_click=go, args=(ORDER[0],))
    with right:
        hero_img = img_tag("hero", "hero-img")
        if hero_img:
            st.markdown(hero_img, unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="mock"><b>How has sleep been?</b>
Children rarely say "I feel low". They say "I'm tired".
<br><span class="chip">Type</span><span class="chip">Choose</span><span class="chip">Rate 1 to 10</span></div>""",
                        unsafe_allow_html=True)

    st.markdown('<div class="section-title">Choose a question to begin</div>', unsafe_allow_html=True)
    for r in range(0, len(QUESTIONS), 3):
        cols = st.columns(3, gap="large")
        for c, q in zip(cols, QUESTIONS[r:r + 3]):
            with c:
                card(q["key"], ORDER.index(q["key"]) + 1, q["label"], q["short"])
    cols = st.columns(3, gap="large")
    with cols[0]:
        card("Analysis", 10, "Analysis and result", "Review the answers and get the risk score.")
    with cols[1]:
        card("Care", 11, "Care guide", "What to do next, based on the result.")
    with cols[2]:
        st.markdown('<div class="qcard static"><div class="num">Need help now?</div><h3>Call 14416</h3>'
                    '<p>Tele-MANAS is free and open 24x7. Childline is 1098. Emergency is 112.</p></div>',
                    unsafe_allow_html=True)
    footer()


def page_question(key):
    q = QMAP[key]
    idx = ORDER.index(key)
    topbar((idx + 1) / len(ORDER) * 100)

    main, side = st.columns([2.1, 1], gap="large")
    with main:
        st.markdown(f'<div class="crumb">Question {idx + 1} of {len(QUESTIONS)}</div>'
                    f'<div class="page-title">{q["label"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="essay"><h3>Why it is needed</h3><p>{q["why"]}</p></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="essay"><h3>How it works</h3><p>{q["how"]}</p></div>', unsafe_allow_html=True)
        cells = "".join(f'<div class="stat"><div class="big">{b}</div><div class="cap">{c}</div></div>'
                        for b, c in q["stats"])
        st.markdown(f'<div class="essay" style="max-width:none"><h3>The world today</h3>'
                    f'<div class="stats">{cells}</div><div class="source">{STAT_NOTE}</div></div>',
                    unsafe_allow_html=True)
    with side:
        with st.container(key="inputpanel"):
            st.markdown('<div class="panel-title">Your answer</div>', unsafe_allow_html=True)
            render_input(key)
            scale_help(key)
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                if idx == 0:
                    st.button("All questions", key="b_home", on_click=go, args=("home",), use_container_width=True)
                else:
                    st.button("Back", key="b_back", on_click=go_step, args=(-1,), use_container_width=True)
            with c2:
                nxt = "Next" if idx < len(QUESTIONS) - 1 else "Go to analysis"
                st.button(nxt, key="b_next", type="primary", on_click=go_step, args=(1,), use_container_width=True)
            st.markdown(f'<div class="quote">{q["quote"]}</div>', unsafe_allow_html=True)
        st.markdown(img_tag("right"), unsafe_allow_html=True)
    footer()


def page_analysis():
    topbar((ORDER.index("Analysis") + 1) / len(ORDER) * 100)
    st.markdown('<div class="crumb">Step 10 of 11</div><div class="page-title">Analysis and result</div>',
                unsafe_allow_html=True)
    main, side = st.columns([1.2, 1], gap="large")
    with main:
        st.markdown('<div class="essay"><h3>Review the answers</h3>'
                    '<p>Check the answers below. To change one, open it from the question list, then come back and press Analyse.</p></div>',
                    unsafe_allow_html=True)
        labels = {q["key"]: q["label"] for q in QUESTIONS}
        rows = "".join(f"<tr><td>{labels[k]}</td><td>{ans[k]}</td></tr>" for k in labels)
        st.markdown(f'<table class="review">{rows}</table>', unsafe_allow_html=True)
        scale_help_all()
        st.write("")
        c1, c2, _ = st.columns([1, 1, 1])
        with c1:
            st.button("Edit answers", on_click=go, args=("home",), use_container_width=True)
        with c2:
            if st.button("Analyse", type="primary", use_container_width=True):
                try:
                    run_analysis()
                except Exception as e:
                    st.error(f"Could not run the model: {e}")
    with side:
        with st.container(key="resultpanel"):
            st.markdown('<div class="panel-title">Result</div>', unsafe_allow_html=True)
            res = st.session_state.result
            if res is None:
                st.markdown('<p style="font-size:1.25rem;line-height:1.6">Press <b>Analyse</b> to see the risk score for this child.</p>',
                            unsafe_allow_html=True)
            else:
                st.markdown(result_html(res), unsafe_allow_html=True)
                if res["saved"]:
                    st.caption("Saved to the database.")
                else:
                    st.error(f"Could not save to database: {res['error']}")
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                st.button("Back", key="a_back", on_click=go_step, args=(-1,), use_container_width=True)
            with c2:
                st.button("How to help", key="a_next", type="primary", on_click=go_step, args=(1,),
                          disabled=res is None, use_container_width=True)
    footer()


def page_care():
    topbar(100)
    st.markdown('<div class="crumb">Step 11 of 11</div><div class="page-title">Care guide</div>',
                unsafe_allow_html=True)
    res = st.session_state.result
    if res is None:
        st.warning("Run the analysis first so the guide can match the result.")
        st.button("Go to analysis", type="primary", on_click=go, args=("Analysis",))
        footer()
        return

    g = CARE[res["risk"]]
    top, score = st.columns([2, 1], gap="large")
    with top:
        st.markdown(f'<div class="essay"><h3>{g["title"]}</h3><p>{g["intro"]}</p></div>', unsafe_allow_html=True)
    with score:
        st.markdown(result_html(res), unsafe_allow_html=True)

    if res["risk"] == "High":
        st.markdown('<div class="urgent"><b>If the child talks about wanting to die or hurting themselves,</b> '
                    'stay with them and call <b>Tele-MANAS 14416</b>, <b>Childline 1098</b> or <b>emergency 112</b> right now. '
                    'Do not wait for an appointment.</div>', unsafe_allow_html=True)

    def block(title, items, extra=""):
        li = "".join(f"<li>{i}</li>" for i in items)
        return f'<div class="care {extra}"><h3>{title}</h3><ul>{li}</ul></div>'

    st.markdown('<div class="care-grid">' + block("At home", g["home"]) + block("At school", g["school"])
                + block("Professional help", g["pro"]) + '</div>', unsafe_allow_html=True)

    pts = focus_points()
    left, right = st.columns(2, gap="large")
    with left:
        if pts:
            st.markdown(block("Focus areas from these answers", pts), unsafe_allow_html=True)
        else:
            st.markdown(block("Focus areas from these answers",
                              ["No single answer stood out. Keep the daily routines and open conversations going."]),
                        unsafe_allow_html=True)
    with right:
        st.markdown(block("What to avoid", g["avoid"], "avoid"), unsafe_allow_html=True)

    st.markdown('<div class="helplines"><b>Who to call in India</b><br>'
                'Tele-MANAS 14416 (free, 24x7 mental health support) | Childline 1098 | Emergency 112</div>',
                unsafe_allow_html=True)
    st.write("")
    c1, c2, _ = st.columns([1, 1, 3])
    with c1:
        st.button("Back", key="c_back", on_click=go_step, args=(-1,), use_container_width=True)
    with c2:
        st.button("Start over", key="c_home", type="primary", on_click=go, args=("home",), use_container_width=True)
    footer()


# =====================================================================
# ROUTER
# =====================================================================
page = st.session_state.page
if page == "home":
    page_home()
elif page == "Analysis":
    page_analysis()
elif page == "Care":
    page_care()
else:
    page_question(page)