import streamlit as st
from google.cloud import bigquery, vision
import pandas as pd

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant - Debug Mode")
st.markdown("**Testing Vision API**")

# Initialize clients
bq_client = bigquery.Client()
vision_client = vision.ImageAnnotatorClient()

st.sidebar.header("📄 Document Intelligence - Test")
uploaded_file = st.sidebar.file_uploader("Upload an image (receipt, invoice, etc.)", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    st.sidebar.info("File uploaded. Processing...")
    try:
        content = uploaded_file.read()
        image = vision.Image(content=content)
        
        response = vision_client.document_text_detection(image=image)
        extracted_text = response.full_text_annotation.text if response.full_text_annotation else "No text detected."
        
        st.sidebar.success("✅ Vision API Call Succeeded!")
        st.sidebar.text_area("Extracted Text", extracted_text, height=300)
        
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

st.info("If you see the error above, please copy and paste it here.")
