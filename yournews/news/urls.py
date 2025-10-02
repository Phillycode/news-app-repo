from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    # 'Home' page as article_list
    path("", views.article_list, name="article_list"),
    # Authentication
    path("login/", views.login_user, name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("register/", views.register, name="register"),
    # Password reset
    path(
        "forgot_password/",
        views.forgot_password,
        name="forgot_password",
    ),
    path(
        "reset_password/<str:token>/",
        views.reset_password,
        name="reset_password",
    ),
    # Role Applications
    path("apply-role/", views.apply_for_role, name="apply_role"),
    # News-related views
    path("articles/<int:pk>/", views.article_detail, name="article_detail"),
    path(
        "articles/<int:pk>/update/",
        views.update_article,
        name="update_article",
    ),
    path(
        "articles/<int:pk>/delete/",
        views.delete_article,
        name="delete_article",
    ),
    # Professional role dashboards
    path("editor/dashboard/", views.editor_dashboard, name="editor_dashboard"),
    path(
        "journalist/dashboard/",
        views.journalist_dashboard,
        name="journalist_dashboard",
    ),
    path(
        "publisher/dashboard/",
        views.publisher_dashboard,
        name="publisher_dashboard",
    ),
    # Admin dashboard
    path("staff/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path(
        "staff/approve/<int:pk>/",
        views.approve_role_application,
        name="approve_role_application",
    ),
    path(
        "staff/reject/<int:pk>/",
        views.reject_role_application,
        name="reject_role_application",
    ),
    # Editor actions
    path(
        "editor/approve/<int:pk>/",
        views.approve_article,
        name="approve_article",
    ),
    path(
        "editor/reject/<int:pk>/", views.reject_article, name="reject_article"
    ),
    path("submit_article/", views.submit_article, name="submit_article"),
    # Newsletter views
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path(
        "newsletters/<int:pk>/",
        views.newsletter_detail,
        name="newsletter_detail",
    ),
    path(
        "newsletters/create/",
        views.create_newsletter,
        name="create_newsletter",
    ),
    path(
        "newsletters/<int:pk>/update/",
        views.update_newsletter,
        name="update_newsletter",
    ),
    path(
        "newsletters/<int:pk>/delete/",
        views.delete_newsletter,
        name="delete_newsletter",
    ),
    # Subscription views
    path("subscriptions/", views.my_subscriptions, name="my_subscriptions"),
    path(
        "browse/journalists/",
        views.browse_journalists,
        name="browse_journalists",
    ),
    path(
        "browse/publishers/", views.browse_publishers, name="browse_publishers"
    ),
    path(
        "subscribe/journalist/<int:journalist_id>/",
        views.subscribe_to_journalist,
        name="subscribe_journalist",
    ),
    path(
        "unsubscribe/journalist/<int:journalist_id>/",
        views.unsubscribe_from_journalist,
        name="unsubscribe_journalist",
    ),
    path(
        "subscribe/publisher/<int:publisher_id>/",
        views.subscribe_to_publisher,
        name="subscribe_publisher",
    ),
    path(
        "unsubscribe/publisher/<int:publisher_id>/",
        views.unsubscribe_from_publisher,
        name="unsubscribe_publisher",
    ),
]
