import streamlit as st
from google.cloud import bigquery
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="AI Sales Insights Assistant", layout="wide")
st.title("🔍 AI Sales Insights Assistant")
st.markdown("**Powered by Google Cloud — BigQuery + Visualizations**")

# Initialize BigQuery
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

            # Q1 Specific
            if "q1" in prompt_lower:
                df = run_query("""
                    SELECT SUM(deal_value) as total_revenue 
                    FROM `sales_insights.sales_data` 
                    WHERE quarter = 'Q1' AND status = 'Closed-Won'
                """)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Q1 Closed-Won Revenue**: ${total:,.0f}"

            # Q2 Specific
            elif "q2" in prompt_lower:
                df = run_query("""
                    SELECT SUM(deal_value) as total_revenue 
                    FROM `sales_insights.sales_data` 
                    WHERE quarter = 'Q2' AND status = 'Closed-Won'
                """)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Q2 Closed-Won Revenue**: ${total:,.0f}"

            # General Revenue
            elif any(word in prompt_lower for word in ["revenue", "total", "sum"]):
                df = run_query("""
                    SELECT SUM(deal_value) as total_revenue 
                    FROM `sales_insights.sales_data` 
                    WHERE status = 'Closed-Won'
                """)
                total = df['total_revenue'].iloc[0] if not df.empty else 0
                response = f"**Total Closed-Won Revenue**: ${total:,.0f}"

            # Lost Deals
            elif any(word in prompt_lower for word in ["lost", "loss", "close lost"]):
                df = run_query("""
                    SELECT loss_reason, COUNT(*) as count 
                    FROM `sales_insights.sales_data` 
                    WHERE status = 'Closed-Lost' AND loss_reason IS NOT NULL 
                    GROUP BY loss_reason
                    ORDER BY count DESC
                """)
                if not df.empty:
                    response = "**Top Loss Reasons:**\n" + df.to_string(index=False)
                else:
                    response = "No Closed-Lost deals found."

            # Default response
            else:
                response = "Here are key sales visualizations:"

            st.markdown(response)

            # === CHARTS ===
            col1, col2 = st.columns(2)

            with col1:
                revenue_by_q = run_query("""
                    SELECT quarter, SUM(deal_value) as revenue 
                    FROM `sales_insights.sales_data` 
                    WHERE status = 'Closed-Won' 
                    GROUP BY quarter
                """)
                if not revenue_by_q.empty:
                    fig1 = px.bar(revenue_by_q, x='quarter', y='revenue', 
                                  title="Revenue by Quarter", text='revenue')
                    fig1.update_traces(texttemplate='$%{text:,.0f}')
                    st.plotly_chart(fig1, use_container_width=True)

            with col2:
                status_count = run_query("""
                    SELECT status, COUNT(*) as count 
                    FROM `sales_insights.sales_data` 
                    GROUP BY status
                """)
                if not status_count.empty:
                    fig2 = px.pie(status_count, names='status', values='count', title="Deals by Status")
                    st.plotly_chart(fig2, use_container_width=True)

            st.session_state.messages.append({"role": "assistant", "content": response})
