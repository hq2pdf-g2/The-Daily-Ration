import streamlit as st
from bs4 import BeautifulSoup
from html import escape
from src.storage.database_connection import DatabaseConnection
from src.storage.article_repository import ArticleRepository

# Initialize page configuration
st.set_page_config(page_title="The Daily Ration", page_icon="📰", layout="wide")
st.title("The Daily Ration")

# -----------------------------
# DATABASE INITIALIZATION
# -----------------------------
# Ensure the singleton connection is created once using your classes
try:
    db_conn = DatabaseConnection()
    article_repo = ArticleRepository()
except Exception as e:
    st.error(f"Failed to connect to the database: {e}")
    st.stop()

# -----------------------------
# REFACTORED FETCH FUNCTION
# -----------------------------
@st.cache_data(ttl="5m")  # Caches results for 5 minutes so it doesn't slam Neon DB
def load_processed_news():
    """Fetches already scraped and processed articles via the ArticleRepository."""
    try:
        # Utilizing your repository read method instead of raw queries
        # Note: adjust the limit/offset pagination defaults if you'd like
        articles = article_repo.list_published_articles(limit=50)
        return articles, None
    except Exception as e:
        return [], f"Error pulling articles from repository: {str(e)}"

# Fetch backend data
all_entries, fetch_error = load_processed_news()

if fetch_error:
    st.error(fetch_error)

# -----------------------------
# FILTERS & CONTROLS
# -----------------------------
view_mode = st.radio("View", ["Card View", "List View", "Compact View"], horizontal=True)
col_search, col_filter = st.columns([2, 1])

with col_search:
    search = st.text_input("Search articles", value="")

with col_filter:
    # Use fallback .get() methods to prevent KeyError if some fields are missing from your schema
    distinct_sources = list(set([entry.get("source_label", "Unknown") for entry in all_entries if entry.get("source_label")]))
    selected_source = st.selectbox("Filter by Source", ["All Sources"] + distinct_sources)

# -----------------------------
# FILTER & GROUPING LOGIC
# -----------------------------
filtered_entries = []
grouped_entries = {}

for entry in all_entries:
    # Safely pulling titles and sources matching your schema
    title_text = entry.get("title", "")
    source_label = entry.get("source_label", "General")
    
    text_match = search.lower() in title_text.lower()
    source_match = (selected_source == "All Sources") or (source_label == selected_source)
    
    if text_match and source_match:
        filtered_entries.append(entry)
        cat = entry.get("ai_category", "General")
        grouped_entries.setdefault(cat, []).append(entry)

# -----------------------------
# RENDER LAYOUTS
# -----------------------------
def display_single_article(entry, mode, col_context=None):
    title = escape(entry.get("title", "Untitled"))
    link = escape(entry.get("link", "#"))
    
    # Gracefully process summaries if they exist, fallback to content snippets if missing
    raw_summary = entry.get("summary") or entry.get("description") or "No content available."
    summary = escape(BeautifulSoup(raw_summary, "html.parser").get_text(strip=True)[:220])
    
    source_tag = escape(entry.get("source_label", "News"))
    ai_cat = escape(entry.get("ai_category", "General"))
    image_url = entry.get("image_url")

    if mode == "Card View" and col_context is not None:
        with col_context:
            with st.container(border=True):
                if image_url: 
                    st.image(image_url, use_container_width=True)
                st.markdown(f'<div class="source-tag">{source_tag} • {ai_cat}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-title">{title}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="card-summary">{summary}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="read-more"><a href="{link}" target="_blank">Read Full →</a></div>', unsafe_allow_html=True)

# Render logic
if not filtered_entries:
    st.info("No articles match your settings.")
else:
    for category, articles in grouped_entries.items():
        st.subheader(f"📁 {category} ({len(articles)})")
        
        # Displaying articles in grid layouts (3 columns)
        cols = st.columns(3)
        for idx, article in enumerate(articles):
            col_target = cols[idx % 3]
            display_single_article(article, view_mode, col_context=col_target)
