from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import (
    Publisher,
    Editor,
    Journalist,
    Article,
    Newsletter,
    JournalistSubscription,
    PublisherSubscription,
)

User = get_user_model()


class APITestSetup(APITestCase):
    """Base class for API tests with common setup and helper methods."""

    def setUp(self):
        """Create test data for all API tests."""
        # Create users with different roles
        self.reader_user = self.create_user(
            "reader", "reader@test.com", "reader"
        )
        self.journalist_user = self.create_user(
            "journalist", "journalist@test.com", "journalist"
        )
        self.editor_user = self.create_user(
            "editor", "editor@test.com", "editor"
        )
        self.publisher_user = self.create_user(
            "publisher", "publisher@test.com", "publisher"
        )

        # Create another set for testing subscriptions
        self.reader2_user = self.create_user(
            "reader2", "reader2@test.com", "reader"
        )
        self.journalist2_user = self.create_user(
            "journalist2", "journalist2@test.com", "journalist"
        )
        self.publisher2_user = self.create_user(
            "publisher2", "publisher2@test.com", "publisher"
        )

        # Create publisher profiles
        self.publisher = Publisher.objects.create(
            user=self.publisher_user,
            name="Test Publisher",
            description="A test publisher",
        )

        self.publisher2 = Publisher.objects.create(
            user=self.publisher2_user,
            name="Test Publisher 2",
            description="Another test publisher",
        )

        # Create journalist profiles
        self.journalist = Journalist.objects.create(
            user=self.journalist_user, publisher=self.publisher
        )

        self.journalist2 = Journalist.objects.create(
            user=self.journalist2_user, publisher=self.publisher2
        )

        # Create editor profile
        self.editor = Editor.objects.create(
            user=self.editor_user, publisher=self.publisher
        )

        # Create articles with different statuses
        self.approved_article = Article.objects.create(
            title="Approved Article",
            content="This is an approved article.",
            journalist=self.journalist,
            publisher=self.publisher,
            status="approved",
        )

        self.pending_article = Article.objects.create(
            title="Pending Article",
            content="This is a pending article.",
            journalist=self.journalist,
            publisher=self.publisher,
            status="pending",
        )

        self.approved_article2 = Article.objects.create(
            title="Another Approved Article",
            content="This is another approved article.",
            journalist=self.journalist2,
            publisher=self.publisher2,
            status="approved",
        )

        # Create newsletters
        self.newsletter = Newsletter.objects.create(
            title="Test Newsletter",
            content="Newsletter content",
            journalist=self.journalist,
            publisher=self.publisher,
        )

        self.newsletter2 = Newsletter.objects.create(
            title="Another Newsletter",
            content="Another newsletter content",
            journalist=self.journalist2,
            publisher=self.publisher2,
        )

        # Create tokens for authentication
        self.reader_token = Token.objects.create(user=self.reader_user)
        self.journalist_token = Token.objects.create(user=self.journalist_user)
        self.editor_token = Token.objects.create(user=self.editor_user)
        self.publisher_token = Token.objects.create(user=self.publisher_user)

    def create_user(self, username, email, role):
        """Helper method to create users with different roles."""
        user = User.objects.create_user(
            username=username, email=email, password="testpass123", role=role
        )
        return user

    def authenticate_user(self, token):
        """Helper method to authenticate a user via token."""
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def create_subscription(self, reader, journalist=None, publisher=None):
        """Helper method to create subscriptions."""
        if journalist:
            return JournalistSubscription.objects.create(
                reader=reader, journalist=journalist
            )
        elif publisher:
            return PublisherSubscription.objects.create(
                reader=reader, publisher=publisher
            )


