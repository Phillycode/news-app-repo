"""Email building utilities for the YourNews application.

This module provides centralized email construction for various
application events including authentication, notifications, and
role management.
"""

from django.core.mail import EmailMessage
from django.conf import settings


class EmailBuilder:
    """Utility class for building emails.

    Provides static methods to construct EmailMessage objects for
    various events where user notification is important.
    """

    @staticmethod
    def build_pw_reset_email(user, reset_url):
        """Build password reset email with secure reset link.

        Args:
            user: User requesting password reset
            reset_url (str): Secure token-based reset URL

        Returns:
            EmailMessage: Configured email ready to send
        """
        subject = "Password Reset"
        body = (
            f"Hi {user.username},\nHere is a link to reset your "
            f"password: {reset_url}"
        )
        return EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]
        )

    @staticmethod
    def build_role_approved_email(user, role):
        """Build role application approval notification email.

        Args:
            user: User whose application was approved
            role (str): The approved role name

        Returns:
            EmailMessage: Configured approval email
        """
        subject = "Your role application was approved"
        body = (
            f"Hi {user.username},\n\n"
            f"Congratulations! Your application for the role '{role}' "
            f"has been approved.\n"
            "You can now log in and start using your new permissions."
        )
        return EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]
        )

    @staticmethod
    def build_role_rejected_email(user, role):
        """Build role application rejection notification email.

        Args:
            user: User whose application was rejected
            role (str): The rejected role name

        Returns:
            EmailMessage: Configured rejection email
        """
        subject = "Your role application was rejected"
        body = (
            f"Hi {user.username},\n\n"
            f"We're sorry to inform you that your application for "
            f"the role '{role}' has been rejected.\n"
            "Feel free to apply again in the future."
        )
        return EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]
        )

    @staticmethod
    def build_article_status_email(user, article):
        """Build article status change notification email.

        Notifies journalist when their article is approved or rejected.

        Args:
            user: Journalist who wrote the article
            article: Article with updated status

        Returns:
            EmailMessage: Configured status notification email
        """
        status_display = article.status.capitalize()
        subject = f"Your Article '{article.title}' has been {status_display}"
        body = (
            f"Hi {user.username},\n\n"
            f"Your article titled '{article.title}' has been "
            f"{article.status} by the editor.\n\n"
            "Thank you for contributing to YourNews!"
        )
        email = EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [user.email]
        )
        return email

    @staticmethod
    def build_new_article_notification_email(subscriber_user, article):
        """Build new article notification for subscribers.

        Sent to readers subscribed to the article's
        journalist or publisher.

        Args:
            subscriber_user: Reader who is subscribed
            article: Newly approved article

        Returns:
            EmailMessage: Configured subscriber notification email
        """
        subject = f"New Article: {article.title}"
        author_name = (
            article.journalist.user.get_full_name()
            or article.journalist.user.username
        )
        body = (
            f"Hi {subscriber_user.username},\n\n"
            f"A new article has been published by {author_name}!\n\n"
            f"Title: {article.title}\n"
            f"Publisher: {article.publisher.name}\n\n"
            f"Read the full article at YourNews.\n\n"
            "Best regards,\nThe YourNews Team"
        )
        email = EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [subscriber_user.email]
        )
        return email

    @staticmethod
    def build_new_newsletter_notification_email(subscriber_user, newsletter):
        """Build new newsletter notification for subscribers.

        Sent to readers subscribed to the newsletter's journalist or
        publisher. Includes content preview.

        Args:
            subscriber_user: Reader who is subscribed
            newsletter: Newly published newsletter

        Returns:
            EmailMessage: Configured newsletter notification email
        """
        subject = f"New Newsletter: {newsletter.title}"
        author_name = (
            newsletter.journalist.user.get_full_name()
            or newsletter.journalist.user.username
        )
        body = (
            f"Hi {subscriber_user.username},\n\n"
            f"A new newsletter has been published by {author_name}!\n\n"
            f"Title: {newsletter.title}\n"
            f"Publisher: {newsletter.publisher.name}\n\n"
            f"Content Preview:\n"
            f"{newsletter.content[:200]}"
            f"{'...' if len(newsletter.content) > 200 else ''}\n\n"
            f"Read the full newsletter at YourNews.\n\n"
            "Best regards,\nThe YourNews Team"
        )
        email = EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [subscriber_user.email]
        )
        return email

    @staticmethod
    def build_newsletter_created_confirmation_email(
        journalist_user, newsletter
    ):
        """Build newsletter creation confirmation email.

        Confirms to journalist that their newsletter was published
        successfully and is now live.

        Args:
            journalist_user: Journalist who created the newsletter
            newsletter: The published newsletter

        Returns:
            EmailMessage: Configured confirmation email
        """
        subject = f"Newsletter Published: {newsletter.title}"
        body = (
            f"Hi {journalist_user.username},\n\n"
            f"Your newsletter '{newsletter.title}' has been "
            f"successfully published!\n\n"
            f"Your newsletter is now live and visible to all subscribers.\n\n"
            "Thank you for contributing to YourNews!\n\n"
            "Best regards,\nThe YourNews Team"
        )
        email = EmailMessage(
            subject, body, settings.DEFAULT_FROM_EMAIL, [journalist_user.email]
        )
        return email
