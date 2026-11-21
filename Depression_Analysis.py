import streamlit as st
import pickle

def main():
    st.title('Child Depression Risk Analysis')
    Gender=st.selectbox('Gender:',['Female','Male'])
    Age=st.number_input('Age:',10,17,13)
    Country=st.selectbox('Country:',['Argentina','Bangladesh','Brazil','India','Indonesia','Jordan','Kenya','Philippines'])
    Sleep=st.number_input('Sleep Hours:',2.0,12.0,7.0)
    ParentRelationship=st.number_input('Parent Relationship (1-5):',1,5,3)
    SocialSupport=st.number_input('Social Support (1-5):',1,5,3)
    AceHousehold=st.number_input('ACE Household (0-5):',0,5,0)
    Bullied=st.number_input('Bullied in last 30 days (0/1):',0,1,0)
    TrustedAdult=st.number_input('Has Trusted Adult (0/1):',0,1,1)

    knn = pickle.load(open('rf_depression_model.sav', 'rb'))
    scaler = pickle.load(open('scaler_depression.sav', 'rb'))

    pred=st.button('Predict')
    if pred:
        # not asked, so typical values are used
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

        Gender=0 if Gender=='Female' else 1

        Age,Sleep,AcademicPressure,SocialSupport,ParentRelationship,FoodInsecurity,Income,AceNeglect,AceAbuse,AceHousehold=scaler.transform([[Age,Sleep,AcademicPressure,SocialSupport,ParentRelationship,FoodInsecurity,Income,AceNeglect,AceAbuse,AceHousehold]])[0]

        countries=['Argentina','Bangladesh','Brazil','India','Indonesia','Jordan','Kenya','Philippines']
        country=[1 if c==Country else 0 for c in countries]

        feature=[Gender,AcademicPressure,HousingInsecure,Income,AceNeglect,Suicidal,AceAbuse,
                 SocialSupport,Cyberbullied,FoodInsecurity,TrustedAdult,ParentRelationship,
                 Age,Sleep,Discrimination,Bullied,AceHousehold,SuicidalMissing]+country

        proba=knn.predict_proba([feature])[0][1]
        st.write('Depression probability:',round(proba*100),'%')
        if proba<0.4:
            st.write('Risk level: Low')
        elif proba<0.7:
            st.write('Risk level: Moderate')
        else:
            st.write('Risk level: High')

main()