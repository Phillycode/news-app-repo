from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import (
    AuthenticationForm,
    RegisterForm,
    RoleApplicationForm,
    ForgotPasswordForm,
    ResetPasswordForm,
    ArticleForm,
    NewsletterForm,
)
from .models import (
    Article,
    Newsletter,
    RoleApplication,
    ResetToken,
    Journalist,
    Publisher,
    Editor,
    JournalistSubscription,
    PublisherSubscription,
)
from django.db import models
from django.contrib import messages
from .utils import (
    generate_reset_url,
    send_article_approval_notification,
    send_article_subscriber_notifications,
    send_newsletter_notifications,
    send_newsletter_confirmation_email,
)
from .emails import EmailBuilder
from .twitter_service import post_article_to_twitter
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from hashlib import sha1

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # All new users start as "reader"
            user.role = "reader"
            user.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")
            return redirect("news:article_list")
    else:
        form = RegisterForm()
    return render(request, "news/register.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in.")
                return redirect("news:article_list")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "news/login.html", {"form": form})


def logout_user(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("news:login")


@login_required
def apply_for_role(request):
    if request.user.role != "reader":
        messages.warning(request, "Only readers can apply for new roles.")
        return redirect("news:article_list")

    # Check if user already has a pending application
    existing_application = RoleApplication.objects.filter(
        user=request.user, status="pending"
    ).first()

    if existing_application:
        return render(request, "news/application_pending.html")

    # Check if user has any active subscriptions
    journalist_subscriptions_count = JournalistSubscription.objects.filter(
        reader=request.user, is_active=True
    ).count()
    publisher_subscriptions_count = PublisherSubscription.objects.filter(
        reader=request.user, is_active=True
    ).count()
    total_subscriptions = (
        journalist_subscriptions_count + publisher_subscriptions_count
    )

    if request.method == "POST":
        form = RoleApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.status = "pending"
            application.save()
            return render(request, "news/applied.html")
    else:
        form = RoleApplicationForm()

    context = {
        "form": form,
        "has_subscriptions": total_subscriptions > 0,
        "total_subscriptions": total_subscriptions,
        "journalist_subscriptions_count": journalist_subscriptions_count,
        "publisher_subscriptions_count": publisher_subscriptions_count,
    }

    return render(request, "news/apply_for_role.html", context)


@login_required
def article_list(request):
    articles = Article.objects.filter(status="approved").order_by(
        "-created_at"
    )
    return render(request, "news/article_list.html", {"articles": articles})


def article_detail(request, pk):
    if request.user.is_authenticated and request.user.role in [
        "editor",
        "journalist",
    ]:
        article = get_object_or_404(Article, pk=pk)  # no status filter
    else:
        article = get_object_or_404(Article, pk=pk, status="approved")

    context = {"article": article}

    # Add subscription status for readers
    if request.user.is_authenticated and request.user.role == "reader":
        context["is_subscribed_to_journalist"] = (
            JournalistSubscription.objects.filter(
                reader=request.user,
                journalist=article.journalist,
                is_active=True,
            ).exists()
        )
        context["is_subscribed_to_publisher"] = (
            PublisherSubscription.objects.filter(
                reader=request.user,
                publisher=article.publisher,
                is_active=True,
            ).exists()
        )

    return render(request, "news/article_detail.html", context)


def forgot_password(request):
    if request.method == "POST":
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "No user with this email exists.")
                return render(
                    request, "news/forgot_password.html", {"form": form}
                )

            # Generate reset URL
            reset_url = generate_reset_url(user)

            # Build and send email
            email_msg = EmailBuilder.build_pw_reset_email(user, reset_url)
            email_msg.send()

            messages.success(
                request, "Password reset link sent. Check your email."
            )
            return redirect("news:login")
    else:
        form = ForgotPasswordForm()

    return render(request, "news/forgot_password.html", {"form": form})


def reset_password(request, token):
    # Look up token in DB (hashed version)
    hashed_token = sha1(token.encode()).hexdigest()
    try:
        reset_obj = ResetToken.objects.get(token=hashed_token, used=False)
    except ResetToken.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect("news:login")

    # Check expiry
    if reset_obj.expiry_date < timezone.now():
        messages.error(request, "This reset link has expired.")
        return redirect("news:forgot_password")

    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            user = reset_obj.user
            user.password = make_password(new_password)
            user.save()

            # Mark token as used
            reset_obj.used = True
            reset_obj.save()

            messages.success(
                request, "Your password has been reset successfully."
            )
            return redirect("news:login")
    else:
        form = ResetPasswordForm()

    return render(request, "news/reset_password.html", {"form": form})


