import streamlit as st
from google.cloud import bigquery
import pandas as pd

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant")
st.markdown("**Powered by Google Cloud — BigQuery**")

client = bigquery.Client()

def run_query(query):
    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"Query Error: {str(e)}")
        return pd.DataFrame()

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

            prompt_lower = prompt.lower()

            # Revenue related
            if any(word in prompt_lower for word in ["revenue", "total revenue", "sum", "closed-won"]):
                query = """
                SELECT SUM(deal_value) as total_revenue 
                FROM `sales_insights.sales_data` 
                WHERE status = 'Closed-Won'
                """
                df = run_query(query)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Total Closed-Won Revenue**: ${total:,.0f}"

            # Q1 / Q2 specific
            elif "q1" in prompt_lower:
                query = """
                SELECT SUM(deal_value) as total_revenue 
                FROM `sales_insights.sales_data` 
                WHERE quarter = 'Q1' AND status = 'Closed-Won'
                """
                df = run_query(query)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Q1 Closed-Won Revenue**: ${total:,.0f}"

            elif "q2" in prompt_lower:
                query = """
                SELECT SUM(deal_value) as total_revenue 
                FROM `sales_insights.sales_data` 
                WHERE quarter = 'Q2' AND status = 'Closed-Won'
                """
                df = run_query(query)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Q2 Closed-Won Revenue**: ${total:,.0f}"

            # Lost deals
            elif any(word in prompt_lower for word in ["lost", "loss", "close lost"]):
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
                    response = "No Closed-Lost deals found."

            # Default / Summary
            else:
                query = "SELECT * FROM `sales_insights.sales_data` LIMIT 12"
                df = run_query(query)
                if not df.empty:
                    response = "Here is a sample of the sales data:\n\n" + df.to_string(index=False)
                else:
                    response = "No data available."

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
