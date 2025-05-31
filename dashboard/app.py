import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from fpdf import FPDF
import urllib.parse

# Load all user data once
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("user_health_data.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame()  # empty if no data yet

def generate_wellness_plan(risks):
    plan = []
    # Simple logic to create plan based on high risks
    if risks.get('Diabetes_risk', 0) > 50:
        plan.append("Walk 30 mins daily")
        plan.append("Limit sugar intake")
    if risks.get('Heart_Disease_risk', 0) > 50:
        plan.append("Avoid saturated fats")
        plan.append("Monitor blood pressure")
    if risks.get('Stress_Burnout_risk', 0) > 50:
        plan.append("Practice meditation")
        plan.append("Take regular breaks")
    if not plan:
        plan = ["Maintain balanced diet", "Exercise regularly", "Stay hydrated"]
    return plan

def create_pdf_report(name, risks, plan):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"HealthMate AI Report for {name}", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, "Disease Risk Summary:", ln=True)
    for disease, risk in risks.items():
        pdf.cell(0, 10, f"{disease.replace('_risk','')}: {risk}%", ln=True)

    pdf.ln(10)
    pdf.cell(0, 10, "7-Day Wellness Plan:", ln=True)
    for task in plan:
        pdf.cell(0, 10, f"- {task}", ln=True)

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

def main():
    st.set_page_config(page_title="HealthMate AI Dashboard", layout="centered")

    st.title("🤖 HealthMate AI Wellness Dashboard")

    # Get user_id from query params
    query_params = st.query_params
    user_id = query_params.get("user_id", [None])[0]

    if not user_id:
        st.warning("No user_id provided. Please open this dashboard from the bot's link.")
        st.stop()

    # Load data
    df = load_data()

    user_data = df[df['user_id'] == int(user_id)]
    if user_data.empty:
        st.error("No data found for your user ID. Please complete your health checkup first.")
        st.stop()

    user_info = user_data.iloc[0]
    name = user_info.get("Name", "Friend")

    st.header(f"Hello, {name}!")
    st.write("Here is your personalized health risk summary and wellness plan.")

    # Extract risk columns ending with '_risk'
    risk_cols = [col for col in df.columns if col.endswith('_risk')]
    risks = {col: round(user_info[col], 2) for col in risk_cols if col in user_info}

    # Bar chart of risks
    risk_df = pd.DataFrame({
        "Disease": [col.replace('_risk','').replace('_', ' ') for col in risks.keys()],
        "Risk (%)": list(risks.values())
    })

    fig = px.bar(risk_df, x="Disease", y="Risk (%)", color="Risk (%)",
                 color_continuous_scale='RdYlGn_r',
                 labels={"Risk (%)": "Risk Percentage"},
                 title="Your Disease Risk Probabilities")

    st.plotly_chart(fig, use_container_width=True)

    # Generate wellness plan based on risks
    wellness_plan = generate_wellness_plan(risks)

    st.subheader("Your 7-Day Wellness Plan")
    for day in range(1, 8):
        st.markdown(f"**Day {day}:**")
        for task in wellness_plan:
            st.markdown(f"- {task}")

    # PDF report download
    if st.button("Download Your Personalized PDF Report"):
        pdf_bytes = create_pdf_report(name, risks, wellness_plan)
        st.download_button("Click to download PDF", pdf_bytes, file_name=f"HealthMateAI_Report_{name}.pdf", mime="application/pdf")

    st.info("💡 Remember: This dashboard updates automatically after each health checkup via the Telegram bot!")

if __name__ == "__main__":
    main()