@login_required
def editor_dashboard(request):
    if request.user.role != "editor":
        messages.warning(request, "You do not have access to this page.")
        return redirect("news:article_list")

    editor = request.user.editor_profile
    # Get all articles from this editor's publisher, organized by status
    articles = Article.objects.filter(publisher=editor.publisher).order_by(
        "status", "-created_at"
    )

    # Organize articles by status for the template
    pending_articles = articles.filter(status="pending")
    approved_articles = articles.filter(status="approved")
    rejected_articles = articles.filter(status="rejected")

    context = {
        "articles": articles,
        "pending_articles": pending_articles,
        "approved_articles": approved_articles,
        "rejected_articles": rejected_articles,
        "total_count": articles.count(),
        "pending_count": pending_articles.count(),
        "approved_count": approved_articles.count(),
        "rejected_count": rejected_articles.count(),
        "publisher_name": editor.publisher.name,
    }

    return render(request, "news/editor_dashboard.html", context)


@login_required
def approve_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if (
        request.user.role == "editor"
        and article.publisher == request.user.editor_profile.publisher
    ):
        article.status = "approved"
        article.save()

        # Send email notifications
        send_article_approval_notification(article)
        send_article_subscriber_notifications(article)

        # Post the approved article to Twitter
        post_article_to_twitter(article)

        messages.success(request, f"Article '{article.title}' approved!")
    else:
        messages.error(request, "You cannot approve this article.")
    return redirect("news:editor_dashboard")


@login_required
def reject_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if (
        request.user.role == "editor"
        and article.publisher == request.user.editor_profile.publisher
    ):
        article.status = "rejected"
        article.save()

        # Send email notification to journalist
        send_article_approval_notification(article)

        messages.info(request, f"Article '{article.title}' rejected.")
    else:
        messages.error(request, "You cannot reject this article.")
    return redirect("news:editor_dashboard")


@login_required
def submit_article(request):
    if request.user.role != "journalist":
        messages.warning(request, "Only journalists can submit articles.")
        return redirect("news:article_list")

    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.journalist = request.user.journalist_profile
            article.publisher = request.user.journalist_profile.publisher
            article.save()
            messages.success(
                request,
                "Article submitted successfully! Waiting for editor approval.",
            )
            return redirect("news:article_list")
    else:
        form = ArticleForm()

    return render(request, "news/submit_article.html", {"form": form})


@login_required
def update_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Permission checks: editors can edit any article in their publisher,
    # journalists can only edit their own articles
    if request.user.role == "editor":
        if article.publisher != request.user.editor_profile.publisher:
            messages.error(
                request, "You can only edit articles from your publisher."
            )
            return redirect("news:article_detail", pk=pk)
    elif request.user.role == "journalist":
        if article.journalist != request.user.journalist_profile:
            messages.error(request, "You can only edit your own articles.")
            return redirect("news:article_detail", pk=pk)
    else:
        messages.error(request, "You don't have permission to edit articles.")
        return redirect("news:article_detail", pk=pk)

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            updated_article = form.save()
            messages.success(
                request,
                f"Article '{updated_article.title}' updated successfully!",
            )
            return redirect("news:article_detail", pk=pk)
    else:
        form = ArticleForm(instance=article)

    return render(
        request, "news/update_article.html", {"form": form, "article": article}
    )


