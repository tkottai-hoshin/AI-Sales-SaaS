import streamlit as st
from google.cloud import bigquery, vision
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant")
st.markdown("**Powered by Google Cloud**")

# Initialize clients
bq_client = bigquery.Client()
vision_client = vision.ImageAnnotatorClient()

def run_query(query):
    try:
        df = bq_client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        return pd.DataFrame()

# Document Upload
st.sidebar.header("📄 Document Intelligence")
uploaded_file = st.sidebar.file_uploader("Upload receipt or invoice", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    with st.spinner("Processing..."):
        content = uploaded_file.read()
        image = vision.Image(content=content)
        response = vision_client.document_text_detection(image=image)
        text = response.full_text_annotation.text if response.full_text_annotation else "No text found."
        st.sidebar.success("Processed!")
        st.sidebar.text_area("Extracted Text", text, height=200)

# Main Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about sales (e.g. Q1 revenue, lost deals...)"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = "This is a test response. Chat is working!"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
