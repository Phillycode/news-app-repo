import tweepy
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def post_article_to_twitter(article):
    """
    Simple function to post an approved article to Twitter.
    """
    logger.info(f"Starting Twitter posting for article: {article.title}")

    # Check if Twitter is configured
    if (
        not hasattr(settings, "TWITTER_API_KEY")
        or settings.TWITTER_API_KEY == "your_api_key_here"
    ):
        logger.warning("Twitter API not configured, skipping tweet")
        return False

    try:
        # Initialize Twitter client
        client = tweepy.Client(
            bearer_token=settings.TWITTER_BEARER_TOKEN,
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token=settings.TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

        # Create tweet text
        journalist_name = (
            article.journalist.user.get_full_name()
            or article.journalist.user.username
        )
        tweet_text = (
            f"New article published: {article.title}\nBy: {journalist_name}"
        )

        # Keep it under Twitter's character limit
        if len(tweet_text) > 280:
            tweet_text = tweet_text[:275] + "..."

        # Post the tweet
        logger.info(f"Posting tweet: {tweet_text}")
        response = client.create_tweet(text=tweet_text)

        if response.data:
            tweet_id = response.data["id"]
            logger.info(
                f"Successfully posted tweet {tweet_id} for article: "
                f"{article.title}"
            )
            return True
        else:
            logger.error(
                f"Failed to post tweet for article: {article.title} - "
                f"No response data"
            )
            return False

    except tweepy.Forbidden as e:
        logger.error(
            f"Twitter API forbidden (permissions issue) for article "
            f"{article.title}: {e}"
        )
        logger.error(
            "Check your Twitter app permissions - it needs 'Read and "
            "Write' access"
        )
        return False
    except tweepy.Unauthorized as e:
        logger.error(
            f"Twitter API unauthorized (credential issue) for article "
            f"{article.title}: {e}"
        )
        return False
    except Exception as e:
        logger.error(
            f"Unexpected error posting to Twitter for article "
            f"{article.title}: {e}"
        )
        return False
