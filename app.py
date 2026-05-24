import streamlit as st
from google.cloud import bigquery
import pandas as pd
import os

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant")
st.markdown("**Powered by Google Cloud — BigQuery + Gemini**")

# Initialize BigQuery client
client = bigquery.Client()

# Query helper function
def run_query(query):
    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error

# Chat history
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

            if any(word in prompt.lower() for word in ["revenue", "total", "sum"]):
                query = """
                SELECT SUM(deal_value) as total_revenue 
                FROM `sales_insights.sales_data` 
                WHERE status = 'Closed-Won'
                """
                df = run_query(query)
                if not df.empty and 'total_revenue' in df.columns:
                    total = df['total_revenue'].iloc[0]
                    response = f"**Total Closed-Won Revenue**: ${total:,.0f}"
                else:
                    response = "No revenue data found."

            elif any(word in prompt.lower() for word in ["lost", "loss", "reason"]):
                query = """
                SELECT loss_reason, COUNT(*) as count 
                FROM `sales_insights.sales_data` 
                WHERE status = 'Closed-Lost' AND loss_reason IS NOT NULL 
                GROUP BY loss_reason
                ORDER BY count DESC
                """
                df = run_query(query)
                if not df.empty:
                    response = "**Top Loss Reasons:**\n" + df.to_string(index=False)
                else:
                    response = "No loss data found."

            else:
                # Default: Show sample data
                query = "SELECT * FROM `sales_insights.sales_data` LIMIT 10"
                df = run_query(query)
                if not df.empty:
                    response = "Here is a sample of the sales data:\n" + df.to_string(index=False)
                else:
                    response = "No data available at the moment."

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