class AuthenticationAPITest(APITestSetup):
    """Test API authentication and token management."""

    def test_token_authentication_success(self):
        """Test successful token authentication."""
        url = reverse("api_token_auth")
        data = {"username": "reader", "password": "testpass123"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_token_authentication_invalid_credentials(self):
        """Test token authentication with invalid credentials."""
        url = reverse("api_token_auth")
        data = {"username": "reader", "password": "wrongpassword"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_authenticated_access_required(self):
        """Test that API endpoints require authentication."""
        url = reverse("article-list")
        response = self.client.get(url)

        # DRF returns 403 when no authentication credentials are provided
        # for endpoints that require authentication
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )

    def test_valid_token_access(self):
        """Test API access with valid token."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_access(self):
        """Test API access with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION="Token invalidtoken123")
        url = reverse("article-list")
        response = self.client.get(url)

        # DRF may return either 401 or 403 for invalid tokens depending on
        # configuration
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class ArticleAPITest(APITestSetup):
    """Test Article API endpoints and subscription filtering."""

    def test_article_list_reader_no_subscriptions(self):
        """Test article list for reader with no subscriptions."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_article_list_reader_with_journalist_subscription(self):
        """Test article list for reader subscribed to a journalist."""
        # Create subscription
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"], self.approved_article.id
        )

    def test_article_list_reader_with_publisher_subscription(self):
        """Test article list for reader subscribed to a publisher."""
        # Create subscription
        self.create_subscription(self.reader_user, publisher=self.publisher)

        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"], self.approved_article.id
        )

    def test_article_list_non_reader_sees_all_approved(self):
        """Test that non-readers see all approved articles."""
        self.authenticate_user(self.journalist_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see both approved articles
        self.assertEqual(len(response.data["results"]), 2)
        article_ids = [article["id"] for article in response.data["results"]]
        self.assertIn(self.approved_article.id, article_ids)
        self.assertIn(self.approved_article2.id, article_ids)

    def test_article_list_only_approved_articles_shown(self):
        """Test that only approved articles are shown in list."""
        # Subscribe to journalist with both approved and pending articles
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(
            response.data["results"][0]["id"], self.approved_article.id
        )

    def test_article_detail_view(self):
        """Test article detail view."""
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse(
            "article-detail", kwargs={"pk": self.approved_article.id}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.approved_article.id)
        self.assertEqual(response.data["title"], self.approved_article.title)

    def test_article_by_journalist_authorized(self):
        """Test filtering articles by journalist for subscribed reader."""
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("article-by-journalist")
        response = self.client.get(url, {"journalist_id": self.journalist.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.approved_article.id)

    def test_article_by_journalist_unauthorized(self):
        """Test filtering articles by journalist for non-subscribed reader."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-by-journalist")
        response = self.client.get(url, {"journalist_id": self.journalist.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_by_journalist_non_reader(self):
        """Test that non-readers can access any journalist's articles."""
        self.authenticate_user(self.journalist_token)
        url = reverse("article-by-journalist")
        response = self.client.get(url, {"journalist_id": self.journalist.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_article_by_journalist_missing_parameter(self):
        """Test article by journalist endpoint without journalist_id
        parameter."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-by-journalist")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_article_by_publisher_authorized(self):
        """Test filtering articles by publisher for subscribed reader."""
        self.create_subscription(self.reader_user, publisher=self.publisher)

        self.authenticate_user(self.reader_token)
        url = reverse("article-by-publisher")
        response = self.client.get(url, {"publisher_id": self.publisher.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_article_by_publisher_unauthorized(self):
        """Test filtering articles by publisher for non-subscribed reader."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-by-publisher")
        response = self.client.get(url, {"publisher_id": self.publisher.id})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_article_by_publisher_missing_parameter(self):
        """Test article by publisher endpoint without publisher_id
        parameter."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-by-publisher")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)


class NewsletterAPITest(APITestSetup):
    """Test Newsletter API endpoints and subscription filtering."""

    def test_newsletter_list_reader_no_subscriptions(self):
        """Test newsletter list for reader with no subscriptions."""
        self.authenticate_user(self.reader_token)
        url = reverse("newsletter-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_newsletter_list_reader_with_journalist_subscription(self):
        """Test newsletter list for reader subscribed to a journalist."""
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("newsletter-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.newsletter.id)

    def test_newsletter_list_reader_with_publisher_subscription(self):
        """Test newsletter list for reader subscribed to a publisher."""
        self.create_subscription(self.reader_user, publisher=self.publisher)

        self.authenticate_user(self.reader_token)
        url = reverse("newsletter-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["id"], self.newsletter.id)

    def test_newsletter_list_non_reader_sees_all(self):
        """Test that non-readers see all newsletters."""
        self.authenticate_user(self.journalist_token)
        url = reverse("newsletter-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_newsletter_detail_view(self):
        """Test newsletter detail view."""
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("newsletter-detail", kwargs={"pk": self.newsletter.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.newsletter.id)
        self.assertEqual(response.data["title"], self.newsletter.title)


class PublisherAPITest(APITestSetup):
    """Test Publisher API endpoints."""

    def test_publisher_list_authenticated(self):
        """Test publisher list with authentication."""
        self.authenticate_user(self.reader_token)
        url = reverse("publisher-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        publisher_names = [pub["name"] for pub in response.data["results"]]
        self.assertIn("Test Publisher", publisher_names)
        self.assertIn("Test Publisher 2", publisher_names)

    def test_publisher_detail_view(self):
        """Test publisher detail view."""
        self.authenticate_user(self.reader_token)
        url = reverse("publisher-detail", kwargs={"pk": self.publisher.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.publisher.id)
        self.assertEqual(response.data["name"], "Test Publisher")

    def test_publisher_list_unauthenticated(self):
        """Test that publisher list requires authentication."""
        url = reverse("publisher-list")
        response = self.client.get(url)

        # DRF returns 403 when no authentication credentials are provided
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class JournalistAPITest(APITestSetup):
    """Test Journalist API endpoints."""

    def test_journalist_list_authenticated(self):
        """Test journalist list with authentication."""
        self.authenticate_user(self.reader_token)
        url = reverse("journalist-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        # Check that proper serializer fields are included
        first_journalist = response.data["results"][0]
        self.assertIn("id", first_journalist)
        self.assertIn("name", first_journalist)
        self.assertIn("username", first_journalist)
        self.assertIn("publisher_name", first_journalist)

    def test_journalist_detail_view(self):
        """Test journalist detail view."""
        self.authenticate_user(self.reader_token)
        url = reverse("journalist-detail", kwargs={"pk": self.journalist.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.journalist.id)
        self.assertEqual(response.data["publisher_name"], "Test Publisher")

    def test_journalist_list_unauthenticated(self):
        """Test that journalist list requires authentication."""
        url = reverse("journalist-list")
        response = self.client.get(url)

        # DRF returns 403 when no authentication credentials are provided
        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class APIErrorHandlingTest(APITestSetup):
    """Test API error handling and edge cases."""

    def test_article_detail_nonexistent(self):
        """Test accessing non-existent article."""
        self.authenticate_user(self.reader_token)
        url = reverse("article-detail", kwargs={"pk": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_newsletter_detail_nonexistent(self):
        """Test accessing non-existent newsletter."""
        self.authenticate_user(self.reader_token)
        url = reverse("newsletter-detail", kwargs={"pk": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_publisher_detail_nonexistent(self):
        """Test accessing non-existent publisher."""
        self.authenticate_user(self.reader_token)
        url = reverse("publisher-detail", kwargs={"pk": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_journalist_detail_nonexistent(self):
        """Test accessing non-existent journalist."""
        self.authenticate_user(self.reader_token)
        url = reverse("journalist-detail", kwargs={"pk": 999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_article_by_journalist_nonexistent_journalist(self):
        """Test filtering by non-existent journalist."""
        self.authenticate_user(
            self.journalist_token
        )  # Non-reader to bypass subscription check
        url = reverse("article-by-journalist")
        response = self.client.get(url, {"journalist_id": 999999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return empty list

    def test_article_by_publisher_nonexistent_publisher(self):
        """Test filtering by non-existent publisher."""
        self.authenticate_user(
            self.journalist_token
        )  # Non-reader to bypass subscription check
        url = reverse("article-by-publisher")
        response = self.client.get(url, {"publisher_id": 999999})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # Should return empty list

    def test_multiple_subscriptions(self):
        """Test reader with multiple subscriptions sees all relevant
        content."""
        # Subscribe to both journalist and publisher
        self.create_subscription(self.reader_user, journalist=self.journalist)
        self.create_subscription(self.reader_user, publisher=self.publisher2)

        self.authenticate_user(self.reader_token)

        # Test articles
        url = reverse("article-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 2
        )  # Should see articles from both sources

        # Test newsletters
        url = reverse("newsletter-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 2
        )  # Should see newsletters from both sources

    def test_inactive_subscriptions_filter_content(self):
        """Test that inactive subscriptions don't show content."""
        # Create active subscription then deactivate it
        subscription = self.create_subscription(
            self.reader_user, journalist=self.journalist
        )
        subscription.is_active = False
        subscription.save()

        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data["results"]), 0
        )  # Should not see content


class APIPaginationTest(APITestSetup):
    """Test API pagination functionality."""

    def test_article_list_pagination(self):
        """Test that article list supports pagination."""
        # Create subscription to see articles
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("article-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination fields exist
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)

    def test_newsletter_list_pagination(self):
        """Test that newsletter list supports pagination."""
        self.create_subscription(self.reader_user, journalist=self.journalist)

        self.authenticate_user(self.reader_token)
        url = reverse("newsletter-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination fields exist
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