@login_required
def delete_article(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Permission checks: Editors can delete articles from their publisher
    # Journalists can delete their own articles only
    if request.user.role == "editor":
        if article.publisher != request.user.editor_profile.publisher:
            messages.error(
                request, "You can only delete articles from your publisher."
            )
            return redirect("news:article_detail", pk=pk)
    elif request.user.role == "journalist":
        if article.journalist != request.user.journalist_profile:
            messages.error(request, "You can only delete your own articles.")
            return redirect("news:article_detail", pk=pk)
    else:
        messages.error(
            request, "You don't have permission to delete articles."
        )
        return redirect("news:article_detail", pk=pk)

    if request.method == "POST":
        article_title = article.title
        article.delete()
        messages.success(
            request, f"Article '{article_title}' deleted successfully!"
        )
        return redirect("news:article_list")

    return render(request, "news/delete_article.html", {"article": article})


@login_required
def journalist_dashboard(request):
    if request.user.role != "journalist":
        messages.warning(request, "You do not have access to this page.")
        return redirect("news:article_list")

    journalist = request.user.journalist_profile
    # Get all articles by this journalist, ordered by status and creation date
    articles = Article.objects.filter(journalist=journalist).order_by(
        "status", "-created_at"
    )

    # Get all newsletters by this journalist
    newsletters = Newsletter.objects.filter(journalist=journalist).order_by(
        "-created_at"
    )

    # Organize articles by status for the template
    pending_articles = articles.filter(status="pending")
    approved_articles = articles.filter(status="approved")
    rejected_articles = articles.filter(status="rejected")

    context = {
        "articles": articles,
        "pending_articles": pending_articles,
        "approved_articles": approved_articles,
        "rejected_articles": rejected_articles,
        "total_count": articles.count(),
        "pending_count": pending_articles.count(),
        "approved_count": approved_articles.count(),
        "rejected_count": rejected_articles.count(),
        # Newsletter data
        "newsletters": newsletters,
        "newsletter_count": newsletters.count(),
    }

    return render(request, "news/journalist_dashboard.html", context)


@login_required
def subscribe_to_journalist(request, journalist_id):
    """Subscribe a reader to a journalist."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can subscribe to journalists.")
        return redirect("news:article_list")

    journalist = get_object_or_404(Journalist, id=journalist_id)

    # Check if already subscribed
    subscription, created = JournalistSubscription.objects.get_or_create(
        reader=request.user,
        journalist=journalist,
        defaults={"is_active": True},
    )

    if created:
        messages.success(
            request,
            "Successfully subscribed to "
            f"{journalist.user.get_full_name() or journalist.user.username}!",
        )
    elif not subscription.is_active:
        subscription.is_active = True
        subscription.save()
        messages.success(
            request,
            "Re-subscribed to "
            f"{journalist.user.get_full_name() or journalist.user.username}!",
        )
    else:
        messages.info(
            request, "You are already subscribed to this journalist."
        )

    return redirect(request.META.get("HTTP_REFERER", "news:article_list"))


@login_required
def unsubscribe_from_journalist(request, journalist_id):
    """Unsubscribe a reader from a journalist."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can manage subscriptions.")
        return redirect("news:article_list")

    journalist = get_object_or_404(Journalist, id=journalist_id)

    try:
        subscription = JournalistSubscription.objects.get(
            reader=request.user, journalist=journalist, is_active=True
        )
        subscription.is_active = False
        subscription.save()
        messages.success(
            request,
            f"Successfully unsubscribed from "
            f"{journalist.user.get_full_name() or journalist.user.username}.",
        )
    except JournalistSubscription.DoesNotExist:
        messages.info(request, "You are not subscribed to this journalist.")

    return redirect(request.META.get("HTTP_REFERER", "news:article_list"))


@login_required
def subscribe_to_publisher(request, publisher_id):
    """Subscribe a reader to a publisher."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can subscribe to publishers.")
        return redirect("news:article_list")

    publisher = get_object_or_404(Publisher, id=publisher_id)

    # Check if already subscribed
    subscription, created = PublisherSubscription.objects.get_or_create(
        reader=request.user, publisher=publisher, defaults={"is_active": True}
    )

    if created:
        messages.success(
            request, f"Successfully subscribed to {publisher.name}!"
        )
    elif not subscription.is_active:
        subscription.is_active = True
        subscription.save()
        messages.success(request, f"Re-subscribed to {publisher.name}!")
    else:
        messages.info(request, "You are already subscribed to this publisher.")

    return redirect(request.META.get("HTTP_REFERER", "news:article_list"))


@login_required
def unsubscribe_from_publisher(request, publisher_id):
    """Unsubscribe a reader from a publisher."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can manage subscriptions.")
        return redirect("news:article_list")

    publisher = get_object_or_404(Publisher, id=publisher_id)

    try:
        subscription = PublisherSubscription.objects.get(
            reader=request.user, publisher=publisher, is_active=True
        )
        subscription.is_active = False
        subscription.save()
        messages.success(
            request, f"Successfully unsubscribed from {publisher.name}."
        )
    except PublisherSubscription.DoesNotExist:
        messages.info(request, "You are not subscribed to this publisher.")

    return redirect(request.META.get("HTTP_REFERER", "news:article_list"))


