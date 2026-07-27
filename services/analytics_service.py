from services.database_service import get_connection


def get_total_messages():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM conversations
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_sentiment_distribution():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT sentiment,
               COUNT(*)
        FROM conversations
        GROUP BY sentiment
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        sentiment: count
        for sentiment, count in rows
    }

def get_intent_distribution():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT intent,
               COUNT(*)
        FROM conversations
        GROUP BY intent
    """)

    rows = cursor.fetchall()

    conn.close()

    return {
        intent: count
        for intent, count in rows
    }