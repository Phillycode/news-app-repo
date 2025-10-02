from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .documentation import api_documentation

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"articles", views.ArticleViewSet, basename="article")
router.register(r"newsletters", views.NewsletterViewSet, basename="newsletter")
router.register(r"publishers", views.PublisherViewSet, basename="publisher")
router.register(r"journalists", views.JournalistViewSet, basename="journalist")

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("v1/", include(router.urls)),
    path("v1/auth/token/", obtain_auth_token, name="api_token_auth"),
    path(
        "v1/auth/", include("rest_framework.urls", namespace="rest_framework")
    ),
    path("v1/docs/", api_documentation, name="api_documentation"),
]
