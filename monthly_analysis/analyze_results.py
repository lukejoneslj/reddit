#!/usr/bin/env python3
"""
Analyze results from subreddit toxicity analysis
"""

import pandas as pd
import os

# Read the CSV file
df = pd.read_csv('monthly_toxicity_analysis.csv')

# Filter posts only (looking for empty comment_text)
# Some rows might have whitespace or newline characters, so let's strip them
df['comment_text'] = df['comment_text'].astype(str).str.strip()
posts = df[df['comment_text'].isin(['', 'nan'])]
comments = df[~df['comment_text'].isin(['', 'nan'])]

# Print the total number of posts and comments found
print(f"Total posts found: {len(posts)}")
print(f"Total comments found: {len(comments)}")

# Group by subreddit and sort
for subreddit in ['politics', 'conservative']:
    # Process posts
    subreddit_posts = posts[posts['subreddit'] == subreddit]
    
    # Skip if no data for this subreddit
    if len(subreddit_posts) == 0:
        print(f'No posts found for r/{subreddit}')
    else:
        # Get highest toxicity posts
        print(f'\nTop 3 highest toxicity posts in r/{subreddit}:')
        highest = subreddit_posts.sort_values('toxicity_score', ascending=False).head(3)
        for _, row in highest.iterrows():
            print(f'Score: {row["toxicity_score"]} - "{row["post_title"]}"')
            print(f'Explanation: {row["explanation"]}\n')
        
        # Get lowest toxicity posts
        print(f'\nTop 3 lowest toxicity posts in r/{subreddit}:')
        lowest = subreddit_posts.sort_values('toxicity_score').head(3)
        for _, row in lowest.iterrows():
            print(f'Score: {row["toxicity_score"]} - "{row["post_title"]}"')
            print(f'Explanation: {row["explanation"]}\n')
    
    # Process comments
    subreddit_comments = comments[comments['subreddit'] == subreddit]
    
    # Skip if no comments for this subreddit
    if len(subreddit_comments) == 0:
        print(f'No comments found for r/{subreddit}')
    else:
        # Get highest toxicity comments
        print(f'\nTop 3 highest toxicity comments in r/{subreddit}:')
        highest_comments = subreddit_comments.sort_values('toxicity_score', ascending=False).head(3)
        for _, row in highest_comments.iterrows():
            print(f'Score: {row["toxicity_score"]} - Post: "{row["post_title"]}"')
            print(f'Comment: "{row["comment_text"][:150]}..."' if len(row["comment_text"]) > 150 else f'Comment: "{row["comment_text"]}"')
            print(f'Explanation: {row["explanation"]}\n')
        
        # Get lowest toxicity comments
        print(f'\nTop 3 lowest toxicity comments in r/{subreddit}:')
        lowest_comments = subreddit_comments.sort_values('toxicity_score').head(3)
        for _, row in lowest_comments.iterrows():
            print(f'Score: {row["toxicity_score"]} - Post: "{row["post_title"]}"')
            print(f'Comment: "{row["comment_text"][:150]}..."' if len(row["comment_text"]) > 150 else f'Comment: "{row["comment_text"]}"')
            print(f'Explanation: {row["explanation"]}\n') 