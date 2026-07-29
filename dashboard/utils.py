def filter_conversations(
    conversations,
    search="",
    intent="All",
    sentiment="All",
):

    filtered = conversations

    if search:
        filtered = [
            row
            for row in filtered
            if search.lower() in row["message"].lower()
        ]

    if intent != "All":
        filtered = [
            row
            for row in filtered
            if row["intent"] == intent
        ]

    if sentiment != "All":
        filtered = [
            row
            for row in filtered
            if row["sentiment"] == sentiment
        ]

    return filtered