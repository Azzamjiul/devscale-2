import json

from loguru import logger
from tools.broadcast import broadcast, broadcast_def
from tools.news import (
    news_data_processor,
    news_data_processor_def,
    news_reflection,
    news_scrapper,
    news_scrapper_def,
)
from utils import openai_client

tools = [
    broadcast_def,
    news_data_processor_def,
    news_scrapper_def,
]


def execute_function(function_name, function_args):
    if function_name == "broadcast":
        return broadcast(**function_args)
    elif function_name == "news_scrapper":
        return news_scrapper(**function_args)
    elif function_name == "news_data_processor":
        return news_data_processor(**function_args)
    elif function_name == "news_reflection":
        return news_reflection(**function_args)
    else:
        return {"error": f"Unknown function name: {function_name}"}


def process_research(topic: str):
    SYSTEM_PROMPT = """
        You are an AI News Aggregator tasked with gathering and processing news articles to deliver a comprehensive and structured report.

        # YOUR MISSION
        Aggregate news articles on any given topic and deliver a structured report with key insights and summaries.

        # NEWS AGGREGATION PROCESS
        1. **Select News Category** - Choose the most relevant category for the topic
        2. **Scrape News Articles** - Gather articles from reliable sources
        3. **Process News Data** - Format and summarize the articles into a user-friendly structure
        4. **Self-Reflect** - Evaluate the quality of the aggregated news data
        5. **Improve** - Refine the news aggregation process based on reflection
        6. **Deliver Final Report** - Provide a structured report with key insights

        # EXECUTION STANDARDS
        - **Always use available tools** - Utilize tools for scraping, processing, and reflection
        - **Focus on relevance** - Ensure the news articles are directly related to the topic
        - **Maintain clarity** - Deliver clear and concise summaries
        - **Ensure diversity** - Include a range of perspectives within the selected category

        # COMMUNICATION PROTOCOL
        Before each major step, announce your progress:
        - "🗂️ **CATEGORY SELECTION**: Choosing the most relevant news category..."
        - "🌐 **SCRAPING NEWS**: Gathering articles from reliable sources..."
        - "📝 **PROCESSING DATA**: Formatting and summarizing news articles..."
        - "🔍 **REFLECTING**: Evaluating the quality of the aggregated news..."
        - "✅ **COMPLETE**: News aggregation completed and report delivered"

        # SUCCESS CRITERIA
        - Relevant and diverse news articles
        - Clear and structured summaries
        - Comprehensive coverage of the topic
        - High-quality reflection and improvements
        """

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Query: {topic}. Remember: You MUST use the self_reflection tool to evaluate your news result before concluding.",
        },
    ]

    while True:
        response = openai_client.chat.completions.create(
            model="gpt-4.1-nano-2025-04-14",
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                logger.info(
                    f"Calling function {function_name} with args {function_args}"
                )
                function_response = execute_function(function_name, function_args)

                messages.append(
                    {
                        "role": "tool",
                        "content": function_response,
                        "tool_call_id": tool_call.id,
                    }
                )
        else:
            break

    return "Research Completed"


if __name__ == "__main__":
    topic = "give me news about latest US hot topics"
    process_research(topic)
