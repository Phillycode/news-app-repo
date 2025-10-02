# News Application RESTful API

## Overview
This RESTful API enables third-party clients to retrieve articles and newsletters for publishers and journalists based on user subscriptions.

## Features
- **Subscription-based filtering**: Readers only see content from subscribed publishers/journalists
- **Token-based authentication**: Secure API access using Django REST Framework tokens
- **Role-based permissions**: Different access levels for readers, journalists, editors, and publishers
- **Pagination**: Efficient handling of large datasets
- **Versioned endpoints**: API versioning for future compatibility

## API Endpoints

### Authentication
- **Get Token**: `POST /api/v1/auth/token/`
  - Body: `{"username": "your_username", "password": "your_password"}`
  - Returns: `{"token": "your-api-token"}`

### Articles
- **List Articles**: `GET /api/v1/articles/`
  - Returns articles based on user's subscriptions
  - Headers: `Authorization: Token <your-token>`

- **Article Detail**: `GET /api/v1/articles/{id}/`
  - Returns specific article details
  - Headers: `Authorization: Token <your-token>`

- **Articles by Journalist**: `GET /api/v1/articles/by_journalist/?journalist_id={id}`
  - Returns articles by specific journalist (subscription required for readers)
  - Headers: `Authorization: Token <your-token>`

- **Articles by Publisher**: `GET /api/v1/articles/by_publisher/?publisher_id={id}`
  - Returns articles by specific publisher (subscription required for readers)
  - Headers: `Authorization: Token <your-token>`

- **Create Article**: `POST /api/v1/articles/`
  - Creates a new article (journalists only)
  - Headers: `Authorization: Token <your-token>`
  - Body: `{"title": "Article Title", "content": "Article content..."}`
  - Returns: Created article with status "pending" (requires editor approval)

### Newsletters
- **List Newsletters**: `GET /api/v1/newsletters/`
  - Returns newsletters based on user's subscriptions
  - Headers: `Authorization: Token <your-token>`

- **Newsletter Detail**: `GET /api/v1/newsletters/{id}/`
  - Returns specific newsletter details
  - Headers: `Authorization: Token <your-token>`

- **Create Newsletter**: `POST /api/v1/newsletters/`
  - Creates a new newsletter (journalists only)
  - Headers: `Authorization: Token <your-token>`
  - Body: `{"title": "Newsletter Title", "content": "Newsletter content..."}`
  - Returns: Created newsletter (immediately available, no approval required)

### Publishers & Journalists
- **List Publishers**: `GET /api/v1/publishers/`
- **Publisher Detail**: `GET /api/v1/publishers/{id}/`
- **List Journalists**: `GET /api/v1/journalists/`
- **Journalist Detail**: `GET /api/v1/journalists/{id}/`

### Documentation
- **API Documentation**: `GET /api/v1/docs/`
  - Returns detailed API documentation
  - Headers: `Authorization: Token <your-token>`

## Getting Started

### 1. Create API Tokens
Run the following command to create API tokens for existing users:

```bash
python manage.py create_api_tokens
```

Or for a specific user:
```bash
python manage.py create_api_tokens --username your_username
```

### 2. Test the API

#### Example using curl:

1. **Get an authentication token:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your_username", "password": "your_password"}'
```

2. **Get articles using the token:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/articles/ \
     -H "Authorization: Token your-token-here"
```

3. **Get API documentation:**
```bash
curl -X GET http://127.0.0.1:8000/api/v1/docs/ \
     -H "Authorization: Token your-token-here"
```

4. **Create an article (journalists only):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/articles/ \
     -H "Authorization: Token your-token-here" \
     -H "Content-Type: application/json" \
     -d '{"title": "My New Article", "content": "This is the article content..."}'
```

5. **Create a newsletter (journalists only):**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/newsletters/ \
     -H "Authorization: Token your-token-here" \
     -H "Content-Type: application/json" \
     -d '{"title": "Weekly Newsletter", "content": "This week in news..."}'
```

#### Example using Python requests:

