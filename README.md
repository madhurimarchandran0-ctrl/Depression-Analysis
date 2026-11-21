# Child Depression Risk Analysis

A machine learning project that estimates the risk of depression in children and adolescents from social, family and lifestyle factors, with an interactive Streamlit app for making predictions.

> **Disclaimer:** This is an educational project. It is **not** a medical or diagnostic tool and must not replace advice from a qualified mental health professional. If you or someone you know is struggling, please reach out to a doctor, counsellor or a trusted adult.

## Features

- Exploratory data analysis, including correlation of each factor with depression
- Random Forest classifier to predict depression risk
- Feature scaling with a saved scaler
- Streamlit web app for entering details and viewing the risk result

## Factors Analysed

- Adverse childhood experiences: household, neglect, abuse
- Bullying and cyberbullying
- Social support, trusted adult, parent relationship
- Sleep hours, academic pressure
- Food and housing insecurity, discrimination
- Age

## Project Structure

| File | Description |
|------|-------------|
| `Child_Depression_Risk_Analysis.ipynb` | Data analysis and model training notebook |
| `Depression_Analysis.py` | Analysis script |
| `Depression_app.py` | Streamlit app |
| `main.py` | App entry point |
| `rf_depression_model.sav` | Trained Random Forest model |
| `scaler_depression.sav` | Saved scaler used before prediction |
| `requirements.txt` | Python dependencies |

## Tech Stack

Python, Pandas, NumPy, Scikit-learn, Matplotlib, Streamlit

## How to Run

1. Clone the repository
   ```bash
   git clone https://github.com/madhurimarchandran0-ctrl/Depression-Analysis.git
   cd Depression-Analysis
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app
   ```bash
   streamlit run Depression_app.py
   ```

## Author

**Madhurima R Chandran**
Data Science Intern | Kerala, India
