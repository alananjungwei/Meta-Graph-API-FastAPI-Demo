def filter_conversations(
    conversations,
    search="",
    intent="All",
    sentiment="All",
    platform="All",
):

    filtered = conversations

    # ----------------------------------------------
    # Search
    # ----------------------------------------------

    if search:

        filtered = [
            row
            for row in filtered
            if search.lower() in row["message"].lower()
        ]

    # ----------------------------------------------
    # Intent
    # ----------------------------------------------

    if intent != "All":

        filtered = [
            row
            for row in filtered
            if row["intent"] == intent
        ]

    # ----------------------------------------------
    # Sentiment
    # ----------------------------------------------

    if sentiment != "All":

        filtered = [
            row
            for row in filtered
            if row["sentiment"] == sentiment
        ]

    # ----------------------------------------------
    # Platform
    # ----------------------------------------------

    if platform != "All":

        filtered = [
            row
            for row in filtered
            if row.get("platform", "unknown") == platform
        ]

    return filtered