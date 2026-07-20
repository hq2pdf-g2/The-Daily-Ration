from dataclasses import dataclass
from typing import Optional

@dataclass
class TagModel:
    name: str
    slug: str
    id: Optional[int] = None


def get_or_create_tag(conn, name: str) -> int:
    slug = name.strip().lower().replace(" ", "-")
    row = conn.execute(
        "INSERT INTO tags (name, slug) VALUES (%s, %s) "
        "ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name "
        "RETURNING id",
        (name, slug),
    ).fetchone()
    return row["id"]


def set_article_tags(conn, article_id: int, tag_names: list[str]) -> None:
    conn.execute("DELETE FROM article_tags WHERE article_id = %s", (article_id,))
    for name in tag_names:
        tag_id = get_or_create_tag(conn, name)
        conn.execute(
            "INSERT INTO article_tags (article_id, tag_id) VALUES (%s, %s)",
            (article_id, tag_id),
        )