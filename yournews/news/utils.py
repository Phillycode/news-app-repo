import secrets
from datetime import timedelta
from django.utils import timezone
from hashlib import sha1
from .models import ResetToken, JournalistSubscription, PublisherSubscription
from .emails import EmailBuilder
from django.contrib.auth import get_user_model

User = get_user_model()


# Generate encrypted token for password reset
def generate_reset_url(user):
    """This function is responsible for creating a unique token
    object when a user requests a password reset.
    - The token is stored as 'hashed' in our database.
    - The unhashed token is sent in the email."""

    domain = "http://127.0.0.1:8000"
    app_name = ""
    reset_url = f"{domain}{app_name}/reset_password/"
    token = str(secrets.token_urlsafe(16))
    # Create expiry date/time using a timezone-aware value
    expiry_date = timezone.now() + timedelta(minutes=5)
    ResetToken.objects.create(
        user=user,
        token=sha1(token.encode()).hexdigest(),
        expiry_date=expiry_date,
    )
    reset_url += f"{token}/"
    return reset_url


def send_article_approval_notification(article):
    """Send email notification to journalist when article is
    approved/rejected."""
    try:
        journalist_user = article.journalist.user
        email = EmailBuilder.build_article_status_email(
            journalist_user, article
        )
        email.send()
        print(f"Article status email sent to {journalist_user.email}")
    except Exception as e:
        print(f"Failed to send article status email: {e}")


def send_article_subscriber_notifications(article):
    """Send email notifications to subscribers when an article is approved."""
    if article.status != "approved":
        return

    try:
        # Get subscribers to the journalist
        journalist_subscribers = JournalistSubscription.objects.filter(
            journalist=article.journalist, is_active=True
        ).select_related("reader")

        # Get subscribers to the publisher
        publisher_subscribers = PublisherSubscription.objects.filter(
            publisher=article.publisher, is_active=True
        ).select_related("reader")

        # Collect unique subscribers
        subscriber_emails = set()
        all_subscribers = list(journalist_subscribers) + list(
            publisher_subscribers
        )

        for subscription in all_subscribers:
            subscriber_user = subscription.reader
            if subscriber_user.email not in subscriber_emails:
                subscriber_emails.add(subscriber_user.email)
                try:
                    email = EmailBuilder.build_new_article_notification_email(
                        subscriber_user, article
                    )
                    email.send()
                    print(
                        f"Article notification sent to {subscriber_user.email}"
                    )
                except Exception as e:
                    print(
                        f"Failed to send article notification to "
                        f"{subscriber_user.email}: {e}"
                    )

    except Exception as e:
        print(f"Failed to send article subscriber notifications: {e}")


def send_newsletter_notifications(newsletter):
    """Send email notifications to subscribers when a newsletter is
    published."""
    try:
        # Get subscribers to the journalist
        journalist_subscribers = JournalistSubscription.objects.filter(
            journalist=newsletter.journalist, is_active=True
        ).select_related("reader")

        # Get subscribers to the publisher
        publisher_subscribers = PublisherSubscription.objects.filter(
            publisher=newsletter.publisher, is_active=True
        ).select_related("reader")

        # Collect unique subscribers
        subscriber_emails = set()
        all_subscribers = list(journalist_subscribers) + list(
            publisher_subscribers
        )

        for subscription in all_subscribers:
            subscriber_user = subscription.reader
            if subscriber_user.email not in subscriber_emails:
                subscriber_emails.add(subscriber_user.email)
                try:
                    email = (
                        EmailBuilder.build_new_newsletter_notification_email(
                            subscriber_user, newsletter
                        )
                    )
                    email.send()
                    print(
                        f"Newsletter notification sent to "
                        f"{subscriber_user.email}"
                    )
                except Exception as e:
                    print(
                        f"Failed to send newsletter notification to "
                        f"{subscriber_user.email}: {e}"
                    )

    except Exception as e:
        print(f"Failed to send newsletter notifications: {e}")


def send_newsletter_confirmation_email(newsletter):
    """Send confirmation email to journalist when newsletter is created."""
    try:
        journalist_user = newsletter.journalist.user
        email = EmailBuilder.build_newsletter_created_confirmation_email(
            journalist_user, newsletter
        )
        email.send()
        print(f"Newsletter confirmation email sent to {journalist_user.email}")
    except Exception as e:
        print(f"Failed to send newsletter confirmation email: {e}")