@login_required
def my_subscriptions(request):
    """Display user's subscriptions page."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can view subscriptions.")
        return redirect("news:article_list")

    journalist_subscriptions = JournalistSubscription.objects.filter(
        reader=request.user, is_active=True
    ).select_related("journalist__user", "journalist__publisher")

    publisher_subscriptions = PublisherSubscription.objects.filter(
        reader=request.user, is_active=True
    ).select_related("publisher")

    # Get recent articles from subscribed journalists and publishers
    subscribed_journalist_ids = journalist_subscriptions.values_list(
        "journalist_id", flat=True
    )
    subscribed_publisher_ids = publisher_subscriptions.values_list(
        "publisher_id", flat=True
    )

    recent_articles = (
        Article.objects.filter(status="approved")
        .filter(
            models.Q(journalist_id__in=subscribed_journalist_ids)
            | models.Q(publisher_id__in=subscribed_publisher_ids)
        )
        .select_related("journalist__user", "publisher")
        .order_by("-created_at")[:10]
    )

    context = {
        "journalist_subscriptions": journalist_subscriptions,
        "publisher_subscriptions": publisher_subscriptions,
        "recent_articles": recent_articles,
        "total_subscriptions": journalist_subscriptions.count()
        + publisher_subscriptions.count(),
    }

    return render(request, "news/my_subscriptions.html", context)


@login_required
def browse_journalists(request):
    """Browse available journalists to subscribe to."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can browse journalists.")
        return redirect("news:article_list")

    # Get all journalists with their counts
    journalists = (
        Journalist.objects.select_related("user", "publisher")
        .annotate(
            article_count=models.Count(
                "articles",
                filter=models.Q(articles__status="approved"),
                distinct=True,
            )
        )
        .order_by("-article_count")
    )

    # Add subscriber counts separately to avoid JOIN issues
    for journalist in journalists:
        journalist.subscriber_count = JournalistSubscription.objects.filter(
            journalist=journalist, is_active=True
        ).count()

    # Get user's current subscriptions
    user_subscribed_journalists = set(
        JournalistSubscription.objects.filter(
            reader=request.user, is_active=True
        ).values_list("journalist_id", flat=True)
    )

    context = {
        "journalists": journalists,
        "user_subscribed_journalists": user_subscribed_journalists,
    }

    return render(request, "news/browse_journalists.html", context)


@login_required
def browse_publishers(request):
    """Browse available publishers to subscribe to."""
    if request.user.role != "reader":
        messages.error(request, "Only readers can browse publishers.")
        return redirect("news:article_list")

    # Get all publishers with their counts
    publishers = Publisher.objects.annotate(
        article_count=models.Count(
            "articles",
            filter=models.Q(articles__status="approved"),
            distinct=True,
        )
    ).order_by("-article_count")

    # Add subscriber counts separately to avoid JOIN issues
    for publisher in publishers:
        publisher.subscriber_count = PublisherSubscription.objects.filter(
            publisher=publisher, is_active=True
        ).count()

    # Get user's current subscriptions
    user_subscribed_publishers = set(
        PublisherSubscription.objects.filter(
            reader=request.user, is_active=True
        ).values_list("publisher_id", flat=True)
    )

    context = {
        "publishers": publishers,
        "user_subscribed_publishers": user_subscribed_publishers,
    }

    return render(request, "news/browse_publishers.html", context)


# Newsletter Views
@login_required
def newsletter_list(request):
    """Display all newsletters."""
    newsletters = (
        Newsletter.objects.all()
        .select_related("journalist__user", "publisher")
        .order_by("-created_at")
    )
    return render(
        request, "news/newsletter_list.html", {"newsletters": newsletters}
    )


def newsletter_detail(request, pk):
    """Display a single newsletter."""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    context = {"newsletter": newsletter}

    # Add subscription status for readers
    if request.user.is_authenticated and request.user.role == "reader":
        context["is_subscribed_to_journalist"] = (
            JournalistSubscription.objects.filter(
                reader=request.user,
                journalist=newsletter.journalist,
                is_active=True,
            ).exists()
        )
        context["is_subscribed_to_publisher"] = (
            PublisherSubscription.objects.filter(
                reader=request.user,
                publisher=newsletter.publisher,
                is_active=True,
            ).exists()
        )

    # Check if user can edit/delete this newsletter
    can_edit = False
    if request.user.is_authenticated:
        # Journalists can edit their own newsletters
        if (
            request.user.role == "journalist"
            and newsletter.journalist == request.user.journalist_profile
        ):
            can_edit = True
        # Editors can edit newsletters from their publisher
        elif (
            request.user.role == "editor"
            and newsletter.publisher == request.user.editor_profile.publisher
        ):
            can_edit = True

    context["can_edit"] = can_edit

    return render(request, "news/newsletter_detail.html", context)


