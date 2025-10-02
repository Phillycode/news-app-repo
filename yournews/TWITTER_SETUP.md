# Twitter Integration Setup Guide

This guide is for setting up Twitter/X API integration to automatically post approved articles to Twitter.

## 1. Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Apply for a developer account if you don't have one
3. Create a new app or use an existing one
4. Generate the following credentials:
   - **API Key** (Consumer Key)
   - **API Secret** (Consumer Secret)
   - **Access Token**
   - **Access Token Secret**
   - **Bearer Token**

## 2. Configure Django Settings

Update your `settings.py` file with your Twitter API credentials:

```python
# Twitter/X API Configuration
TWITTER_API_KEY = "your_actual_api_key_here"
TWITTER_API_SECRET = "your_actual_api_secret_here"
TWITTER_ACCESS_TOKEN = "your_actual_access_token_here"
TWITTER_ACCESS_TOKEN_SECRET = "your_actual_access_token_secret_here"
TWITTER_BEARER_TOKEN = "your_actual_bearer_token_here"

# Twitter integration settings
TWITTER_ENABLED = True  # Set to False to disable Twitter posting
TWITTER_POST_ON_APPROVAL = True  # Post to Twitter when articles are approved
```

## 3. Test the Integration

Run the test command to verify your Twitter API connection:

```bash
python manage.py test_twitter
```

This will:
- Test your API credentials
- Show your connected Twitter account
- Optionally post a test tweet

## 4. How It Works

Once configured, the system will automatically:

1. **When an editor approves an article**, the system will:
   - Send email notifications (existing functionality)
   - **Post a tweet** with the article title and journalist name

2. **Tweet Format**:
   ```
   New article published: [Article Title]
   By: [Journalist Name]
   ```

3. **Error Handling**:
   - If Twitter API is not configured, it will skip posting (no errors)
   - If posting fails, it logs the error but doesn't interrupt the approval process

## 5. Troubleshooting

### Common Issues:

**❌ "Twitter API authentication failed"**
- Double-check your API credentials
- Ensure your Twitter app has the correct permissions

**❌ "Twitter API access forbidden"**
- Check your app permissions in the Twitter Developer Portal
- Make sure your app has "Read and Write" permissions

**❌ "Rate limit exceeded"**
- Twitter has rate limits for posting
- The system will automatically retry if configured

### Testing Steps:

1. **Test API connection:**
   ```bash
   python manage.py test_twitter
   ```

2. **Check logs for errors:**
   - Django will log Twitter-related errors
   - Check your console output or log files

3. **Disable temporarily:**
   ```python
   TWITTER_ENABLED = False  # In settings.py
   ```

## 6. Security Notes

- **Never commit API keys to version control**
- Consider using environment variables for production:
  ```python
  import os
  TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
  ```
- Keep your API credentials secure and rotate them if compromised

## 7. Twitter Developer Requirements

Make sure your Twitter app has:
- ✅ **Read and Write** permissions
- ✅ **Tweet** permissions

Once set up, articles will be posted to Twitter/X upon editor approval.

**For testing instructions, see the instructions above - 3. Test the integration