#!/usr/bin/env python3
"""
Simple API test script for the News Application RESTful API.

This script demonstrates how to:
1. Authenticate with the API
2. Retrieve articles and newsletters
3. Test subscription-based filtering
4. Create articles and newsletters (for journalists)
5. Handle API errors

Usage:
    python test_api.py --username your_username --password your_password

    # To test POST functionality (requires journalist role):
    python test_api.py --username journalist_user --password password \
        --test-create
"""

import requests
import argparse


class NewsAPIClient:
    def __init__(self, base_url="http://127.0.0.1:8000/api/v1", token=None):
        self.base_url = base_url
        self.token = token
        self.headers = {"Authorization": f"Token {token}"} if token else {}

    def authenticate(self, username, password):
        """Get authentication token."""
        print(f"🔐 Authenticating user: {username}")

        try:
            response = requests.post(
                f"{self.base_url}/auth/token/",
                json={"username": username, "password": password},
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data["token"]
                self.headers = {"Authorization": f"Token {self.token}"}
                print(
                    f"✅ Authentication successful! "
                    f"Token: {self.token[:20]}..."
                )
                return True
            else:
                print(
                    f"❌ Authentication failed: {response.status_code} - "
                    f"{response.text}"
                )
                return False

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error during authentication: {e}")
            return False

    def get_api_documentation(self):
        """Get API documentation."""
        print("Fetching API documentation...")

        try:
            response = requests.get(
                f"{self.base_url}/docs/", headers=self.headers
            )

            if response.status_code == 200:
                docs = response.json()
                print(f"API Version: {docs.get('api_version')}")
                print(f"Description: {docs.get('description')}")
                return docs
            else:
                print(f"Failed to get documentation: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching documentation: {e}")
            return None

    def get_articles(self, page=1):
        """Get articles based on user subscriptions."""
        print(f"📰 Fetching articles (page {page})...")

        try:
            response = requests.get(
                f"{self.base_url}/articles/",
                headers=self.headers,
                params={"page": page},
            )

            if response.status_code == 200:
                data = response.json()
                articles = data.get("results", [])
                print(
                    f"✅ Found {len(articles)} articles "
                    f"(Total: {data.get('count', 0)})"
                )

                for article in articles[:3]:  # Show first 3
                    print(
                        f"   📄 {article.get('title')} - "
                        f"by {article.get('journalist_name')}"
                    )

                return data
            else:
                print(
                    f"❌ Failed to get articles: {response.status_code} - "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching articles: {e}")
            return None

    def get_newsletters(self, page=1):
        """Get newsletters based on user subscriptions."""
        print(f"📬 Fetching newsletters (page {page})...")

        try:
            response = requests.get(
                f"{self.base_url}/newsletters/",
                headers=self.headers,
                params={"page": page},
            )

            if response.status_code == 200:
                data = response.json()
                newsletters = data.get("results", [])
                print(
                    f"✅ Found {len(newsletters)} newsletters "
                    f"(Total: {data.get('count', 0)})"
                )

                for newsletter in newsletters[:3]:  # Show first 3
                    print(
                        f"   📧 {newsletter.get('title')} - "
                        f"by {newsletter.get('journalist_name')}"
                    )

                return data
            else:
                print(
                    f"❌ Failed to get newsletters: {response.status_code} - "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching newsletters: {e}")
            return None

    def get_publishers(self):
        """Get list of publishers."""
        print("🏢 Fetching publishers...")

        try:
            response = requests.get(
                f"{self.base_url}/publishers/", headers=self.headers
            )

            if response.status_code == 200:
                data = response.json()
                publishers = data.get("results", [])
                print(f"✅ Found {len(publishers)} publishers")

                for publisher in publishers:
                    print(
                        f"   🏢 {publisher.get('name')} "
                        f"(ID: {publisher.get('id')})"
                    )

                return data
            else:
                print(
                    f"❌ Failed to get publishers: {response.status_code} - "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching publishers: {e}")
            return None

    def get_journalists(self):
        """Get list of journalists."""
        print("👥 Fetching journalists...")

        try:
            response = requests.get(
                f"{self.base_url}/journalists/", headers=self.headers
            )

            if response.status_code == 200:
                data = response.json()
                journalists = data.get("results", [])
                print(f"✅ Found {len(journalists)} journalists")

                for journalist in journalists:
                    name = journalist.get("name") or journalist.get(
                        "username", "Unknown"
                    )
                    print(
                        f"   👤 {name} at {journalist.get('publisher_name')} "
                        f"(ID: {journalist.get('id')})"
                    )

                return data
            else:
                print(
                    f"❌ Failed to get journalists: {response.status_code} - "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching journalists: {e}")
            return None

    def test_journalist_filter(self, journalist_id):
        """Test filtering articles by specific journalist."""
        print(f"🔍 Testing articles by journalist ID: {journalist_id}")

        try:
            response = requests.get(
                f"{self.base_url}/articles/by_journalist/",
                headers=self.headers,
                params={"journalist_id": journalist_id},
            )

            if response.status_code == 200:
                articles = response.json()
                print(f"✅ Found {len(articles)} articles by this journalist")
                return articles
            elif response.status_code == 403:
                print(
                    "⚠️  Access forbidden - you may not be subscribed "
                    "to this journalist"
                )
                return None
            else:
                print(
                    f"❌ Failed to get articles by journalist: "
                    f"{response.status_code} - {response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching articles by journalist: {e}")
            return None

    def create_article(self, title, content):
        """Create a new article (for journalists)."""
        print(f"📝 Creating new article: {title[:30]}...")

        article_data = {
            "title": title,
            "content": content,
        }

        try:
            response = requests.post(
                f"{self.base_url}/articles/",
                headers=self.headers,
                json=article_data,
            )

            if response.status_code == 201:
                article = response.json()
                print(
                    f"✅ Article created successfully! "
                    f"ID: {article.get('id')}"
                )
                print(f"   📄 Title: {article.get('title')}")
                journalist = article.get("journalist", {})
                if journalist:
                    author_name = journalist.get("name") or journalist.get(
                        "username", "Unknown"
                    )
                    print(f"   👤 Author: {author_name}")
                publisher = article.get("publisher", {})
                if publisher:
                    print(f"   🏢 Publisher: {publisher.get('name')}")
                print(f"   📅 Created: {article.get('created_at')}")
                return article
            elif response.status_code == 400:
                print(
                    f"❌ Invalid article data: {response.status_code} - "
                    f"{response.text}"
                )
                return None
            elif response.status_code == 403:
                print(
                    "❌ Permission denied - you may not have journalist "
                    "permissions or are not authenticated"
                )
                return None
            else:
                print(
                    f"❌ Failed to create article: {response.status_code} - "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating article: {e}")
            return None

    def create_newsletter(self, title, content):
        """Create a new newsletter (for journalists)."""
        print(f"📰 Creating new newsletter: {title[:30]}...")

        newsletter_data = {
            "title": title,
            "content": content,
        }

        try:
            response = requests.post(
                f"{self.base_url}/newsletters/",
                headers=self.headers,
                json=newsletter_data,
            )

            if response.status_code == 201:
                newsletter = response.json()
                print(
                    f"✅ Newsletter created successfully! "
                    f"ID: {newsletter.get('id')}"
                )
                print(f"   📧 Title: {newsletter.get('title')}")
                journalist = newsletter.get("journalist", {})
                if journalist:
                    author_name = journalist.get("name") or journalist.get(
                        "username", "Unknown"
                    )
                    print(f"   👤 Author: {author_name}")
                publisher = newsletter.get("publisher", {})
                if publisher:
                    print(f"   🏢 Publisher: {publisher.get('name')}")
                print(f"   📅 Created: {newsletter.get('created_at')}")
                return newsletter
            elif response.status_code == 400:
                print(
                    f"❌ Invalid newsletter data: {response.status_code} - "
                    f"{response.text}"
                )
                return None
            elif response.status_code == 403:
                print(
                    "❌ Permission denied - you may not have journalist "
                    "permissions or are not authenticated"
                )
                return None
            else:
                print(
                    f"❌ Failed to create newsletter: {response.status_code} - "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating newsletter: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(
        description="Test the News Application API"
    )
    parser.add_argument(
        "--username", required=True, help="Username for authentication"
    )
    parser.add_argument(
        "--password", required=True, help="Password for authentication"
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000/api/v1",
        help="Base API URL",
    )
    parser.add_argument(
        "--test-create",
        action="store_true",
        help="Test creating articles and newsletters "
             "(requires journalist role)",
    )

    args = parser.parse_args()

    print("🚀 Starting News API Test")
    print("=" * 50)

    # Initialize client
    client = NewsAPIClient(base_url=args.base_url)

    # Authenticate
    if not client.authenticate(args.username, args.password):
        print("❌ Cannot proceed without authentication")
        return

    print("\n" + "=" * 50)

    # Get API documentation
    client.get_api_documentation()

    print("\n" + "=" * 50)

    # Get publishers
    client.get_publishers()

    print("\n" + "=" * 50)

    # Get journalists
    journalists = client.get_journalists()

    print("\n" + "=" * 50)

    # Get articles
    client.get_articles()

    print("\n" + "=" * 50)

    # Get newsletters
    client.get_newsletters()

    print("\n" + "=" * 50)

    # Test journalist filtering (if we have journalists)
    if journalists and journalists.get("results"):
        first_journalist = journalists["results"][0]
        journalist_id = first_journalist.get("id")
        if journalist_id:
            client.test_journalist_filter(journalist_id)

    # Test POST functionality if requested
    if args.test_create:
        print("\n" + "=" * 50)
        print("📝 Testing POST functionality (create article & newsletter)")

        # Test creating an article
        article_title = "Test Article from API Client"
        article_content = (
            "This is a test article created via the API to demonstrate "
            "the POST functionality for journalists. It should be "
            "created with pending status and require editor approval."
        )

        created_article = client.create_article(article_title, article_content)

        print("\n" + "-" * 30)

        # Test creating a newsletter
        newsletter_title = "Test Newsletter from API Client"
        newsletter_content = (
            "This is a test newsletter created via the API to demonstrate "
            "the POST functionality for journalists. Newsletters do not "
            "require editor approval and are immediately available."
        )

        created_newsletter = client.create_newsletter(
            newsletter_title, newsletter_content
        )

        if created_article or created_newsletter:
            print(
                "\n✅ POST functionality test completed! "
                "Check the results above."
            )
        else:
            print(
                "\n⚠️  POST functionality test completed with issues. "
                "Make sure you're authenticated as a journalist."
            )

    print("\nAPI test completed!")


if __name__ == "__main__":
    main()