```python
import requests

# Base URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# Get token
auth_response = requests.post(f"{BASE_URL}/auth/token/", {
    "username": "your_username",
    "password": "your_password"
})
token = auth_response.json()["token"]

# Set headers
headers = {"Authorization": f"Token {token}"}

# Get articles
articles_response = requests.get(f"{BASE_URL}/articles/", headers=headers)
articles = articles_response.json()

print(f"Found {len(articles['results'])} articles")

# Create an article (journalists only)
article_data = {
    "title": "My New Article",
    "content": "This is the article content..."
}
create_article_response = requests.post(
    f"{BASE_URL}/articles/", 
    headers=headers, 
    json=article_data
)
if create_article_response.status_code == 201:
    new_article = create_article_response.json()
    print(f"Created article: {new_article['title']} (ID: {new_article['id']})")

# Create a newsletter (journalists only)
newsletter_data = {
    "title": "Weekly Newsletter",
    "content": "This week in news..."
}
create_newsletter_response = requests.post(
    f"{BASE_URL}/newsletters/", 
    headers=headers, 
    json=newsletter_data
)
if create_newsletter_response.status_code == 201:
    new_newsletter = create_newsletter_response.json()
    print(f"Created newsletter: {new_newsletter['title']} (ID: {new_newsletter['id']})")
```

## Testing the API

### Automated Test Suite

This project includes a comprehensive test suite with **39 automated tests** covering:
- ✅ Authentication and token management
- ✅ API endpoint functionality
- ✅ Subscription-based filtering
- ✅ Role-based permissions
- ✅ Error handling and edge cases
- ✅ Data validation and integrity

### Running Tests

#### 1. Run All API Tests
```bash
# Run all tests with basic output
python manage.py test news.tests

# Run all tests with detailed output
python manage.py test news.tests --verbosity=2
```

#### 2. Run Specific Test Categories

**Authentication Tests:**
```bash
python manage.py test news.tests.AuthenticationAPITest
```

**Article API Tests:**
```bash
python manage.py test news.tests.ArticleAPITest
```

**Newsletter API Tests:**
```bash
python manage.py test news.tests.NewsletterAPITest
```

**Publisher API Tests:**
```bash
python manage.py test news.tests.PublisherAPITest
```

**Journalist API Tests:**
```bash
python manage.py test news.tests.JournalistAPITest
```

**Error Handling Tests:**
```bash
python manage.py test news.tests.APIErrorHandlingTest
```

**Pagination Tests:**
```bash
python manage.py test news.tests.APIPaginationTest
```

#### 3. Run Individual Tests

```bash
# Test token authentication
python manage.py test news.tests.AuthenticationAPITest.test_token_authentication_success

# Test article subscription filtering
python manage.py test news.tests.ArticleAPITest.test_article_list_reader_with_journalist_subscription

# Test unauthorized access
python manage.py test news.tests.ArticleAPITest.test_article_by_journalist_unauthorized
```

#### 4. Test Coverage Analysis

**Install coverage tool:**
```bash
pip install coverage
```

**Run tests with coverage:**
```bash
# Generate coverage report
coverage run --source='.' manage.py test news.tests
coverage report

# Generate HTML coverage report
coverage html
```

### Test Results Example

```bash
$ python manage.py test news.tests --verbosity=1

Found 39 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
.......................................

----------------------------------------------------------------------
Ran 39 tests in 81.220s

OK
Destroying test database for alias 'default'...
```

### Manual Testing with Test Script

Use the included manual testing script:

```bash
# Test API with your credentials
python test_api.py --username your_username --password your_password

# Test with custom base URL
python test_api.py --username your_username --password your_password --base-url http://localhost:8000/api/v1

# Test POST functionality (create articles and newsletters - requires journalist role)
python test_api.py --username journalist_username --password password --test-create
```

### Test Environment Setup

**Prerequisites:**
- Django test database (automatically created)
- All required dependencies installed
- Virtual environment activated

**Test Data:**
Tests automatically create:
- Users with different roles (reader, journalist, editor, publisher)
- Publishers and journalist profiles
- Articles with different statuses (approved, pending)
- Newsletters
- Subscriptions for testing filtering
- Authentication tokens

### Continuous Integration

**For CI/CD pipelines, use:**
```bash
# Run tests with CI-friendly output
python manage.py test news.tests --verbosity=0 --keepdb

# Run with coverage for CI reports
coverage run --source='.' manage.py test news.tests
coverage xml  # Generates coverage.xml for CI tools
```

### Test Categories Explained

#### **Authentication Tests (5 tests)**
- Token generation and validation
- Invalid credentials handling
- Unauthorized access protection
- Token-based API access

#### **Article API Tests (15 tests)**
- List articles with subscription filtering
- Article detail views
- Journalist and publisher filtering
- Role-based access control
- Status filtering (approved only)

#### **Newsletter API Tests (5 tests)**
- Newsletter listing with subscriptions
- Newsletter detail views
- Role-based access

#### **Publisher & Journalist Tests (6 tests)**
- List and detail views
- Authentication requirements
- Data structure validation

