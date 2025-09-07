from constants import category_map
from utils import extract_from_html, getHtml, openai_client, scrapeURL


def news_scrapper():
    try:
        # System prompt for selecting a topic
        SYSTEM_PROMPT = """
        You are an intelligent agent tasked with selecting a news category from the following options:
        - Top Stories
        - US Headlines
        - International Headlines
        - Politics Headlines
        - Money Headlines
        - Technology Headlines
        - Health Headlines
        - Entertainment Headlines
        - Travel Headlines
        - Sports Headlines

        Respond with the exact category name.
        """

        response = openai_client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
            ],
        )

        if (
            not response.choices
            or not response.choices[0].message
            or not response.choices[0].message.content
        ):
            return {"error": "Invalid response from the agent."}

        selected_topic = response.choices[0].message.content.strip().lower()

        if selected_topic not in category_map:
            return {"error": "Invalid topic selected by the agent."}

        # Scrape raw news data
        news_items = scrapeURL(selected_topic)

        processed_articles = []

        for item in news_items:
            print("=" * 80)
            print(f"Link: {item['link']}")

            # Fetching HTML and get article text
            htmlContent = getHtml(item["link"])

            if htmlContent is None:
                print("Failed to retrieve HTML content.")
                continue

            article = extract_from_html(htmlContent)
            if not article:
                print("Failed to extract article content.")
                continue

            print(f"Title: {article.get('title', 'N/A')}")

            processed_articles.append(
                {
                    "link": item["link"],
                    "title": article.get("title", "N/A"),
                    "description": article.get("description", "N/A"),
                    "content": article.get("content", "N/A"),
                }
            )

        return processed_articles

    except Exception as e:
        return {"error": str(e)}


def news_data_processor(processed_articles):
    try:
        # System prompt for processing the data
        SYSTEM_PROMPT = """
        You are a news data processor. Your task is to format and summarize the following raw news data into a structured and user-friendly format.
        Each news item should include:
        - Title
        - Publication Date
        - Summary (based on the description)
        - Link
        """

        # Prepare the input for OpenAI API
        raw_data = "\n".join(
            [
                f"Title: {article['title']}\nDescription: {article['description']}\nContent: {article['content']}\nLink: {article['link']}"
                for article in processed_articles
            ]
        )

        response = openai_client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_data},
            ],
        )

        # Extract the content from the response
        content = response.choices[0].message.content
        return content

    except Exception as e:
        return {"error": str(e)}


def news_reflection(processed_articles):
    SYSTEM_PROMPT = """
        You are an expert evaluator for news data processing. Your task is to provide a detailed reflection on the quality of the processed news articles.

        # Evaluation Criteria
        1. **Relevance**: Are the articles relevant to the selected topic?
        2. **Clarity**: Are the titles, summaries, and content clear and well-structured?
        3. **Completeness**: Do the articles include all necessary information (title, publication date, summary, and link)?
        4. **Accuracy**: Is the information accurate and free from errors?
        5. **Diversity**: Do the articles cover a diverse range of perspectives within the topic?

        # Output Format
        **NEWS DATA QUALITY ASSESSMENT**
        
        **Overall Score**: [X/10]
        
        **Strengths**:
        - [List key strengths]
        
        **Areas for Improvement**:
        - [Specific improvements needed]
        
        **Missing Elements**:
        - [What's missing or could be added]
        
        **Recommendation**:
        - [Overall assessment and next steps]
        """

    try:
        # Prepare the input for OpenAI API
        raw_data = "\n".join(
            [
                f"Title: {article['title']}\nSummary: {article['description']}\nContent: {article['content']}\nLink: {article['link']}"
                for article in processed_articles
            ]
        )

        response = openai_client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": raw_data},
            ],
        )

        return response.choices[0].message.content

    except Exception as e:
        return {"error": str(e)}


news_scrapper_def = {
    "type": "function",
    "function": {
        "name": "news_scrapper",
        "description": "Scrape news articles based on a dynamically selected topic",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}

news_data_processor_def = {
    "type": "function",
    "function": {
        "name": "news_data_processor",
        "description": "Process and format scraped news articles into a structured format",
        "parameters": {
            "type": "object",
            "properties": {
                "processed_articles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "link": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["link", "title", "description", "content"],
                    },
                }
            },
            "required": ["processed_articles"],
        },
    },
}

news_reflection_def = {
    "type": "function",
    "function": {
        "name": "news_reflection",
        "description": "Reflect on the quality of processed news articles.",
        "parameters": {
            "type": "object",
            "properties": {
                "processed_articles": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "link": {"type": "string"},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["link", "title", "description", "content"],
                    },
                }
            },
            "required": ["processed_articles"],
        },
    },
}
