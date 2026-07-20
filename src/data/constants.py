from src.data.enums.priority import Priority

# ==========================================
# DATABASE SCHEMA CONSTANTS
# ==========================================s
TABLE_ARTICLES = "articles"

COL_ID = "id"
COL_TITLE = "title"
COL_SLUG = "slug"
COL_DESCRIPTION = "description"
COL_CONTENT = "content"
COL_SOURCE_NAME = "source_name"
COL_SOURCE_ID = "source_id"
COL_SOURCE_REGION = "source_region"
COL_CONTENT_REGION = "content_region"
COL_IMAGE_URL = "image_url"
COL_CATEGORY = "category"
COL_PUBLISHED_AT = "created_at"
COL_UPDATED_AT = "updated_at"
COL_PRIORITY = "priority"

TABLE_TAGS = "tags"
TABLE_ARTICLE_TAGS = "article_tags"

COL_TAG_ID = "id"
COL_TAG_NAME = "name"
COL_TAG_SLUG = "slug"
COL_ARTICLE_ID = "article_id"
COL_TAG_ID_FK = "tag_id"

# ==========================================
# DEFAULT VALUE CONSTANTS
# ==========================================
DEFAULT_CONTENT_REGION = "Uncategorised"
DEFAULT_CATEGORY = "Uncategorised"
DEFAULT_IMAGE_URL = ""
DEFAULT_PRIORITY = Priority.LOW