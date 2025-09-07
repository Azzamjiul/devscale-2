import xml.etree.ElementTree as ET

import openai
import requests
from constants import category_map
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

openai_client = openai


def scrapeURL(query: str):
    """
    Fetch news articles based on the query.
    Supports fetching news from various categories in ABC News.
    """

    category_url = category_map.get(query.lower())

    if category_url:
        response = requests.get(category_url)

        if response.status_code == 200:
            # Parse the XML response
            root = ET.fromstring(response.content)

            # Extract news items
            news_items = []
            for item in root.findall(".//item"):
                title_element = item.find("title")
                link_element = item.find("link")
                pub_date_element = item.find("pubDate")
                description_element = item.find("description")

                title = title_element.text if title_element is not None else "No title"
                link = link_element.text if link_element is not None else "No link"
                pub_date = (
                    pub_date_element.text
                    if pub_date_element is not None
                    else "No publication date"
                )
                description = (
                    description_element.text
                    if description_element is not None
                    else "No description"
                )

                news_items.append(
                    {
                        "title": title,
                        "link": link,
                        "pub_date": pub_date,
                        "description": description,
                    }
                )

            logger.info(f"Fetched {len(news_items)} news items for query: {query}")

            return news_items
        else:
            raise Exception(
                f"Failed to fetch news. HTTP Status Code: {response.status_code}"
            )
    else:
        raise ValueError("Unsupported query. Please provide a valid category.")


def getHtml(url: str):
    """
    Fetch HTML content from a given URL.

    Args:
        url (str): The URL to fetch HTML content from.

    Returns:
        str: The HTML content as a string.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        logger.error(f"Failed to fetch HTML. HTTP Status Code: {response.status_code}")
        return None


def extract_from_html(html: str):
    """
    Extract news data from HTML content.

    Args:
        html (str): The HTML content as a string.

    Returns:
        dict: A dictionary containing extracted news data.
    """
    import json
    import re

    match = re.search(r"window\['__abcnews__'\]\s*=\s*(\{[\s\S]*?\});", html)
    if match and match.group(1):
        try:
            json_data = json.loads(match.group(1))
            story = (
                json_data.get("page", {})
                .get("content", {})
                .get("story", {})
                .get("story")
            )

            if story:
                return {
                    "title": story.get("headline") or story.get("title") or "",
                    "description": story.get("description") or "",
                    "content": story.get("body") or "",
                }
        except json.JSONDecodeError:
            logger.error("❌ Failed to parse __abcnews__ JSON:")
            raise ValueError("❌ Failed to parse news JSON from HTML")

    return {}
