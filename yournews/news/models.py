"""Django models for the YourNews application.

This module contains all the data models for the news application,
including user management, role-based access control, content management,
and subscription system.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.conf import settings


class CustomUser(AbstractUser):
    """Custom user model with role-based permissions.

    Extends Django's AbstractUser to include role-based access control.
    Users start as readers and can apply for elevated roles (journalist,
    editor, publisher) through the role application system.

    Attributes:
        role (str): The user's role in the system. Defaults to 'reader'.
            Can be one of: 'reader', 'journalist', 'editor', 'publisher'.

    Note:
        - All new users start as 'reader' upon registration
        - Role changes trigger automatic subscription cleanup
        - Users are automatically assigned to appropriate Django groups
        - Only readers can have active subscriptions
    """

    ROLE_CHOICES = (
        ("reader", "Reader"),
        ("journalist", "Journalist"),
        ("editor", "Editor"),
        ("publisher", "Publisher"),
    )

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="reader"
    )

    def save(self, *args, **kwargs):
        """Save the user and update group membership.

        This method extends the default save behavior to:
        1. Update Django group membership based on the user's role
        2. Deactivate subscriptions if role changes from 'reader'

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments

        Returns:
            None
        """
        # Check if this is an update (not a new user) and role is changing
        is_role_changing = False
        old_role = None
        if self.pk:  # User already exists
            try:
                old_user = CustomUser.objects.get(pk=self.pk)
                old_role = old_user.role
                is_role_changing = old_role != self.role
            except CustomUser.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        # Update group membership
        group, _ = Group.objects.get_or_create(name=self.role.capitalize())
        self.groups.clear()
        self.groups.add(group)

        # If role changed from reader, deactivate subscriptions
        if is_role_changing and old_role == "reader" and self.role != "reader":
            self._deactivate_subscriptions()

    # Internal helper method
    def _deactivate_subscriptions(self):
        """Deactivate all subscriptions for this user.

        Internal helper method that deactivates all subscriptions for a user
        when their role changes from 'reader'. This is necessary because only
        users with the 'reader' role should have active subscriptions.

        Returns:
            None
        """
        from .models import JournalistSubscription, PublisherSubscription

        JournalistSubscription.objects.filter(
            reader=self, is_active=True
        ).update(is_active=False)

        PublisherSubscription.objects.filter(
            reader=self, is_active=True
        ).update(is_active=False)


class RoleApplication(models.Model):
    """Model for managing user role change applications.

    This model tracks applications for role changes and their approval
    status. Users start as readers and can apply for journalist, editor,
    or publisher roles. Applications must be approved by an admin before
    the role is granted.

    Attributes:
        user (ForeignKey): The user applying for a role change
        applied_role (str): The role the user is applying for
        motivation (str): The user's justification for the role change
        status (str): Current application status
            (pending, approved, rejected)
        submitted_at (datetime): When the application was submitted

    Note:
        - Only admins can approve or reject applications
        - Approved applications may require assigning the user to a
          publisher
        - Approving a role change triggers subscription deactivation
    """

    ROLE_CHOICES = (
        ("journalist", "Journalist"),
        ("editor", "Editor"),
        ("publisher", "Publisher"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_applications",
    )
    applied_role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    motivation = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=(
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ),
        default="pending",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user.username} applied for {self.applied_role} "
            f"({self.status})"
        )


class Publisher(models.Model):
    """Publisher entity representing a news organization.

    Publishers are top-level organizational entities that employ editors
    and journalists. They serve as containers for articles and newsletters,
    and can be subscribed to by readers.

    Attributes:
        user (OneToOneField): The user with publisher role associated with
            this entity
        name (str): The unique name of the publisher organization
        description (str, optional): A detailed description of the publisher

    Relationships:
        - Has many editors (Editor model)
        - Has many journalists (Journalist model)
        - Has many articles (Article model)
        - Has many newsletters (Newsletter model)
        - Has many subscribers (PublisherSubscription model)

    Note:
        When a user's role changes to 'publisher', a Publisher entity is
        automatically created with a default name based on the username.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="publisher_profile",
        limit_choices_to={"role": "publisher"},
    )
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name or (self.user.get_full_name() or self.user.username)


