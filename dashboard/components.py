import pandas as pd
import streamlit as st


# ==================================================
# KPI Cards
# ==================================================

def render_kpis(
    messages,
    customers,
    platform_counts,
):

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            label="📨 Messages",
            value=messages["total_messages"],
        )

    with col2:

        st.metric(
            label="👥 Customers",
            value=customers["unique_customers"],
        )

    with col3:

        st.metric(
            label="📸 Instagram",
            value=platform_counts.get(
                "instagram",
                0,
            ),
        )

    with col4:

        st.metric(
            label="💬 Messenger",
            value=platform_counts.get(
                "messenger",
                0,
            ),
        )


# ==================================================
# Charts
# ==================================================

def render_charts(
    sentiment,
    intents,
):

    st.divider()

    st.subheader("📊 Key Metrics")

    col1, col2 = st.columns(2)

    # ----------------------------------------------
    # Sentiment
    # ----------------------------------------------

    with col1:

        st.subheader(
            "😊 Sentiment Distribution"
        )

        sentiment_df = (
            pd.DataFrame(
                sentiment.items(),
                columns=[
                    "Sentiment",
                    "Count",
                ],
            )
            .sort_values(
                "Count",
                ascending=False,
            )
        )

        st.bar_chart(
            sentiment_df,
            x="Sentiment",
            y="Count",
        )

    # ----------------------------------------------
    # Intent
    # ----------------------------------------------

    with col2:

        st.subheader(
            "🧠 Intent Distribution"
        )

        intent_df = (
            pd.DataFrame(
                intents.items(),
                columns=[
                    "Intent",
                    "Count",
                ],
            )
            .sort_values(
                "Count",
                ascending=False,
            )
        )

        st.bar_chart(
            intent_df,
            x="Intent",
            y="Count",
        )


# ==================================================
# Recent Conversations
# ==================================================

def render_recent_conversations(
    recent,
):

    if not recent:

        st.info(
            "No conversations found."
        )

        return

    recent_df = pd.DataFrame(
        recent
    )

    # ----------------------------------------------
    # Timestamp
    # ----------------------------------------------

    recent_df["timestamp"] = pd.to_datetime(
        recent_df["timestamp"]
    )

    recent_df["timestamp"] = (
        recent_df["timestamp"]
        .dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    # ----------------------------------------------
    # Platform display name
    # ----------------------------------------------

    recent_df["Channel"] = (
        recent_df["platform"]
        .map(
            {
                "instagram": "📸 Instagram",
                "messenger": "💬 Messenger",
                "unknown": "❓ Unknown",
            }
        )
        .fillna("❓ Unknown")
    )

    # ----------------------------------------------
    # Rename columns
    # ----------------------------------------------

    recent_df = recent_df.rename(
        columns={
            "timestamp": "Timestamp",
            "sender_id": "Customer ID",
            "message": "Customer Message",
            "reply": "AI Reply",
            "intent": "Intent",
            "sentiment": "Sentiment",
        }
    )

    # ----------------------------------------------
    # Display columns
    # ----------------------------------------------

    recent_df = recent_df[
        [
            "Channel",
            "Timestamp",
            "Customer ID",
            "Customer Message",
            "AI Reply",
            "Intent",
            "Sentiment",
        ]
    ]

    # ----------------------------------------------
    # CSV export
    # ----------------------------------------------

    csv = recent_df.to_csv(
        index=False
    )

    st.divider()

    st.subheader(
        "💬 Recent Conversations"
    )

    st.download_button(
        label="📥 Export Conversations",
        data=csv,
        file_name="conversations.csv",
        mime="text/csv",
    )

    # ----------------------------------------------
    # Table
    # ----------------------------------------------

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
    )