import logging
import re
from typing import Any, Dict, Optional

from psycopg.rows import dict_row

from src.data.constants import (
    COL_CATEGORY,
    COL_CONTENT,
    COL_CONTENT_REGION,
    COL_DESCRIPTION,
    COL_ID,
    COL_IMAGE_URL,
    COL_PUBLISHED_AT,
    COL_SLUG,
    COL_SOURCE_NAME,
    COL_TITLE,
    COL_UPDATED_AT,
    TABLE_ARTICLES,
)
from src.data.models.article import ArticleModel
from src.storage.database_connection import DatabaseConnection
from src.storage.tag_repository import attach_tags

logger = logging.getLogger(__name__)

# ==========================================
# SQL QUERIES (Using Schema Constants)
# ==========================================
def build_create_article_query(db_fields: dict) -> str:
    """Builds the INSERT statement directly from ArticleModel.to_db_dict(),
    so column list and param order can never drift apart again."""
    columns = ", ".join(db_fields.keys())
    placeholders = ", ".join(["%s"] * len(db_fields))
    return f"""
        INSERT INTO {TABLE_ARTICLES} ({columns})
        VALUES ({placeholders})
        ON CONFLICT ({COL_SLUG}) DO NOTHING
        RETURNING {COL_ID}, title, slug;
    """

GET_ARTICLE_BY_SLUG_QUERY = f"""
    SELECT * FROM {TABLE_ARTICLES} WHERE {COL_SLUG} = %s;
"""

UPDATE_ARTICLE_CONTENT_QUERY = f"""
    UPDATE {TABLE_ARTICLES}
    SET {COL_TITLE} = %s,
        {COL_CONTENT} = %s,
        {COL_DESCRIPTION} = %s,
        {COL_UPDATED_AT} = NOW()
    WHERE {COL_ID} = %s
    RETURNING {COL_ID}, {COL_TITLE}, {COL_SLUG}, {COL_UPDATED_AT};
"""
# Note: slug intentionally excluded from updates. Changing a slug after
# publication breaks external links/SEO; treat it as immutable post-create.
# If you do need to support it, it should be an explicit, separate operation
# (e.g. update_article_slug) so it's never an accidental side effect.

DELETE_ARTICLE_QUERY = f"DELETE FROM {TABLE_ARTICLES} WHERE {COL_ID} = %s;"


# ==========================================
# REPOSITORY IMPLEMENTATION
# ==========================================
class ArticleRepository:

    def __init__(self, db: Optional[DatabaseConnection] = None):
        # Injected rather than constructed here, so tests can pass a fake/mock connection.
        self.db = db or DatabaseConnection()

    @staticmethod
    def generate_slug(title: str) -> str:
        """Pure utility — kept here for reuse, but NOT called by create_article.
        Slug generation is the caller's/model's responsibility; the repository
        should persist what it's given, not silently rewrite it."""
        text = title.lower()
        text = re.sub(r"[^a-z0-9\s-]", "", text)
        return re.sub(r"[\s-]+", "-", text).strip("-")

    # ==========================================
    # C - CREATE
    # ==========================================
    def create_article(self, article: ArticleModel) -> Optional[Dict[str, Any]]:
        db_fields = article.to_db_dict()
        query = build_create_article_query(db_fields)

        with self.db.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(query, tuple(db_fields.values()))
                row = cur.fetchone()
                if row and article.tags:
                    attach_tags(cur, row["id"], article.tags)
                conn.commit()
                return row

    # ==========================================
    # R - READ
    # ==========================================
    def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(GET_ARTICLE_BY_SLUG_QUERY, (slug,))
                return cur.fetchone()

    # ==========================================
    # U - UPDATE
    # ==========================================
    def update_article_content(
        self, article_id: int, title: str, content: str, description: str
    ) -> Optional[Dict[str, Any]]:
        with self.db.get_connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute(
                    UPDATE_ARTICLE_CONTENT_QUERY,
                    (title, content, description, article_id),
                )
                conn.commit()
                return cur.fetchone()

    # ==========================================
    # D - DELETE
    # ==========================================
    def delete_article(self, article_id: int) -> None:
        with self.db.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(DELETE_ARTICLE_QUERY, (article_id,))
                conn.commit()

    # ==========================================
    # R - READ
    # ==========================================
    # def get_article_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
    #     """Fetches a single article and increments its view count."""
    #     with self.db.get_connection() as conn:
    #         with conn.cursor(row_factory=dict_row) as cur:
    #             cur.execute(GET_ARTICLE_BY_SLUG_QUERY, (slug,))
    #             article = cur.fetchone()

    #             if article:
    #                 cur.execute(INCREMENT_VIEW_COUNT_QUERY, (slug,))
    #                 conn.commit()

    #             return article

    # def list_published_articles(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    #     """Lists a paginated array of published articles ordered by newest first."""
    #     with self.db.get_connection() as conn:
    #         with conn.cursor(row_factory=dict_row) as cur:
    #             cur.execute(LIST_PUBLISHED_ARTICLES_QUERY, (limit, offset))
    #             return cur.fetchall()

    # # ==========================================
    # # U - UPDATE
    # # ==========================================
    # def update_article_content(self, article_id: str, title: str, content: str, description: str) -> bool:
    #     """Updates an existing article's text attributes and refreshes its slug."""
    #     new_slug = self._generate_slug(title)

    #     with self.db.get_connection() as conn:
    #         with conn.cursor() as cur:
    #             cur.execute(
    #                 UPDATE_ARTICLE_CONTENT_QUERY,
    #                 (title, new_slug, content, description, article_id),
    #             )
    #             conn.commit()
    #             return cur.rowcount > 0

    # # ==========================================
    # # D - DELETE
    # # ==========================================
    # def delete_article(self, article_id: str) -> bool:
    #     """Permanently removes an article row from disk."""
    #     with self.db.get_connection() as conn:
    #         with conn.cursor() as cur:
    #             cur.execute(DELETE_ARTICLE_QUERY, (article_id,))
    #             conn.commit()
    #             return cur.rowcount > 0
