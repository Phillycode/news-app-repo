from django.core.mail import EmailMessage
from django.conf import settings


class EmailBuilder:

    @staticmethod
    def build_pw_reset_email(user, reset_url):
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
        """Email to notify subscribers about a new approved article."""
        subject = f"New Article: {article.title}"
        author_name = (
            article.journalist.user.get_full_name() or
            article.journalist.user.username
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
        """Email to notify subscribers about a new newsletter."""
        subject = f"New Newsletter: {newsletter.title}"
        author_name = (
            newsletter.journalist.user.get_full_name() or
            newsletter.journalist.user.username
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
        """Email to confirm newsletter creation to the journalist."""
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
