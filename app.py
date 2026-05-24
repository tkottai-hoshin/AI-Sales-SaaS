import streamlit as st
from google.cloud import bigquery
import google.generativeai as genai
import os

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant")
st.markdown("**Powered by Google Cloud BigQuery + Gemini**")

# Initialize clients
client = bigquery.Client()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))  # We'll handle this later
model = genai.GenerativeModel('gemini-1.5-flash')

# Query function
def run_query(query):
    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        return f"Error: {str(e)}"

# Chat interface
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
        with st.spinner("Analyzing data..."):
            # Simple intelligent routing
            if any(word in prompt.lower() for word in ["revenue", "total", "sum"]):
                query = """
                SELECT SUM(deal_value) as total_revenue 
                FROM `sales_insights.sales_data` 
                WHERE status = 'Closed-Won'
                """
                df = run_query(query)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Total Closed-Won Revenue**: ${total:,.0f}"
            
            elif "lost" in prompt.lower() or "loss" in prompt.lower():
                query = """
                SELECT loss_reason, COUNT(*) as count 
                FROM `sales_insights.sales_data` 
                WHERE status = 'Closed-Lost' AND loss_reason IS NOT NULL 
                GROUP BY loss_reason
                ORDER BY count DESC
                """
                df = run_query(query)
                response = "**Top Loss Reasons:**\n" + df.to_string(index=False)
            
            else:
                # Use Gemini for smarter responses
                query = "SELECT * FROM `sales_insights.sales_data` LIMIT 10"
                df = run_query(query)
                context = df.to_string()
                gemini_response = model.generate_content(f"Context:\n{context}\n\nQuestion: {prompt}\nAnswer professionally.")
                response = gemini_response.text

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
