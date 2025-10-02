from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import models
from ..models import (
    Article,
    Newsletter,
    Publisher,
    Journalist,
    JournalistSubscription,
    PublisherSubscription,
)
from .serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    NewsletterSerializer,
    NewsletterListSerializer,
    NewsletterCreateSerializer,
    PublisherMinimalSerializer,
    JournalistMinimalSerializer,
)
from .permissions import IsJournalistOrPublisher


class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving and creating articles.
    - GET: articles based on user subscriptions (only approved articles)
    - POST: create new articles (journalists only)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter articles based on user's subscriptions.
        Only return approved articles from subscribed publishers/journalists.
        """
        user = self.request.user

        # Only readers should have subscriptions, but let's be flexible
        if user.role == "reader":
            # Get user's active subscriptions
            subscribed_journalist_ids = JournalistSubscription.objects.filter(
                reader=user, is_active=True
            ).values_list("journalist_id", flat=True)

            subscribed_publisher_ids = PublisherSubscription.objects.filter(
                reader=user, is_active=True
            ).values_list("publisher_id", flat=True)

            # Return articles from subscribed journalists or publishers
            return (
                Article.objects.filter(status="approved")
                .filter(
                    models.Q(journalist_id__in=subscribed_journalist_ids)
                    | models.Q(publisher_id__in=subscribed_publisher_ids)
                )
                .select_related("journalist__user", "publisher")
                .order_by("-created_at")
            )

        else:
            # For non-readers, return all approved articles
            return (
                Article.objects.filter(status="approved")
                .select_related("journalist__user", "publisher")
                .order_by("-created_at")
            )

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == "create":
            return ArticleCreateSerializer
        elif self.action == "list":
            return ArticleListSerializer
        return ArticleSerializer

    def get_permissions(self):
        """Different permissions for different actions."""
        if self.action == "create":
            # Only journalists can create articles
            permission_classes = [IsJournalistOrPublisher]
        else:
            # Read operations require authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Create a new article."""
        # Ensure user is a journalist
        if not hasattr(request.user, "journalist_profile"):
            return Response(
                {"error": "Only journalists can create articles"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get journalist and publisher from user
        journalist = request.user.journalist_profile
        publisher = journalist.publisher

        # Create the article
        article = serializer.save(
            journalist=journalist,
            publisher=publisher,
            status="pending",  # Articles need editor approval
        )

        # Return the created article with full details
        response_serializer = ArticleSerializer(article)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=["get"])
    def by_journalist(self, request):
        """Get articles by specific journalist user is subscribed to."""
        journalist_id = request.query_params.get("journalist_id")
        if not journalist_id:
            return Response(
                {"error": "journalist_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if user.role == "reader":
            # Check if user is subscribed to this journalist
            is_subscribed = JournalistSubscription.objects.filter(
                reader=user, journalist_id=journalist_id, is_active=True
            ).exists()

            if not is_subscribed:
                return Response(
                    {"error": "You are not subscribed to this journalist"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        articles = (
            Article.objects.filter(
                journalist_id=journalist_id, status="approved"
            )
            .select_related("journalist__user", "publisher")
            .order_by("-created_at")
        )

        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def by_publisher(self, request):
        """Get articles by specific publisher user is subscribed to."""
        publisher_id = request.query_params.get("publisher_id")
        if not publisher_id:
            return Response(
                {"error": "publisher_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        if user.role == "reader":
            # Check if user is subscribed to this publisher
            is_subscribed = PublisherSubscription.objects.filter(
                reader=user, publisher_id=publisher_id, is_active=True
            ).exists()

            if not is_subscribed:
                return Response(
                    {"error": "You are not subscribed to this publisher"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        articles = (
            Article.objects.filter(
                publisher_id=publisher_id, status="approved"
            )
            .select_related("journalist__user", "publisher")
            .order_by("-created_at")
        )

        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)


class NewsletterViewSet(viewsets.ModelViewSet):
    """
    ViewSet for retrieving and creating newsletters.
    - GET: newsletters based on user subscriptions
    - POST: create new newsletters (journalists only)
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter newsletters based on user's subscriptions.
        """
        user = self.request.user

        if user.role == "reader":
            # Get user's active subscriptions
            subscribed_journalist_ids = JournalistSubscription.objects.filter(
                reader=user, is_active=True
            ).values_list("journalist_id", flat=True)

            subscribed_publisher_ids = PublisherSubscription.objects.filter(
                reader=user, is_active=True
            ).values_list("publisher_id", flat=True)

            # Return newsletters from subscribed journalists or publishers
            return (
                Newsletter.objects.filter(
                    models.Q(journalist_id__in=subscribed_journalist_ids)
                    | models.Q(publisher_id__in=subscribed_publisher_ids)
                )
                .select_related("journalist__user", "publisher")
                .order_by("-created_at")
            )

        else:
            # For non-readers, return all newsletters
            return (
                Newsletter.objects.all()
                .select_related("journalist__user", "publisher")
                .order_by("-created_at")
            )

    def get_serializer_class(self):
        """Use different serializers for different actions."""
        if self.action == "create":
            return NewsletterCreateSerializer
        elif self.action == "list":
            return NewsletterListSerializer
        return NewsletterSerializer

    def get_permissions(self):
        """Different permissions for different actions."""
        if self.action == "create":
            # Only journalists can create newsletters
            permission_classes = [IsJournalistOrPublisher]
        else:
            # Read operations require authentication
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Create a new newsletter."""
        # Ensure user is a journalist
        if not hasattr(request.user, "journalist_profile"):
            return Response(
                {"error": "Only journalists can create newsletters"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get journalist and publisher from user
        journalist = request.user.journalist_profile
        publisher = journalist.publisher

        # Create the newsletter
        newsletter = serializer.save(
            journalist=journalist, publisher=publisher
        )

        # Return the created newsletter with full details
        response_serializer = NewsletterSerializer(newsletter)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )


class PublisherViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving available publishers.
    """

    queryset = Publisher.objects.all()
    serializer_class = PublisherMinimalSerializer
    permission_classes = [permissions.IsAuthenticated]


class JournalistViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving available journalists.
    """

    queryset = Journalist.objects.select_related("user", "publisher")
    serializer_class = JournalistMinimalSerializer
    permission_classes = [permissions.IsAuthenticated]
