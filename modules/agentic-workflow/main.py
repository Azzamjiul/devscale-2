from tools.broadcast import broadcast, broadcast_def
from tools.news import get_news_def
from utils import extract_from_html, getHtml, scrapeURL

tools = [
    broadcast_def,
    get_news_def,
]


def execute_function(function_name, function_args):
    if function_name == "broadcast":
        return broadcast(**function_args)
    else:
        return {"error": f"Unknown function name: {function_name}"}


if __name__ == "__main__":
    news_items = scrapeURL("us headlines")
    for item in news_items:
        print("\n\n=" * 80)
        print(f"Link: {item['link']}")

        # Fetching html and get article text
        htmlContent = getHtml(item["link"])

        if htmlContent is None:
            print("Failed to retrieve HTML content.")
            continue

        article = extract_from_html(htmlContent)
        if not article:
            print("Failed to extract article content.")
            continue

        print(f"Title: {article.get('title', 'N/A')}")
