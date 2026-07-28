import streamlit as st
import pandas as pd

from api import (
    get_total_messages,
    get_unique_customers,
    get_sentiment_distribution,
    get_intent_distribution,
)

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="AI Customer Support Dashboard",
    page_icon="🤖",
    layout="wide"
)

# -----------------------------
# Dashboard Title
# -----------------------------
st.title("🤖 AI Customer Support Dashboard")

# -----------------------------
# Fetch Data
# -----------------------------
messages = get_total_messages()
customers = get_unique_customers()
sentiment = get_sentiment_distribution()
intents = get_intent_distribution()

# -----------------------------
# KPI Cards
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.metric(
        label="📨 Messages",
        value=messages["total_messages"]
    )

with col2:
    st.metric(
        label="👥 Customers",
        value=customers["unique_customers"]
    )

# -----------------------------
# Sentiment & Intent Distribution
# -----------------------------
st.divider()

col1, col2 = st.columns(2)

with col1:

    st.subheader("😊 Sentiment Distribution")

    sentiment_df = pd.DataFrame(
        sentiment.items(),
        columns=["Sentiment", "Count"]
    )

    st.bar_chart(
        sentiment_df,
        x="Sentiment",
        y="Count"
    )

with col2:

    st.subheader("🧠 Intent Distribution")

    intent_df = pd.DataFrame(
        intents.items(),
        columns=["Intent", "Count"]
    )

    st.bar_chart(
        intent_df,
        x="Intent",
        y="Count"
    )