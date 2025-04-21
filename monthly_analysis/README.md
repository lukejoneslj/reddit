# Monthly Subreddit Toxicity Analyzer

This Python script analyzes the toxicity levels of posts and comments from two subreddits (r/politics and r/conservative) using the Reddit API and Google's Gemini API, focusing specifically on the top posts from the past month.

## Features

- Retrieves top 10 posts from the past month for each subreddit
- Analyzes top 5 comments per post
- Provides toxicity ratings on a scale from 1 to 10
- Includes post and comment dates for temporal analysis
- Outputs results to a CSV file with detailed information
- Handles API rate limits with exponential backoff and retry logic
- Provides statistics comparing toxicity levels between subreddits

## Key Differences from the Main Analyzer

- Focuses on the past month's content rather than all-time top posts
- Includes date information for posts and comments
- Provides additional statistics comparing post vs. comment toxicity
- Uses a separate CSV file for results (`monthly_toxicity_analysis.csv`)

## Usage

Make sure you have activated the virtual environment and installed all dependencies. Then run:

```bash
cd monthly_analysis
python monthly_toxicity_analyzer.py
```

## Output Format

The CSV output includes the following columns:
- `subreddit`: The subreddit name (politics or conservative)
- `post_title`: The title of the post
- `post_date`: The date when the post was created
- `comment_date`: The date when the comment was created
- `comment_text`: The text of the comment (empty for main posts)
- `toxicity_score`: A score from 1 to 10 indicating toxicity level
- `explanation`: A brief explanation for the toxicity score

## Statistics

The script provides several statistics:
- Total number of items analyzed
- Average, minimum, and maximum toxicity scores by subreddit
- Comparison of average toxicity between posts and comments

## API Configuration

The script uses the same API credentials as the main analyzer:

- Reddit API:
  - Client ID: I9G0MVpz4Ec1BAkopA85JA
  - Client Secret: cyZxeRWy3P0jnOrKqZ3WvHYUCHlThA
  - User Agent: script:toxicity-analysis:v1.0 (by /u/Ambitious_Spread_895)

- Gemini API:
  - API Key: AIzaSyCBisD_PXRmS0rvAHM-kYGKrVbJiSFTqn0
  - Model: gemini-2.0-flash-lite 