#### **Error Handling Tests (8 tests)**
- Non-existent resource handling
- Multiple subscription scenarios
- Inactive subscription filtering
- Edge cases and boundary conditions

### Debugging Failed Tests

**Common issues and solutions:**

1. **Test database issues:**
   ```bash
   # Reset test database
   python manage.py flush --database=test
   ```

2. **Migration issues:**
   ```bash
   # Apply migrations before testing
   python manage.py migrate
   ```

3. **Token-related failures:**
   - Check that `rest_framework.authtoken` is in `INSTALLED_APPS`
   - Verify token creation in test setup

4. **Permission failures:**
   - Verify user roles are set correctly
   - Check subscription relationships

### Performance Testing

For performance testing of your API:

```bash
# Install testing tools
pip install locust

# Basic load test (create locustfile.py first)
locust -f locustfile.py --host=http://localhost:8000
```

## Subscription Logic

### For Readers:
- Only see articles and newsletters from publishers/journalists they are subscribed to
- Must be subscribed to access specific journalist/publisher endpoints

### For Journalists, Editors, Publishers:
- Can see all approved articles and newsletters
- No subscription restrictions apply

## Response Format

### Article List Response:
```json
{
    "count": 25,
    "next": "http://127.0.0.1:8000/api/v1/articles/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Sample Article",
            "journalist_name": "John Doe",
            "publisher_name": "News Corp",
            "created_at": "2025-09-17T12:00:00Z"
        }
    ]
}
```

### Article Detail Response:
```json
{
    "id": 1,
    "title": "Sample Article",
    "content": "Article content...",
    "journalist": {
        "id": 1,
        "name": "John Doe",
        "username": "johndoe",
        "publisher_name": "News Corp"
    },
    "publisher": {
        "id": 1,
        "name": "News Corp"
    },
    "created_at": "2025-09-17T12:00:00Z",
    "updated_at": "2025-09-17T12:00:00Z"
}
```

### Create Article Response:
```json
{
    "id": 25,
    "title": "My New Article",
    "content": "This is the article content...",
    "status": "pending",
    "journalist": {
        "id": 1,
        "name": "John Doe",
        "username": "johndoe",
        "publisher_name": "News Corp"
    },
    "publisher": {
        "id": 1,
        "name": "News Corp"
    },
    "created_at": "2025-09-18T20:15:00Z",
    "updated_at": "2025-09-18T20:15:00Z"
}
```

### Create Newsletter Response:
```json
{
    "id": 12,
    "title": "Weekly Newsletter",
    "content": "This week in news...",
    "journalist": {
        "id": 1,
        "name": "John Doe",
        "username": "johndoe",
        "publisher_name": "News Corp"
    },
    "publisher": {
        "id": 1,
        "name": "News Corp"
    },
    "created_at": "2025-09-18T20:16:00Z",
    "updated_at": "2025-09-18T20:16:00Z"
}
```

## Security Features

- **Token Authentication**: All API endpoints require valid authentication tokens
- **Role-based Access**: Different access levels based on user roles
- **Subscription Verification**: Readers can only access content they're subscribed to
- **HTTPS Ready**: Configured for secure production deployment

## Pagination

- Default page size: 20 items
- Use `?page=2` parameter to navigate pages
- Response includes `count`, `next`, and `previous` fields

## Error Handling

The API returns appropriate HTTP status codes:
- `200` - Success
- `400` - Bad Request (missing required parameters)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (not subscribed/insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

## Production Considerations

1. **HTTPS**: Always use HTTPS in production
2. **Token Security**: Store tokens securely on client side
3. **Rate Limiting**: Consider implementing rate limiting for production use
4. **Database Optimization**: Use proper indexing and query optimization
5. **Caching**: Implement caching for frequently accessed data

## Quick Testing Reference

### Most Common Test Commands

```bash
# Run all API tests
python manage.py test news.tests

# Run specific test category
python manage.py test news.tests.ArticleAPITest

# Run single test with details
python manage.py test news.tests.AuthenticationAPITest.test_token_authentication_success --verbosity=2

# Manual API testing
python test_api.py --username your_username --password your_password

# Generate test coverage report
coverage run --source='.' manage.py test news.tests
coverage report
```

### Test Status: ✅ All 39 Tests Passing

- **Authentication**: 5/5 tests passing
- **Articles**: 15/15 tests passing  
- **Newsletters**: 5/5 tests passing
- **Publishers**: 3/3 tests passing
- **Journalists**: 3/3 tests passing
- **Error Handling**: 8/8 tests passing

*Last tested: 2025-09-18*

---

**For detailed API testing instructions, see the [Testing the API](#testing-the-api) section above.**
