from django.core.management.base import BaseCommand

# Removed unused import: django.conf.settings
from news.models import Article
from news.twitter_service import post_article_to_twitter


class Command(BaseCommand):
    help = "Test posting a specific article to Twitter"

    def add_arguments(self, parser):
        parser.add_argument(
            "--article-id",
            type=int,
            help="ID of the article to post to Twitter",
        )

    def handle(self, *args, **options):
        article_id = options.get("article_id")

        if article_id:
            # Test specific article
            try:
                article = Article.objects.get(id=article_id, status="approved")
                self.stdout.write(
                    f"📰 Testing Twitter post for article: {article.title}"
                )
                self.stdout.write(
                    f"📝 By: {
                        article.journalist.user.get_full_name() or
                        article.journalist.user.username
                    }"
                )

                result = post_article_to_twitter(article)

                if result:
                    self.stdout.write(
                        self.style.SUCCESS(
                            "✅ Successfully posted to Twitter!"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            "❌ Failed to post to Twitter - "
                            "check logs for details"
                        )
                    )

            except Article.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(
                        f"❌ Article with ID {article_id} "
                        f"not found or not approved"
                    )
                )
        else:
            # List available articles
            approved_articles = Article.objects.filter(status="approved")[:5]

            if approved_articles.exists():
                self.stdout.write("📰 Available approved articles:")
                for article in approved_articles:
                    self.stdout.write(f"   ID: {article.id} - {article.title}")

                self.stdout.write(
                    "\n💡 Usage: python manage.py test_article_tweet "
                    "--article-id <ID>"
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        "⚠️  No approved articles found. "
                        "Approve an article first."
                    )
                )
