import streamlit as st
from utils import filter_conversations
from streamlit_autorefresh import st_autorefresh
from api import (
    get_total_messages,
    get_unique_customers,
    get_sentiment_distribution,
    get_intent_distribution,
    get_recent_conversations,
)

from components import (
    render_kpis,
    render_charts,
    render_recent_conversations,
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
# Fetch Dashboard Metrics
# -----------------------------
messages = get_total_messages()
customers = get_unique_customers()
sentiment = get_sentiment_distribution()
intents = get_intent_distribution()

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.header("⚙️ Dashboard Settings")

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=True
    )

    conversation_limit = st.slider(
        "Recent Conversations",
        min_value=5,
        max_value=50,
        value=20
    )

    search = st.text_input(
        "🔍 Search Messages"
    )

    intent_filter = st.selectbox(
        "🎯 Filter by Intent",
        ["All"] + sorted(intents.keys())
    )

    sentiment_filter = st.selectbox(
        "😊 Filter by Sentiment",
        ["All"] + sorted(sentiment.keys())
    )   

# -----------------------------
# Auto Refresh
# -----------------------------
if auto_refresh:
    st_autorefresh(
        interval=5000,
        key="dashboard_refresh"
    )

# -----------------------------
# Fetch Conversations
# -----------------------------
recent = get_recent_conversations(
    conversation_limit
)

# -----------------------------
# Apply Filters
# -----------------------------

recent = filter_conversations(
    recent,
    search=search,
    intent=intent_filter,
    sentiment=sentiment_filter,
)
# -----------------------------
# Render Components
# -----------------------------
render_kpis(messages, customers)

render_charts(sentiment, intents)

render_recent_conversations(recent)
