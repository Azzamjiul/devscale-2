get_news_def = {
    "type": "function",
    "function": {
        "name": "get_news",
        "description": "Get news articles based on a query",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The query to search for",
                },
            },
            "required": ["query"],
        },
    },
}
