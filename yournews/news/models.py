from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.conf import settings


class CustomUser(AbstractUser):
    """
    CustomUser model:
    - Always starts off as a reader upon registration.
    - Can apply for one of the other three roles in the app.
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
        """
        Ensure user is placed into the correct group on save.
        Handle subscription cleanup when role changes from reader.
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
        """
        Deactivate all subscriptions for this user since only readers
        should have subscriptions.
        """
        from .models import JournalistSubscription, PublisherSubscription

        JournalistSubscription.objects.filter(
            reader=self, is_active=True
        ).update(is_active=False)

        PublisherSubscription.objects.filter(
            reader=self, is_active=True
        ).update(is_active=False)


class RoleApplication(models.Model):
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
    """
    Article model with different statuses based on editor review
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
    """
    Newsletter model - does not require editor review
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
    """
    Represents a reader's subscription to a specific journalist.
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
    """
    Represents a reader's subscription to a specific publisher.
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    token = models.CharField(max_length=255, unique=True)
    expiry_date = models.DateTimeField()
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Reset token for {self.user.username} (used: {self.used})"
