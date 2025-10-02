from django.contrib import admin
from .models import (
    RoleApplication,
    Article,
    Editor,
    Publisher,
    Journalist,
    JournalistSubscription,
    PublisherSubscription,
)
from .emails import EmailBuilder
from .forms import RoleApplicationAdminForm


@admin.register(RoleApplication)
class RoleApplicationAdmin(admin.ModelAdmin):
    form = RoleApplicationAdminForm
    list_display = ("user", "applied_role", "status", "submitted_at")

    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle approval, rejection,
        and publisher assignment.
        """
        super().save_model(request, obj, form, change)

        user = obj.user

        if obj.status == "approved":
            # Update user role
            user.role = obj.applied_role
            user.save()

            # Since only readers should have subscriptions,
            # deactivate all subscriptions
            # when user role changes from reader to any other role
            JournalistSubscription.objects.filter(
                reader=user, is_active=True
            ).update(is_active=False)
            PublisherSubscription.objects.filter(
                reader=user, is_active=True
            ).update(is_active=False)

            # If approving editor/journalist, assign publisher
            publisher = form.cleaned_data.get("publisher")
            if obj.applied_role == "editor" and publisher:
                Editor.objects.get_or_create(user=user, publisher=publisher)
            elif obj.applied_role == "journalist" and publisher:
                Journalist.objects.get_or_create(
                    user=user, publisher=publisher
                )
            elif obj.applied_role == "publisher":
                Publisher.objects.get_or_create(
                    user=user, name=f"{user.username} Publishing"
                )

            # Send approval email
            email = EmailBuilder.build_role_approved_email(
                user, obj.applied_role
            )
            email.send()

        elif obj.status == "rejected":
            # Send rejection email
            email = EmailBuilder.build_role_rejected_email(
                user, obj.applied_role
            )
            email.send()


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "journalist",
        "publisher",
        "status",
        "created_at",
    )
    list_filter = ("status", "publisher")
    actions = ["approve_articles", "reject_articles"]

    def approve_articles(self, request, queryset):
        """
        Mark selected articles as approved.
        """
        updated = queryset.update(status="approved")
        self.message_user(request, f"{updated} article(s) have been approved.")

    approve_articles.short_description = "Approve selected articles"

    def reject_articles(self, request, queryset):
        """
        Mark selected articles as rejected.
        """
        updated = queryset.update(status="rejected")
        self.message_user(request, f"{updated} article(s) have been rejected.")

    reject_articles.short_description = "Reject selected articles"


@admin.register(JournalistSubscription)
class JournalistSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("reader", "journalist", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at", "journalist__publisher")
    search_fields = ("reader__username", "journalist__user__username")
    readonly_fields = ("subscribed_at",)


@admin.register(PublisherSubscription)
class PublisherSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("reader", "publisher", "subscribed_at", "is_active")
    list_filter = ("is_active", "subscribed_at", "publisher")
    search_fields = ("reader__username", "publisher__name")
    readonly_fields = ("subscribed_at",)
