from src.ingestions.base_collector import BaseCollector 
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests

class AlJazeeraScraper(BaseCollector):
    def __init__(self):
        self.url = "https://www.aljazeera.com/middle-east/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """Requests the live webpage and extracts raw HTML elements as dictionaries."""
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            if response.status_code != 200:
                print(f"Al Jazeera returned status code {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, "html.parser")
            # Return raw string representation or bs4 objects wrapped up
            return [{"html_element": article} for article in soup.find_all("article")]
        except Exception as e:
            print(f"Error requesting Al Jazeera: {e}")
            return []

    def parse_content(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parses raw HTML block structures out to the uniform schema format."""
        article = raw_data.get("html_element")
        if not article:
            return {}

        # 1. Extract Title & Link
        title_el = article.find(["h2", "h3"], class_="article-card__title") or article.find(["h2", "h3"])
        if not title_el:
            return {}
            
        title = title_el.get_text(strip=True)
        link_el = title_el.find("a") or article.find("a", class_="u-clickable-card__link")
        link = link_el.get("href") if link_el else "#"
        if link.startswith("/"): 
            link = f"https://www.aljazeera.com{link}"
            
        # 2. Extract Summary
        summary_el = article.find(class_="article-card__excerpt") or article.find("p")
        summary = summary_el.get_text(strip=True) if summary_el else "No summary available."
        
        # 3. Extract Published Date
        date_el = article.find("span", class_="screen-reader-text")
        if date_el and "Published On" in date_el.get_text():
            published = date_el.get_text().replace("Published On", "").strip()
        else:
            date_simple = article.find("div", class_="date-simple")
            published = date_simple.get_text(strip=True) if date_simple else "Recent News"

        # 4. Extract Image URL
        img_el = article.find("img")
        image_url = img_el.get("src") if img_el else ""
        if image_url.startswith("/"): 
            image_url = f"https://www.aljazeera.com{image_url}"

        return {
            "title": title,
            "link": link,
            "summary": summary,
            "source_label": "Al Jazeera",
            "published": published,
            "image_url": image_url
        }