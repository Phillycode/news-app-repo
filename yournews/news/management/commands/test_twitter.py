from django.core.management.base import BaseCommand
from django.conf import settings
import tweepy


class Command(BaseCommand):
    help = "Test Twitter API connection"

    def handle(self, *args, **options):
        self.stdout.write("🐦 Testing Twitter API connection...")

        # Check if Twitter is configured
        if (
            not hasattr(settings, "TWITTER_API_KEY")
            or settings.TWITTER_API_KEY == "your_api_key_here"
        ):
            self.stdout.write(
                self.style.ERROR(
                    "❌ Twitter API not configured. Please update your "
                    "settings.py with your Twitter API credentials."
                )
            )
            self.stdout.write(
                "Get your credentials from: https://developer.twitter.com/"
            )
            return

        try:
            # Test Twitter API connection
            client = tweepy.Client(
                bearer_token=settings.TWITTER_BEARER_TOKEN,
                consumer_key=settings.TWITTER_API_KEY,
                consumer_secret=settings.TWITTER_API_SECRET,
                access_token=settings.TWITTER_ACCESS_TOKEN,
                access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
            )

            # Get user info to test connection
            user = client.get_me()

            if user.data:
                self.stdout.write(
                    self.style.SUCCESS(
                        "✅ Twitter API connection successful!"
                    )
                )
                self.stdout.write(f"   Connected as: @{user.data.username}")
                self.stdout.write(f"   Name: {user.data.name}")

                # Ask if user wants to post a test tweet
                confirm = input("\nPost a test tweet? (y/N): ")
                if confirm.lower() == "y":
                    test_tweet = "🧪 Test tweet from Django News Application!"
                    response = client.create_tweet(text=test_tweet)

                    if response.data:
                        tweet_id = response.data["id"]
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"✅ Test tweet posted successfully! "
                                f"Tweet ID: {tweet_id}"
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.ERROR("❌ Failed to post test tweet")
                        )
                else:
                    self.stdout.write("⏭️  Skipping test tweet")
            else:
                self.stdout.write(
                    self.style.ERROR("❌ Could not retrieve user information")
                )

        except tweepy.Unauthorized:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Twitter API authentication failed. "
                    "Check your credentials."
                )
            )
        except tweepy.Forbidden:
            self.stdout.write(
                self.style.ERROR(
                    "❌ Twitter API access forbidden. "
                    "Check your app permissions."
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error connecting to Twitter API: {e}")
            )