@login_required
def create_newsletter(request):
    """Create a new newsletter (journalists only)."""
    if request.user.role != "journalist":
        messages.warning(request, "Only journalists can create newsletters.")
        return redirect("news:newsletter_list")

    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.journalist = request.user.journalist_profile
            newsletter.publisher = request.user.journalist_profile.publisher
            newsletter.save()

            # Send email notifications
            send_newsletter_confirmation_email(newsletter)
            send_newsletter_notifications(newsletter)

            messages.success(
                request,
                "Newsletter created successfully! "
                "Email notifications have been sent to your subscribers.",
            )
            return redirect("news:newsletter_detail", pk=newsletter.pk)
    else:
        form = NewsletterForm()

    return render(request, "news/create_newsletter.html", {"form": form})


@login_required
def update_newsletter(request, pk):
    """Update a newsletter (journalists can edit their own,
    editors can edit newsletters from their publisher)."""
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Permission checks
    if request.user.role == "journalist":
        if newsletter.journalist != request.user.journalist_profile:
            messages.error(request, "You can only edit your own newsletters.")
            return redirect("news:newsletter_detail", pk=pk)
    elif request.user.role == "editor":
        if newsletter.publisher != request.user.editor_profile.publisher:
            messages.error(
                request, "You can only edit newsletters from your publisher."
            )
            return redirect("news:newsletter_detail", pk=pk)
    else:
        messages.error(
            request, "You don't have permission to edit newsletters."
        )
        return redirect("news:newsletter_detail", pk=pk)

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            updated_newsletter = form.save()
            messages.success(
                request,
                f"Newsletter '{updated_newsletter.title}' updated "
                "successfully!",
            )
            return redirect("news:newsletter_detail", pk=pk)
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "news/update_newsletter.html",
        {"form": form, "newsletter": newsletter},
    )


