from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def api_documentation(request):
    """
    API Documentation endpoint that returns available
    API endpoints and their usage.
    """
    documentation = {
        "api_version": "v1",
        "description": (
            "RESTful API for retrieving articles and newsletters "
            "based on user subscriptions"
        ),
        "authentication": {
            "type": "Token Authentication",
            "header": "Authorization: Token <your-token>",
            "obtain_token": (
                "/api/v1/auth/token/ (POST with username/password)"
            ),
        },
        "endpoints": {
            "articles": {
                "list": {
                    "url": "/api/v1/articles/",
                    "method": "GET",
                    "description": (
                        "Get articles from subscribed publishers/journalists"
                    ),
                    "permissions": "Authenticated users only",
                },
                "detail": {
                    "url": "/api/v1/articles/{id}/",
                    "method": "GET",
                    "description": "Get specific article details",
                    "permissions": "Authenticated users only",
                },
                "by_journalist": {
                    "url": (
                        "/api/v1/articles/by_journalist/?journalist_id={id}"
                    ),
                    "method": "GET",
                    "description": (
                        "Get articles by specific journalist "
                        "(subscription required for readers)"
                    ),
                    "permissions": "Authenticated users only",
                },
                "by_publisher": {
                    "url": "/api/v1/articles/by_publisher/?publisher_id={id}",
                    "method": "GET",
                    "description": (
                        "Get articles by specific publisher "
                        "(subscription required for readers)"
                    ),
                    "permissions": "Authenticated users only",
                },
            },
            "newsletters": {
                "list": {
                    "url": "/api/v1/newsletters/",
                    "method": "GET",
                    "description": (
                        "Get newsletters from subscribed "
                        "publishers/journalists"
                    ),
                    "permissions": "Authenticated users only",
                },
                "detail": {
                    "url": "/api/v1/newsletters/{id}/",
                    "method": "GET",
                    "description": "Get specific newsletter details",
                    "permissions": "Authenticated users only",
                },
            },
            "publishers": {
                "list": {
                    "url": "/api/v1/publishers/",
                    "method": "GET",
                    "description": "Get list of all publishers",
                    "permissions": "Authenticated users only",
                },
                "detail": {
                    "url": "/api/v1/publishers/{id}/",
                    "method": "GET",
                    "description": "Get specific publisher details",
                    "permissions": "Authenticated users only",
                },
            },
            "journalists": {
                "list": {
                    "url": "/api/v1/journalists/",
                    "method": "GET",
                    "description": "Get list of all journalists",
                    "permissions": "Authenticated users only",
                },
                "detail": {
                    "url": "/api/v1/journalists/{id}/",
                    "method": "GET",
                    "description": "Get specific journalist details",
                    "permissions": "Authenticated users only",
                },
            },
        },
        "filtering_logic": {
            "readers": (
                "Only see articles/newsletters from subscribed "
                "publishers/journalists"
            ),
            "journalists_editors_publishers": (
                "See all approved articles/newsletters"
            ),
        },
        "pagination": {"page_size": 20, "parameters": "?page=<page_number>"},
        "example_requests": {
            "get_token": {
                "url": "/api/v1/auth/token/",
                "method": "POST",
                "body": {
                    "username": "your_username",
                    "password": "your_password",
                },
            },
            "get_articles": {
                "url": "/api/v1/articles/",
                "method": "GET",
                "headers": {"Authorization": "Token your-token-here"},
            },
        },
    }

    return Response(documentation)
