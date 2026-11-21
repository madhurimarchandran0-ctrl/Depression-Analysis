import streamlit as st
import pickle
from PIL import Image
import pymysql

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="Child Depression Risk Analysis",
    layout="wide"
)

# -------------------------------------------------
# DATABASE
# -------------------------------------------------

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    db='depression_db'
)

cursor = conn.cursor()

# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Basic Information"

# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

.stApp{
background:
linear-gradient(
135deg,
#0f2027,
#203a43,
#2c5364
);
}

.block-container{
padding-top:20px;
}

.dashboard-btn{
width:100%;
}

.info-box{
background:rgba(255,255,255,0.08);
padding:20px;
border-radius:16px;
border:1px solid rgba(255,255,255,0.15);
backdrop-filter:blur(12px);
color:white;
}

.title{
color:white;
font-size:32px;
font-weight:bold;
}

.triangle {
clip-path: polygon(0 0, 100% 50%, 0 100%);
width:100%;
height:auto;
border-radius:20px;
overflow:hidden;
}

</style>
""", unsafe_allow_html=True)

# -------------------------------------------------
# NAVIGATION ITEMS
# -------------------------------------------------

topics = [

"Basic Information",
"Sleep Pattern",
"Parent Relationship",
"Social Support",
"Home Environment",
"Bullying",
"Trusted Adult",
"Prediction"
]

# -------------------------------------------------
# IMAGES
# -------------------------------------------------

images = {

"Basic Information":"images/basic.jpg",

"Sleep Pattern":"images/sleep.jpg",

"Parent Relationship":"images/parent.jpg",

"Social Support":"images/support.jpg",

"Home Environment":"images/home.jpg",

"Bullying":"images/bullying.jpg",

"Trusted Adult":"images/trusted.jpg",

"Prediction":"images/result.jpg"

}

# -------------------------------------------------
# DEFAULT SESSION DATA
# -------------------------------------------------

defaults = {

"Gender":"Female",
"Age":13,
"Country":"India",
"Sleep":7.0,
"ParentRelationship":3,
"SocialSupport":3,
"AceHousehold":0,
"Bullied":0,
"TrustedAdult":1
}

for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# -------------------------------------------------
# LAYOUT
# -------------------------------------------------

left,mid,right = st.columns([1,1.4,2.4])

# =================================================
# LEFT DASHBOARD
# =================================================

with left:

    st.markdown(
        "<div class='title'>Assessment</div>",
        unsafe_allow_html=True
    )

    for t in topics:

        if st.button(t,use_container_width=True):
            st.session_state.page=t

# =================================================
# MIDDLE IMAGE PANEL
# =================================================

with mid:

    img = Image.open(images[st.session_state.page])

    st.markdown("### Visual")

    st.image(
        img,
        use_container_width=True
    )

# =================================================
# RIGHT CONTENT
# =================================================

with right:

    page = st.session_state.page

    progress = (topics.index(page)+1)/len(topics)

    st.progress(progress)

    # =============================================

    if page=="Basic Information":

        st.title("Basic Information")

        st.info("""
        Personal details help understand
        age-related emotional risk factors.
        """)

        st.session_state.Gender = st.selectbox(
            "Gender",
            ["Female","Male"]
        )

        st.session_state.Age = st.number_input(
            "Age",
            10,
            17,
            st.session_state.Age
        )

        st.session_state.Country = st.selectbox(

            "Country",

            [
            "Argentina",
            "Bangladesh",
            "Brazil",
            "India",
            "Indonesia",
            "Jordan",
            "Kenya",
            "Philippines"
            ]
        )

    # =============================================

    elif page=="Sleep Pattern":

        st.title("Sleep Pattern")

        st.info("""
        Healthy sleep improves emotional
        regulation and mental health.

        Less sleep increases risk for
        stress, anxiety and depression.
        """)

        st.session_state.Sleep = st.slider(
            "Hours of Sleep",
            2.0,
            12.0,
            float(st.session_state.Sleep)
        )

    # =============================================

    elif page=="Parent Relationship":

        st.title("Parent Relationship")

        st.info("""
        Strong parent-child relationships
        act as a protective factor against
        depression and emotional distress.
        """)

        st.session_state.ParentRelationship = st.slider(
            "Relationship Rating",
            1,
            5,
            int(st.session_state.ParentRelationship)
        )

    # =============================================

    elif page=="Social Support":

        st.title("Social Support")

        st.info("""
        Friends, teachers and family support
        help children manage challenges and
        build resilience.
        """)

        st.session_state.SocialSupport = st.slider(
            "Support Rating",
            1,
            5,
            int(st.session_state.SocialSupport)
        )

    # =============================================

    elif page=="Home Environment":

        st.title("Home Environment")

        st.info("""
        Adverse childhood experiences and
        household stress may affect
        emotional development.
        """)

        st.session_state.AceHousehold = st.slider(
            "ACE Household Score",
            0,
            5,
            int(st.session_state.AceHousehold)
        )

    # =============================================

    elif page=="Bullying":

        st.title("Bullying")

        st.info("""
        Bullying can significantly affect
        confidence, social interaction
        and mental health.
        """)

        st.session_state.Bullied = st.radio(

            "Bullied During Last 30 Days",

            [0,1],

            format_func=lambda x:
            "No" if x==0 else "Yes"
        )

    # =============================================

    elif page=="Trusted Adult":

        st.title("Trusted Adult")

        st.info("""
        Having at least one trusted adult
        provides emotional safety and
        support during difficult situations.
        """)

        st.session_state.TrustedAdult = st.radio(

            "Trusted Adult Available?",

            [1,0],

            format_func=lambda x:
            "Yes" if x==1 else "No"
        )

    # =============================================
    # FINAL PREDICTION PAGE
    # =============================================

    elif page=="Prediction":

        st.title("Risk Analysis")

        if st.button("Generate Prediction"):

            knn = pickle.load(
                open(
                'knn_depression_model.sav',
                'rb'
                )
            )

            scaler = pickle.load(
                open(
                'scaler_knn_depression.sav',
                'rb'
                )
            )

            AcademicPressure=3
            FoodInsecurity=0
            Income=1
            AceNeglect=1
            AceAbuse=1
            HousingInsecure=0
            Suicidal=0
            Cyberbullied=0
            Discrimination=0
            SuicidalMissing=0

            Gender = 0 if \
            st.session_state.Gender=="Female" \
            else 1

            values = scaler.transform([[
                st.session_state.Age,
                st.session_state.Sleep,
                AcademicPressure,
                st.session_state.SocialSupport,
                st.session_state.ParentRelationship,
                FoodInsecurity,
                Income,
                AceNeglect,
                AceAbuse,
                st.session_state.AceHousehold
            ]])[0]

            Age,Sleep,AcademicPressure,\
            SocialSupport,ParentRelationship,\
            FoodInsecurity,Income,\
            AceNeglect,AceAbuse,\
            AceHousehold = values

            countries = [

                'Argentina',
                'Bangladesh',
                'Brazil',
                'India',
                'Indonesia',
                'Jordan',
                'Kenya',
                'Philippines'
            ]

            country = [

                1 if c ==
                st.session_state.Country
                else 0

                for c in countries
            ]

            feature = [

                Gender,
                AcademicPressure,
                HousingInsecure,
                Income,
                AceNeglect,
                Suicidal,
                AceAbuse,
                SocialSupport,
                Cyberbullied,
                FoodInsecurity,
                st.session_state.TrustedAdult,
                ParentRelationship,
                Age,
                Sleep,
                Discrimination,
                st.session_state.Bullied,
                AceHousehold,
                SuicidalMissing

            ] + country

            proba = knn.predict_proba(
                [feature]
            )[0][1]

            percent = round(
                proba*100
            )

            st.metric(
                "Depression Risk",
                f"{percent}%"
            )

            if proba < 0.4:

                risk="Low"

                st.success(
                    "✅ Low Risk"
                )

            elif proba < 0.7:

                risk="Moderate"

                st.warning(
                    "⚠ Moderate Risk"
                )

            else:

                risk="High"

                st.error(
                    "🚨 High Risk"
                )

            query = """
            INSERT INTO prediction_history
            (
            gender,
            age,
            country,
            sleep,
            parent_rel,
            social_support,
            ace_household,
            bullied,
            trusted_adult,
            probability,
            risk
            )

            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """

            data = [

                st.session_state.Gender,
                st.session_state.Age,
                st.session_state.Country,
                st.session_state.Sleep,
                st.session_state.ParentRelationship,
                st.session_state.SocialSupport,
                st.session_state.AceHousehold,
                st.session_state.Bullied,
                st.session_state.TrustedAdult,
                percent,
                risk
            ]

            cursor.execute(query,data)

            conn.commit()

            st.success(
                "Prediction Saved Successfully"
            )