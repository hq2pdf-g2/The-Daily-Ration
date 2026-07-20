import scrapy
from fastapi import FastAPI
from scrapy.crawler import AsyncCrawlerRunner
from scrapy.utils.log import configure_logging
import uvicorn

app = FastAPI(title="Al Jazeera Scraping API")

# configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})

class AlJazeeraSpider(scrapy.Spider):
    name = "aljazeera_api"
    allowed_domains = ["aljazeera.com"]
    start_urls = ["https://www.aljazeera.com/middle-east/"]

    custom_settings = {
        "USER_AGENT": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "ROBOTSTXT_OBEY": False,
        "LOG_LEVEL": "ERROR",
    }

    def __init__(self, items_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items_list = items_list if items_list is not None else []

    def parse(self, response):
        articles = response.css("article.gc")

        for article in articles:
            title = article.css("h3.gc__title a span::text").get()
            link = article.css("h3.gc__title a::attr(href)").get()
            summary = article.css("div.gc__excerpt p::text").get()

            if link and link.startswith("/"):
                link = response.urljoin(link)

            if title and link:
                self.items_list.append({
                    "title": title.strip(),
                    "link": link,
                    "summary": summary.strip() if summary else "No summary available.",
                    "source_label": "Al Jazeera",
                    "published": "Recent",
                })

@app.get("/api/news/middle-east")
async def get_middle_east_news():
    scraped_data = []
    runner = AsyncCrawlerRunner()

    try:
        await runner.crawl(
            AlJazeeraSpider,
            items_list=scraped_data
        )

        # print(scraped_data)

        return {
            "status": "success",
            "count": len(scraped_data),
            "data": scraped_data,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "data": [],
        }


if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )