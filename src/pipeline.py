from datetime import datetime, timezone

from src.data.models.article import ArticleModel, Priority
from src.ingestions.rss_reader import RSSReader
from src.storage.article_repository import ArticleRepository
from src.storage.database_connection import DatabaseConnection


def run_data_pipeline():
    print("🚀 Starting Data Collection Pipeline...")

    # 1. Initialize DB Connection and Repository — actually instantiate, so a
    # bad DATABASE_URL or unreachable host fails loudly here instead of later.
    try:
        db_conn = DatabaseConnection()
        repo = ArticleRepository(db_conn)
        print("💾 Connected to Neon Database successfully.")
    except Exception as e:
        print(f"❌ Database Initialization Failed: {e}")
        return

    # 2. Register all your collectors
    collectors = [
        # AlJazeeraScraper(),
        RSSReader(source_name="CNA - Singapore",
                  feed_url="https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6511"),
        # RSSReader(source_name="TechCrunch", feed_url="https://techcrunch.com/feed/"),
    ]
    # NOTE: replace the CNA URL above with the actual feed URL you're using —
    # I substituted a real-looking CNA RSS endpoint since " " can't be fetched,
    # but you should verify it's the one you actually want.

    total_inserted = 0
    total_skipped_duplicate = 0

    # 3. Loop through each collector dynamically
    for collector in collectors:
        source_identity = getattr(
            collector, "source_name", collector.__class__.__name__)
        print(f"\n🔄 Running collector: [{source_identity}]")

        # Step A: Fetch the raw components
        raw_items = collector.fetch_raw_data()
        print(f"📥 Fetched {len(raw_items)} raw elements.")

        collector_success_count = 0
        for raw_item in raw_items:
            try:
                parsed_article = collector.parse_content(raw_item)

                # Guard against empty entries or failed parsing elements
                if not parsed_article or not parsed_article.get("title"):
                    continue

                title = parsed_article["title"]
                now = datetime.now(timezone.utc)

                article = ArticleModel(
                    title=title,
                    slug=ArticleRepository.generate_slug(title),
                    description=parsed_article.get("summary", ""),
                    content=parsed_article.get("content")
                    or f"Link to original article: {parsed_article.get('link', '')}",
                    source_name=source_identity,
                    source_id=getattr(collector, "source_id", source_identity),
                    source_region=parsed_article.get(
                        "region", "Uncategorised"),
                    published_at=parsed_article.get("published_at", now),
                    updated_at=now,
                    priority=Priority.LOW,  # no scoring pipeline yet — see earlier TODO
                    tags=parsed_article.get("tags", []),
                )

                # Step C: Save to Neon database
                result = repo.create_article(article)
                if result is None:
                    # ON CONFLICT (slug) DO NOTHING — already exists, not an error
                    total_skipped_duplicate += 1
                else:
                    collector_success_count += 1

            except Exception as item_err:
                # Individual row failure shouldn't crash the entire loop
                print(
                    f"⚠️ Skipping individual article due to error: {item_err}")
                continue

        print(
            f"✅ Successfully processed & saved {collector_success_count} articles from [{source_identity}].")
        total_inserted += collector_success_count

    print(
        f"\n🏁 Pipeline execution finished. "
        f"Inserted: {total_inserted}, skipped duplicates: {total_skipped_duplicate}."
    )


if __name__ == "__main__":
    run_data_pipeline()
