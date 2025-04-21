#!/usr/bin/env python3
"""
Analyze results from subreddit toxicity analysis
"""

import pandas as pd
import os

# Read the CSV file
df = pd.read_csv('monthly_toxicity_analysis.csv')

# Filter posts only (no comments)
posts = df[df['comment_text'] == '']

# Group by subreddit and sort
for subreddit in ['politics', 'conservative']:
    subreddit_posts = posts[posts['subreddit'] == subreddit]
    
    # Skip if no data for this subreddit
    if len(subreddit_posts) == 0:
        print(f'No data found for r/{subreddit}')
        continue
    
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