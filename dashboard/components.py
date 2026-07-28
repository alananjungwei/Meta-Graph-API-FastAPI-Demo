import pandas as pd
import streamlit as st


def render_kpis(messages, customers):

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


def render_charts(sentiment, intents):

    st.divider()

    st.subheader("📊 Key Metrics")

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("😊 Sentiment Distribution")

        sentiment_df = (
            pd.DataFrame(
                sentiment.items(),
                columns=["Sentiment", "Count"]
            )
            .sort_values("Count", ascending=False)
        )

        st.bar_chart(
            sentiment_df,
            x="Sentiment",
            y="Count"
        )

    with col2:

        st.subheader("🧠 Intent Distribution")

        intent_df = (
            pd.DataFrame(
                intents.items(),
                columns=["Intent", "Count"]
            )
            .sort_values("Count", ascending=False)
        )

        st.bar_chart(
            intent_df,
            x="Intent",
            y="Count"
        )

def render_recent_conversations(recent):

    recent_df = pd.DataFrame(recent)

    recent_df["timestamp"] = pd.to_datetime(
        recent_df["timestamp"]
    )

    recent_df["timestamp"] = recent_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    recent_df = recent_df.rename(
        columns={
            "timestamp": "Timestamp",
            "sender_id": "Customer ID",
            "message": "Customer Message",
            "intent": "Intent",
            "sentiment": "Sentiment"
        }
    )

    recent_df = recent_df[
        [
            "Timestamp",
            "Customer ID",
            "Customer Message",
            "Intent",
            "Sentiment"
        ]
    ]

    st.divider()

    st.subheader("💬 Recent Conversations")

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True
    )