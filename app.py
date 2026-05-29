import streamlit as st
from google.cloud import bigquery, vision
import google.generativeai as genai
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant")
st.markdown("**Powered by Google Cloud — BigQuery + Vision API + Gemini**")

# Initialize clients
bq_client = bigquery.Client()
vision_client = vision.ImageAnnotatorClient()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # Add this in Cloud Run environment variables later
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def run_query(query):
    try:
        df = bq_client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        return pd.DataFrame()

# ========================
# DOCUMENT INTELLIGENCE
# ========================
st.sidebar.header("📄 Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload receipt, invoice, or contract", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    with st.spinner("Processing document with Cloud Vision + Gemini..."):
        content = uploaded_file.read()
        image = vision.Image(content=content)
        
        # Use Cloud Vision for OCR
        response = vision_client.document_text_detection(image=image)
        extracted_text = response.full_text_annotation.text
        
        if extracted_text:
            st.sidebar.success("✅ Document Processed!")
            
            # Use Gemini to analyze and summarize
            gemini_prompt = f"""
            Extract key information from this document and summarize it professionally.
            Document text: {extracted_text}
            """
            gemini_response = gemini_model.generate_content(gemini_prompt)
            
            st.sidebar.subheader("📋 Extracted & Analyzed")
            st.sidebar.text_area("Extracted Text", extracted_text, height=150)
            st.sidebar.markdown("**Gemini Analysis:**")
            st.sidebar.write(gemini_response.text)
        else:
            st.sidebar.error("Could not extract text from document.")

# ========================
# MAIN CHAT INTERFACE
# ========================
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask anything about sales performance..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            response = ""
            prompt_lower = prompt.lower()

            if "q1" in prompt_lower:
                df = run_query("SELECT SUM(deal_value) as total FROM `sales_insights.sales_data` WHERE quarter = 'Q1' AND status = 'Closed-Won'")
                total = df['total'].iloc[0] if not df.empty else 0
                response = f"**Q1 Closed-Won Revenue**: ${total:,.0f}"

            elif "q2" in prompt_lower:
                df = run_query("SELECT SUM(deal_value) as total FROM `sales_insights.sales_data` WHERE quarter = 'Q2' AND status = 'Closed-Won'")
                total = df['total'].iloc[0] if not df.empty else 0
                response = f"**Q2 Closed-Won Revenue**: ${total:,.0f}"

            elif any(word in prompt_lower for word in ["revenue", "total"]):
                df = run_query("SELECT SUM(deal_value) as total FROM `sales_insights.sales_data` WHERE status = 'Closed-Won'")
                total = df['total'].iloc[0] if not df.empty else 0
                response = f"**Total Closed-Won Revenue**: ${total:,.0f}"

            elif any(word in prompt_lower for word in ["lost", "loss"]):
                df = run_query("SELECT loss_reason, COUNT(*) as count FROM `sales_insights.sales_data` WHERE status = 'Closed-Lost' GROUP BY loss_reason ORDER BY count DESC")
                if not df.empty:
                    response = "**Top Loss Reasons:**\n" + df.to_string(index=False)
                else:
                    response = "No Closed-Lost deals found."

            else:
                response = "Here are key sales visualizations:"

            st.markdown(response)

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                revenue_by_q = run_query("SELECT quarter, SUM(deal_value) as revenue FROM `sales_insights.sales_data` WHERE status = 'Closed-Won' GROUP BY quarter")
                if not revenue_by_q.empty:
                    fig = px.bar(revenue_by_q, x='quarter', y='revenue', title="Revenue by Quarter", text='revenue')
                    fig.update_traces(texttemplate='$%{text:,.0f}')
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                status_count = run_query("SELECT status, COUNT(*) as count FROM `sales_insights.sales_data` GROUP BY status")
                if not status_count.empty:
                    fig2 = px.pie(status_count, names='status', values='count', title="Deals by Status")
                    st.plotly_chart(fig2, use_container_width=True)

            st.session_state.messages.append({"role": "assistant", "content": response})
