from rest_framework import serializers
from ..models import Article, Newsletter, Publisher, Journalist


class PublisherMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Publisher model."""

    class Meta:
        model = Publisher
        fields = ["id", "name"]


class JournalistMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for Journalist model."""

    name = serializers.CharField(source="user.get_full_name", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True
    )

    class Meta:
        model = Journalist
        fields = ["id", "name", "username", "publisher_name"]


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for Article model with minimal related data."""

    journalist = JournalistMinimalSerializer(read_only=True)
    publisher = PublisherMinimalSerializer(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "journalist",
            "publisher",
            "created_at",
            "updated_at",
        ]


class ArticleListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for article listings."""

    journalist_name = serializers.CharField(
        source="journalist.user.get_full_name", read_only=True
    )
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True
    )

    class Meta:
        model = Article
        fields = [
            "id",
            "title",
            "journalist_name",
            "publisher_name",
            "created_at",
        ]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model with minimal related data."""

    journalist = JournalistMinimalSerializer(read_only=True)
    publisher = PublisherMinimalSerializer(read_only=True)

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "content",
            "journalist",
            "publisher",
            "created_at",
            "updated_at",
        ]


class NewsletterListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for newsletter listings."""

    journalist_name = serializers.CharField(
        source="journalist.user.get_full_name", read_only=True
    )
    publisher_name = serializers.CharField(
        source="publisher.name", read_only=True
    )

    class Meta:
        model = Newsletter
        fields = [
            "id",
            "title",
            "journalist_name",
            "publisher_name",
            "created_at",
        ]


class ArticleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new articles."""

    class Meta:
        model = Article
        fields = ["title", "content"]

    def validate_title(self, value):
        """Ensure title is not empty and has reasonable length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value.strip()) > 255:
            raise serializers.ValidationError(
                "Title cannot exceed 255 characters."
            )
        return value.strip()

    def validate_content(self, value):
        """Ensure content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()


class NewsletterCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new newsletters."""

    class Meta:
        model = Newsletter
        fields = ["title", "content"]

    def validate_title(self, value):
        """Ensure title is not empty and has reasonable length."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value.strip()) > 255:
            raise serializers.ValidationError(
                "Title cannot exceed 255 characters."
            )
        return value.strip()

    def validate_content(self, value):
        """Ensure content is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Content cannot be empty.")
        return value.strip()
