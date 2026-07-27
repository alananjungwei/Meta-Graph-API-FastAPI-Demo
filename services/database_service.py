import sqlite3
from datetime import datetime

DATABASE_NAME = "conversations.db"

def save_conversation(
    sender_id,
    message,
    intent,
    sentiment,
    reply,
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (
            sender_id,
            timestamp,
            message,
            intent,
            sentiment,
            reply
        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            sender_id,
            datetime.now().isoformat(),
            message,
            intent,
            sentiment,
            reply,
        ),
    )

    conn.commit()

    conn.close()

def get_connection():
    return sqlite3.connect(DATABASE_NAME)

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_id TEXT,

            timestamp TEXT,

            message TEXT,

            intent TEXT,

            sentiment TEXT,

            reply TEXT

        )
        """
    )

    conn.commit()
    conn.close()

def get_total_messages():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM conversations
        """
    )

    total = cursor.fetchone()[0]

    conn.close()

    return total