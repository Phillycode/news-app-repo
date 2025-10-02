from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db import models
from .models import Article, Newsletter


@receiver(post_migrate)
def create_roles_and_permissions(sender, **kwargs):
    """
    Ensure groups (roles) and their permissions are created after migrations.
    This will run once per migration cycle for this app.
    """
    if sender.name != "news":
        return

    # --- Create Groups (Roles) ---
    reader_group, _ = Group.objects.get_or_create(name="Reader")
    journalist_group, _ = Group.objects.get_or_create(name="Journalist")
    editor_group, _ = Group.objects.get_or_create(name="Editor")
    publisher_group, _ = Group.objects.get_or_create(name="Publisher")

    # --- Get ContentTypes for Article and Newsletter ---
    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    # --- Assign Permissions ---
    # Reader: view only
    reader_perms = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct],
        codename__startswith="view_",
    )
    reader_group.permissions.set(reader_perms)

    # Journalist: add, change, delete, view for articles and newsletters
    journalist_perms = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct]
    )
    journalist_group.permissions.set(journalist_perms)

    # Editor: change, delete, view (but not add - journalists create content)
    editor_perms = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct]
    ).filter(
        models.Q(codename__startswith="change_")
        | models.Q(codename__startswith="delete_")
        | models.Q(codename__startswith="view_")
    )
    editor_group.permissions.set(editor_perms)

    # Publisher: change, delete, view (but NOT add)
    publisher_perms = Permission.objects.filter(
        content_type__in=[article_ct, newsletter_ct]
    ).filter(
        models.Q(codename__startswith="change_")
        | models.Q(codename__startswith="delete_")
        | models.Q(codename__startswith="view_")
    )
    publisher_group.permissions.set(publisher_perms)
