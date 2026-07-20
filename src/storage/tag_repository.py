from psycopg.rows import dict_row
from src.data.constants import (
    COL_ARTICLE_ID, COL_TAG_ID_FK, COL_TAG_NAME, COL_TAG_SLUG,
    TABLE_ARTICLE_TAGS, TABLE_TAGS,
)

GET_OR_CREATE_TAG_QUERY = f"""
    INSERT INTO {TABLE_TAGS} ({COL_TAG_NAME}, {COL_TAG_SLUG})
    VALUES (%s, %s)
    ON CONFLICT ({COL_TAG_NAME}) DO UPDATE SET {COL_TAG_NAME} = EXCLUDED.{COL_TAG_NAME}
    RETURNING id;
"""

LINK_ARTICLE_TAG_QUERY = f"""
    INSERT INTO {TABLE_ARTICLE_TAGS} ({COL_ARTICLE_ID}, {COL_TAG_ID_FK})
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING;
"""

def attach_tags(cur, article_id: int, tag_names: list[str]) -> None:
    """Must be called with a cursor from the SAME transaction as the article
    insert — partial tag writes on failure are worse than no tags."""
    for name in tag_names:
        slug = name.strip().lower().replace(" ", "-")
        cur.execute(GET_OR_CREATE_TAG_QUERY, (name.strip(), slug))
        tag_id = cur.fetchone()["id"]
        cur.execute(LINK_ARTICLE_TAG_QUERY, (article_id, tag_id))