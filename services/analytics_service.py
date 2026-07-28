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

def get_unique_customers():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT sender_id)
        FROM conversations
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total

def get_recent_conversations(limit=20):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            timestamp,
            sender_id,
            message,
            intent,
            sentiment,
            reply
        FROM conversations
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "timestamp": row[0],
            "sender_id": row[1],
            "message": row[2],
            "intent": row[3],
            "sentiment": row[4],
            "reply": row[5],
        }
        for row in rows
    ]