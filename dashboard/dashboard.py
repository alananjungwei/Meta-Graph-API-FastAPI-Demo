import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils import filter_conversations

from api import (
    get_total_messages,
    get_unique_customers,
    get_sentiment_distribution,
    get_intent_distribution,
    get_platform_distribution,
    get_recent_conversations,
)

from components import (
    render_kpis,
    render_charts,
    render_recent_conversations,
)


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="AI Customer Support",
    page_icon="🤖",
    layout="wide",
)


# ==================================================
# Header
# ==================================================

st.title(
    "🤖 AI Customer Support"
)

st.caption(
    "Manage AI-powered customer conversations "
    "across your connected channels."
)


# ==================================================
# Fetch Metrics
# ==================================================

messages = get_total_messages()

customers = get_unique_customers()

sentiment = get_sentiment_distribution()

intents = get_intent_distribution()

platforms = get_platform_distribution()


# ==================================================
# Sidebar
# ==================================================

with st.sidebar:

    st.header(
        "⚙️ Dashboard Settings"
    )

    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=True,
    )

    conversation_limit = st.slider(
        "Recent Conversations",
        min_value=5,
        max_value=50,
        value=20,
    )

    st.divider()

    # ----------------------------------------------
    # Channel filter
    # ----------------------------------------------

    st.subheader(
        "🔌 Channels"
    )

    platform_filter = st.selectbox(
        "Channel",
        [
            "All",
            "instagram",
            "messenger",
        ],
        format_func=lambda x: {
            "All": "All Channels",
            "instagram": "📸 Instagram",
            "messenger": "💬 Facebook Messenger",
        }.get(
            x,
            x,
        ),
    )

    # ----------------------------------------------
    # Search
    # ----------------------------------------------

    search = st.text_input(
        "🔍 Search Messages"
    )

    # ----------------------------------------------
    # Intent
    # ----------------------------------------------

    intent_filter = st.selectbox(
        "🎯 Filter by Intent",
        ["All"] + sorted(
            intents.keys()
        ),
    )

    # ----------------------------------------------
    # Sentiment
    # ----------------------------------------------

    sentiment_filter = st.selectbox(
        "😊 Filter by Sentiment",
        ["All"] + sorted(
            sentiment.keys()
        ),
    )


# ==================================================
# Auto Refresh
# ==================================================

if auto_refresh:

    st_autorefresh(
        interval=5000,
        key="dashboard_refresh",
    )


# ==================================================
# Connected Channels
# ==================================================

st.subheader(
    "🔌 Connected Channels"
)

col1, col2 = st.columns(2)


with col1:

    instagram_messages = platforms.get(
        "instagram",
        0,
    )

    st.metric(
        "📸 Instagram",
        f"{instagram_messages} messages",
    )


with col2:

    messenger_messages = platforms.get(
        "messenger",
        0,
    )

    st.metric(
        "💬 Facebook Messenger",
        f"{messenger_messages} messages",
    )


# ==================================================
# Main KPIs
# ==================================================

render_kpis(
    messages,
    customers,
    platforms,
)


# ==================================================
# Charts
# ==================================================

render_charts(
    sentiment,
    intents,
)


# ==================================================
# Fetch Conversations
# ==================================================

recent = get_recent_conversations(
    conversation_limit
)


# ==================================================
# Apply Filters
# ==================================================

recent = filter_conversations(
    recent,
    search=search,
    intent=intent_filter,
    sentiment=sentiment_filter,
    platform=platform_filter,
)


# ==================================================
# Render Conversations
# ==================================================

render_recent_conversations(
    recent
)
