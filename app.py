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
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def run_query(query):
    try:
        df = bq_client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        return pd.DataFrame()

# ========================
# DOCUMENT INTELLIGENCE (Cloud Vision)
# ========================
st.sidebar.header("📄 Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload receipt, invoice, or contract", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    with st.spinner("Processing document with Cloud Vision + Gemini..."):
        content = uploaded_file.read()
        image = vision.Image(content=content)
        
        response = vision_client.document_text_detection(image=image)
        extracted_text = response.full_text_annotation.text
        
        if extracted_text:
            st.sidebar.success("✅ Document Processed!")
            
            # Use Gemini to summarize
            gemini_prompt = f"Extract and summarize the key information from this document professionally:\n\n{extracted_text}"
            gemini_response = gemini_model.generate_content(gemini_prompt)
            
            st.sidebar.subheader("📋 Extracted Text")
            st.sidebar.text_area("Raw Text", extracted_text, height=150)
            st.sidebar.markdown("**Gemini Summary:**")
            st.sidebar.write(gemini_response.text)
        else:
            st.sidebar.error("Could not extract text from the document.")

# ========================
# MAIN CHAT INTERFACE
# ========================
if "messages" not in st.session
