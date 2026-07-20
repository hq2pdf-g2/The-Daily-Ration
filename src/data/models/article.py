from dataclasses import asdict, dataclass, field
from typing import ClassVar, List, Optional
from datetime import datetime
from src.data.constants import COL_CONTENT_REGION, COL_PRIORITY, COL_SOURCE_ID, COL_SOURCE_REGION, DEFAULT_CATEGORY, DEFAULT_IMAGE_URL, DEFAULT_CONTENT_REGION
from src.data.constants import (
    COL_CATEGORY, COL_CONTENT, COL_DESCRIPTION, COL_IMAGE_URL,
    COL_PUBLISHED_AT, COL_SOURCE_NAME, COL_SLUG,
    COL_TITLE, COL_UPDATED_AT
)
from src.data.enums.priority import Priority

@dataclass
class ArticleModel:
    title: str
    slug: str
    description: str
    content: str
    source_name: str
    source_id: str
    source_region: str
    published_at: datetime
    updated_at: datetime
    content_region: Optional[str] = DEFAULT_CONTENT_REGION
    category: Optional[str] = DEFAULT_CATEGORY
    image_url: Optional[str] = DEFAULT_IMAGE_URL
    priority: Priority = Priority.LOW

    # Transient — no column on `articles`. The repository pulls this out and
    # writes it to `tags` / `article_tags` separately, in the same transaction
    # as the article insert. Must stay out of _COLUMN_MAP.
    tags: List[str] = field(default_factory=list)

    """Single source of truth for field mapping to databse column. 
    Add a row here (and a matching COL_* constant) whenever a field is added."""
    _COLUMN_MAP: ClassVar[dict] = {
        "title": COL_TITLE,
        "slug": COL_SLUG,
        "description": COL_DESCRIPTION,
        "content": COL_CONTENT,
        "source_name": COL_SOURCE_NAME,
        "source_id": COL_SOURCE_ID,
        "source_region": COL_SOURCE_REGION,
        "content_region": COL_CONTENT_REGION,
        "category": COL_CATEGORY,
        "image_url": COL_IMAGE_URL,
        "published_at": COL_PUBLISHED_AT,
        "updated_at": COL_UPDATED_AT,
        "priority": COL_PRIORITY
    }

    _TRANSIENT_FIELDS: ClassVar[set] = {"tags"}

    def to_db_dict(self) -> dict:
        """Maps dataclass attributes to `articles` column names. Fields with
        no column (e.g. tags) are deliberately excluded, not silently dropped —
        any field that's neither mapped nor transient raises KeyError, so
        forgetting to wire up a new field fails loudly instead of vanishing."""
        return {
            self._COLUMN_MAP[name]: value
            for name, value in asdict(self).items()
            if name not in self._TRANSIENT_FIELDS
        }