class Editor(models.Model):
    """Editor profile for users with the 'editor' role.

    Editors are responsible for reviewing and approving/rejecting articles
    submitted by journalists. They are associated with a specific publisher
    and can only manage content from that publisher.

    Attributes:
        user (OneToOneField): The user with editor role
        publisher (ForeignKey): The publisher this editor works for

    Permissions:
        - Approve/reject articles from their publisher
        - Edit articles from their publisher
        - Delete articles from their publisher
        - Edit/delete newsletters from their publisher

    Note:
        Editors are assigned to a publisher by an admin when their
        role application is approved.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="editor_profile",
        limit_choices_to={"role": "editor"},
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="editors"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Journalist(models.Model):
    """Journalist profile for users with the 'journalist' role.

    Journalists create content in the form of articles (which require
    editor approval) and newsletters (which are published directly). They
    are associated with a specific publisher and readers can subscribe to
    them.

    Attributes:
        user (OneToOneField): The user with journalist role
        publisher (ForeignKey): The publisher this journalist works for

    Relationships:
        - Has many articles (Article model)
        - Has many newsletters (Newsletter model)
        - Has many subscribers (JournalistSubscription model)

    Permissions:
        - Create articles and newsletters
        - Edit/delete their own articles and newsletters
        - View all articles and newsletters

    Note:
        Journalists are assigned to a publisher by an admin when their
        role application is approved.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="journalist_profile",
        limit_choices_to={"role": "journalist"},
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="journalists"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Article(models.Model):
    """Article model for news content that requires editorial approval.

    Articles are created by journalists and must be approved by an editor
    before becoming visible to readers. Each article belongs to a journalist
    and their associated publisher.

    Attributes:
        title (str): The article headline
        content (str): The full article text content
        journalist (ForeignKey): The author of the article
        publisher (ForeignKey): The publisher the article belongs to
        status (str): Current article status
            (pending, approved, rejected)
        created_at (datetime): When the article was created
        updated_at (datetime): When the article was last updated

    Workflow:
        1. Journalist creates article (status: pending)
        2. Editor reviews article
        3. Editor approves or rejects article (status: approved/rejected)
        4. If approved, article is visible to readers and notifications
           are sent
        5. If approved, article is automatically posted to Twitter
           (if enabled)

    Note:
        Only approved articles are visible to general readers.
        Journalists and editors can see all articles regardless of
        status.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    journalist = models.ForeignKey(
        Journalist, on_delete=models.CASCADE, related_name="articles"
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="articles"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """Newsletter model for direct-to-subscriber content.

    Newsletters are created by journalists and do not require editor
    approval. They are immediately available and notifications are sent
    to subscribers upon creation.

    Attributes:
        title (str): The newsletter title
        content (str): The full newsletter content
        journalist (ForeignKey): The author of the newsletter
        publisher (ForeignKey): The publisher the newsletter belongs to
        created_at (datetime): When the newsletter was created
        updated_at (datetime): When the newsletter was last updated

    Workflow:
        1. Journalist creates newsletter
        2. Newsletter is immediately available
        3. Email notifications are sent to subscribers of the journalist
           and publisher

    Note:
        Unlike articles, newsletters do not have approval/rejection status
        and are immediately visible after creation.
    """

    title = models.CharField(max_length=255)
    content = models.TextField()
    journalist = models.ForeignKey(
        Journalist, on_delete=models.CASCADE, related_name="newsletters"
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="newsletters"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class JournalistSubscription(models.Model):
    """Subscription relationship between readers and journalists.

    Represents a reader's subscription to a specific journalist.
    Subscriptions affect content filtering and email notifications for
    articles and newsletters.

    Attributes:
        reader (ForeignKey): The user with 'reader' role who is
            subscribing
        journalist (ForeignKey): The journalist being subscribed to
        subscribed_at (datetime): When the subscription was created
        is_active (bool): Whether the subscription is currently active

    Effects:
        - Readers receive email notifications about new content
        - API responses filter content based on subscriptions
        - Web interface highlights subscription status

    Note:
        Subscriptions are automatically deactivated (not deleted) when a
        reader's role changes to anything other than 'reader'.
    """

    reader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="journalist_subscriptions",
        limit_choices_to={"role": "reader"},
    )
    journalist = models.ForeignKey(
        Journalist, on_delete=models.CASCADE, related_name="subscribers"
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("reader", "journalist")
        verbose_name = "Journalist Subscription"
        verbose_name_plural = "Journalist Subscriptions"

    def __str__(self):
        return f"{self.reader.username} subscribed to {self.journalist}"


class PublisherSubscription(models.Model):
    """Subscription relationship between readers and publishers.

    Represents a reader's subscription to a specific publisher.
    Subscribing to a publisher provides access to all content from that
    publisher's journalists.

    Attributes:
        reader (ForeignKey): The user with 'reader' role who is
            subscribing
        publisher (ForeignKey): The publisher being subscribed to
        subscribed_at (datetime): When the subscription was created
        is_active (bool): Whether the subscription is currently active

    Effects:
        - Readers receive email notifications about new content
        - API responses filter content based on subscriptions
        - Web interface highlights subscription status
        - Provides access to all content from the publisher's
          journalists

    Note:
        Subscriptions are automatically deactivated (not deleted) when a
        reader's role changes to anything other than 'reader'.
    """

    reader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="publisher_subscriptions",
        limit_choices_to={"role": "reader"},
    )
    publisher = models.ForeignKey(
        Publisher, on_delete=models.CASCADE, related_name="subscribers"
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("reader", "publisher")
        verbose_name = "Publisher Subscription"
        verbose_name_plural = "Publisher Subscriptions"

    def __str__(self):
        return f"{self.reader.username} subscribed to {self.publisher.name}"


class ResetToken(models.Model):
    """Secure token for password reset functionality.

    Stores secure tokens for the password reset process with expiration
    and one-time use functionality.

    Attributes:
        user (ForeignKey): The user requesting password reset
        token (str): Unique token string (stored as SHA-1 hash)
        expiry_date (datetime): When the token expires
        used (bool): Whether the token has been used

    Workflow:
        1. User requests password reset
        2. System generates token and sends email with reset URL
        3. User clicks URL and resets password
        4. Token is marked as used to prevent reuse

    Security features:
        - Tokens are hashed before storage
        - Tokens expire after a set time period
        - Tokens can only be used once
        - Invalid/expired tokens are rejected
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    token = models.CharField(max_length=255, unique=True)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset token for {self.user.username} (used: {self.used})"
