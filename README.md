# Subreddit Toxicity Analyzer

This Python script analyzes the toxicity levels of posts and comments from two subreddits (r/politics and r/conservative) using the Reddit API and Google's Gemini API.

## Features

- Retrieves top posts from each subreddit (default: 10 posts)
- Analyzes top comments per post (default: 5 comments)
- Provides toxicity ratings on a scale from 1 to 10
- Outputs results to a CSV file with detailed information
- Handles API rate limits with exponential backoff and retry logic
- Provides statistics comparing toxicity levels between subreddits

## Requirements

- Python 3.7+
- PRAW (Python Reddit API Wrapper)
- Google Generative AI Python library
- pandas
- tqdm

## Installation

1. Clone this repository:
```bash
git clone https://github.com/lukejoneslj/reddit.git
cd reddit
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Simply run the script:
```bash
python subreddit_toxicity_analyzer.py
```

The script will:
1. Analyze posts and comments from r/politics and r/conservative
2. Generate a CSV file named `subreddit_toxicity_analysis.csv` with the results
3. Display basic statistics in the console

### Customization

You can modify these variables in the script to adjust the number of posts and comments:
```python
POSTS_LIMIT = 10  # Number of posts to analyze per subreddit
COMMENTS_LIMIT = 5  # Number of comments to analyze per post
```

## Rate Limit Handling

The script implements exponential backoff and retry logic to handle API rate limits:
- When a rate limit error (HTTP 429) is encountered, the script will wait and retry
- Retry delays are based on the response from the API or calculated using exponential backoff
- Maximum retry attempts can be configured (default: 5)

## Output Format

The CSV output includes the following columns:
- `subreddit`: The subreddit name (politics or conservative)
- `post_title`: The title of the post
- `comment_text`: The text of the comment (empty for main posts)
- `toxicity_score`: A score from 1 to 10 indicating toxicity level
- `explanation`: A brief explanation for the toxicity score

## Toxicity Scale

The toxicity scale ranges from 1 to 10:
1. Completely non-toxic, respectful, and constructive
2. Generally respectful with minor criticism
3. Mildly critical but still respectful and civil
4. Noticeably critical, some negative tone, but no hostility
5. Moderately negative, clear criticism, mild hostility
6. Negative tone with moderate hostility and sarcasm
7. Clearly hostile, aggressive language, minor insults
8. Very hostile, significant insults and inflammatory language
9. Extremely hostile, severe insults, potentially threatening language
10. Maximum hostility, threats, harassment, or hate speech

## API Configuration

The script uses the following API credentials:

- Reddit API:
  - Client ID: I9G0MVpz4Ec1BAkopA85JA
  - Client Secret: cyZxeRWy3P0jnOrKqZ3WvHYUCHlThA
  - User Agent: script:toxicity-analysis:v1.0 (by /u/Ambitious_Spread_895)

- Gemini API:
  - API Key: AIzaSyCBisD_PXRmS0rvAHM-kYGKrVbJiSFTqn0
  - Model: gemini-2.0-flash-lite (Free tier has rate limits of approximately 30 requests per minute)

## License

MIT 