@login_required
def delete_newsletter(request, pk):
    """
    Delete a newsletter (journalists can delete their own,
    editors can delete newsletters from their publisher).
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Permission checks
    if request.user.role == "journalist":
        if newsletter.journalist != request.user.journalist_profile:
            messages.error(
                request, "You can only delete your own newsletters."
            )
            return redirect("news:newsletter_detail", pk=pk)
    elif request.user.role == "editor":
        if newsletter.publisher != request.user.editor_profile.publisher:
            messages.error(
                request, "You can only delete newsletters from your publisher."
            )
            return redirect("news:newsletter_detail", pk=pk)
    else:
        messages.error(
            request, "You don't have permission to delete newsletters."
        )
        return redirect("news:newsletter_detail", pk=pk)

    if request.method == "POST":
        newsletter_title = newsletter.title
        newsletter.delete()
        messages.success(
            request, f"Newsletter '{newsletter_title}' deleted successfully!"
        )
        return redirect("news:newsletter_list")

    return render(
        request, "news/delete_newsletter.html", {"newsletter": newsletter}
    )


@login_required
def publisher_dashboard(request):
    """Publisher dashboard showing editors, journalists,
    and subscriber stats."""
    if request.user.role != "publisher":
        messages.warning(request, "You do not have access to this page.")
        return redirect("news:article_list")

    publisher = request.user.publisher_profile

    # Get all editors assigned to this publisher
    editors = Editor.objects.filter(publisher=publisher).select_related("user")

    # Get all journalists assigned to this publisher with
    # article/newsletter counts
    journalists = (
        Journalist.objects.filter(publisher=publisher)
        .select_related("user")
        .annotate(
            article_count=models.Count("articles", distinct=True),
            newsletter_count=models.Count("newsletters", distinct=True),
            pending_article_count=models.Count(
                "articles",
                filter=models.Q(articles__status="pending"),
                distinct=True,
            ),
            approved_article_count=models.Count(
                "articles",
                filter=models.Q(articles__status="approved"),
                distinct=True,
            ),
            rejected_article_count=models.Count(
                "articles",
                filter=models.Q(articles__status="rejected"),
                distinct=True,
            ),
        )
    )

    # Add subscriber counts separately
    for journalist in journalists:
        journalist.subscriber_count = JournalistSubscription.objects.filter(
            journalist=journalist, is_active=True
        ).count()

    # Get publisher subscriber count
    publisher_subscriber_count = PublisherSubscription.objects.filter(
        publisher=publisher, is_active=True
    ).count()

    # Get total article stats for this publisher
    total_articles = Article.objects.filter(publisher=publisher)
    total_newsletters = Newsletter.objects.filter(publisher=publisher)

    # Organize article statistics
    total_pending_articles = total_articles.filter(status="pending").count()
    total_approved_articles = total_articles.filter(status="approved").count()
    total_rejected_articles = total_articles.filter(status="rejected").count()

    context = {
        "publisher": publisher,
        "editors": editors,
        "journalists": journalists,
        "publisher_subscriber_count": publisher_subscriber_count,
        "total_articles_count": total_articles.count(),
        "total_newsletters_count": total_newsletters.count(),
        "total_pending_articles": total_pending_articles,
        "total_approved_articles": total_approved_articles,
        "total_rejected_articles": total_rejected_articles,
        "editors_count": editors.count(),
        "journalists_count": journalists.count(),
    }

    return render(request, "news/publisher_dashboard.html", context)


@staff_member_required
def admin_dashboard(request):
    """
    Admin dashboard for managing role applications.
    Only accessible to staff members/superusers.
    """
    # Get all role applications organized by status
    applications = RoleApplication.objects.all().order_by(
        "status", "-submitted_at"
    )

    # Organize applications by status for the template
    pending_applications = applications.filter(status="pending")
    approved_applications = applications.filter(status="approved")
    rejected_applications = applications.filter(status="rejected")

    # Get available publishers for assignment
    publishers = Publisher.objects.all()

    context = {
        "applications": applications,
        "pending_applications": pending_applications,
        "approved_applications": approved_applications,
        "rejected_applications": rejected_applications,
        "total_count": applications.count(),
        "pending_count": pending_applications.count(),
        "approved_count": approved_applications.count(),
        "rejected_count": rejected_applications.count(),
        "publishers": publishers,
    }

    return render(request, "news/admin_dashboard.html", context)


@staff_member_required
def approve_role_application(request, pk):
    """
    Approve a role application and update user role.
    """
    application = get_object_or_404(RoleApplication, pk=pk)

    if request.method == "POST":
        # Get publisher assignment if applicable
        publisher_id = request.POST.get("publisher")
        publisher = None
        if publisher_id:
            publisher = get_object_or_404(Publisher, pk=publisher_id)

        # Approve the application
        application.status = "approved"
        application.save()

        user = application.user

        # Update user role
        user.role = application.applied_role
        user.save()

        # Deactivate user subscriptions since they're no longer a reader
        JournalistSubscription.objects.filter(
            reader=user, is_active=True
        ).update(is_active=False)
        PublisherSubscription.objects.filter(
            reader=user, is_active=True
        ).update(is_active=False)

        # Create role-specific profiles
        if application.applied_role == "editor" and publisher:
            Editor.objects.get_or_create(user=user, publisher=publisher)
        elif application.applied_role == "journalist" and publisher:
            Journalist.objects.get_or_create(user=user, publisher=publisher)
        elif application.applied_role == "publisher":
            Publisher.objects.get_or_create(
                user=user, name=f"{user.username} Publishing"
            )

        # Send approval email
        email = EmailBuilder.build_role_approved_email(
            user, application.applied_role
        )
        email.send()

        messages.success(
            request,
            f"{application.applied_role} application for {user.username} "
            "has been approved!",
        )

    return redirect("news:admin_dashboard")


@staff_member_required
def reject_role_application(request, pk):
    """
    Reject a role application.
    """
    application = get_object_or_404(RoleApplication, pk=pk)

    application.status = "rejected"
    application.save()

    # Send rejection email
    email = EmailBuilder.build_role_rejected_email(
        application.user, application.applied_role
    )
    email.send()

    messages.info(
        request,
        f"{application.applied_role} application for "
        f"{application.user.username} has been rejected.",
    )

    return redirect("news:admin_dashboard")
