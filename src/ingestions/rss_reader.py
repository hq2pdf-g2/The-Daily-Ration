import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import feedparser

from src.ingestions.base_collector import BaseCollector


class RSSReader(BaseCollector):
    def __init__(self, source_name: str, feed_url: str):
        super().__init__()  # remove if BaseCollector has no __init__ to call
        self.source_name = source_name
        self.feed_url = feed_url

    def fetch_raw_data(self) -> List[Dict[str, Any]]:
        """Parses the RSS feed URL and returns raw entry dictionaries."""
        feed = feedparser.parse(self.feed_url)

        # feedparser signals failure via `bozo`, not exceptions — a malformed
        # or unreachable feed silently returns 0 entries unless you check this.
        if feed.bozo:
            print(
                f"⚠️ Feed parse issue for {self.source_name}: "
                f"{getattr(feed, 'bozo_exception', 'unknown error')}"
            )
            if not feed.entries:
                return []

        return [dict(entry) for entry in feed.entries]

    def parse_content(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalizes raw RSS entry fields into the app's standard schema."""
        image_url = ""
        thumb = raw_data.get("media_thumbnail", [])
        content_media = raw_data.get("media_content", [])

        if isinstance(thumb, list) and len(thumb) > 0:
            image_url = thumb[0].get("url", "")
        elif isinstance(content_media, list) and len(content_media) > 0:
            image_url = content_media[0].get("url", "")

        # Prefer full content (feedparser's `content` field) over the summary;
        # only fall back to the link in the pipeline if neither is available.
        full_content: Optional[str] = None
        content_blocks = raw_data.get("content")
        if isinstance(content_blocks, list) and len(content_blocks) > 0:
            full_content = content_blocks[0].get("value")

        published_at = self._parse_published_date(raw_data)

        tags = [
            t.get("term") for t in raw_data.get("tags", []) if t.get("term")
        ]

        return {
            "title": raw_data.get("title", "No title"),
            "link": raw_data.get("link", "#"),
            "summary": raw_data.get("summary", ""),
            "content": full_content,
            "source_label": self.source_name,
            "published_at": published_at,  # key now matches pipeline's lookup
            "image_url": image_url,
            "tags": tags,
        }

    @staticmethod
    def _parse_published_date(raw_data: Dict[str, Any]) -> Optional[datetime]:
        """feedparser exposes a pre-parsed struct_time at *_parsed when it can
        figure out the format — much more reliable than parsing the raw string
        ourselves. Returns None (not "now") if it truly can't be determined,
        so the pipeline's `now` fallback only kicks in when there's genuinely
        no date, rather than masking a parsing failure."""
        parsed_struct = raw_data.get("published_parsed") or raw_data.get("updated_parsed")
        if parsed_struct is None:
            return None
        return datetime.fromtimestamp(time.mktime(parsed_struct), tz=timezone.utc)