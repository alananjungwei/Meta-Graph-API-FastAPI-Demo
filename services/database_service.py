import sqlite3
from datetime import datetime

DATABASE_NAME = "conversations.db"


# ==================================================
# Save Conversation
# ==================================================

def save_conversation(
    sender_id,
    message,
    intent,
    sentiment,
    reply,
    platform="unknown",
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
            reply,
            platform
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sender_id,
            datetime.now().isoformat(),
            message,
            intent,
            sentiment,
            reply,
            platform,
        ),
    )

    conn.commit()
    conn.close()


# ==================================================
# Database Connection
# ==================================================

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# ==================================================
# Initialize Database
# ==================================================

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # ----------------------------------------------
    # Create table for completely new databases
    # ----------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_id TEXT,

            timestamp TEXT,

            message TEXT,

            intent TEXT,

            sentiment TEXT,

            reply TEXT,

            platform TEXT DEFAULT 'unknown'

        )
        """
    )

    # ----------------------------------------------
    # Safe migration for existing databases
    # ----------------------------------------------

    cursor.execute(
        """
        PRAGMA table_info(conversations)
        """
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "platform" not in columns:

        cursor.execute(
            """
            ALTER TABLE conversations
            ADD COLUMN platform TEXT DEFAULT 'unknown'
            """
        )

    conn.commit()
    conn.close()


# ==================================================
# Analytics
# ==================================================

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