#!/usr/bin/env python3
"""
Monthly Subreddit Toxicity Analyzer

Analyzes the toxicity levels of posts and comments from two subreddits
using Reddit API and Google's Gemini API. Focuses on top posts from the past month.
"""

import os
import json
import time
import csv
import praw
import google.generativeai as genai
from tqdm import tqdm
import pandas as pd
import re
import random
from datetime import datetime

# Configure Reddit API
reddit = praw.Reddit(
    client_id="I9G0MVpz4Ec1BAkopA85JA",
    client_secret="cyZxeRWy3P0jnOrKqZ3WvHYUCHlThA",
    user_agent="script:toxicity-analysis:v1.0 (by /u/Ambitious_Spread_895)"
)

# Configure Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyCBisD_PXRmS0rvAHM-kYGKrVbJiSFTqn0"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-2.0-flash-lite')

# Set lower limits to avoid rate limiting
POSTS_LIMIT = 10  # Analyze 10 posts per subreddit
COMMENTS_LIMIT = 5  # Analyze 5 comments per post

def analyze_toxicity(text, max_retries=5):
    """
    Analyze text for toxicity using Gemini API with retry logic.
    
    Args:
        text (str): The text to analyze
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        dict: Dictionary containing toxicity score and explanation
    """
    # Clean text to prevent prompt injection and limit length
    text = text.strip()
    if not text:
        return {"toxicity_score": 1, "explanation": "Empty text"}
    
    # Limit text length to avoid exceeding model limits
    if len(text) > 10000:
        text = text[:10000] + "..."
    
    prompt = f"""
    Analyze the following text and rate its toxicity on a scale from 1 (least toxic) to 10 (most toxic).

    Toxicity Scale Definition:
    1 - Completely non-toxic, respectful, and constructive.
    2 - Generally respectful with minor criticism.
    3 - Mildly critical but still respectful and civil.
    4 - Noticeably critical, some negative tone, but no hostility.
    5 - Moderately negative, clear criticism, mild hostility.
    6 - Negative tone with moderate hostility and sarcasm.
    7 - Clearly hostile, aggressive language, minor insults.
    8 - Very hostile, significant insults and inflammatory language.
    9 - Extremely hostile, severe insults, potentially threatening language.
    10 - Maximum hostility, threats, harassment, or hate speech.

    TEXT:
    "{text}"

    Respond ONLY in JSON:
    {{
        "toxicity_score": number,
        "explanation": "brief reason for score"
    }}
    """
    
    retries = 0
    while retries <= max_retries:
        try:
            response = model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            
            # Use regex to extract the JSON part
            match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if match:
                json_str = match.group(0)
                try:
                    result = json.loads(json_str)
                    return {
                        "toxicity_score": int(result.get("toxicity_score", 1)),
                        "explanation": result.get("explanation", "No explanation provided")
                    }
                except json.JSONDecodeError:
                    return {"toxicity_score": 1, "explanation": "Failed to parse JSON response"}
            else:
                return {"toxicity_score": 1, "explanation": "No JSON found in response"}
        
        except Exception as e:
            error_msg = str(e)
            retries += 1
            
            if "429" in error_msg and retries <= max_retries:
                # Extract retry delay if available, or use exponential backoff
                retry_delay = 60
                delay_match = re.search(r'retry_delay\s*{\s*seconds:\s*(\d+)', error_msg)
                if delay_match:
                    retry_delay = int(delay_match.group(1))
                else:
                    # Exponential backoff with jitter
                    retry_delay = min(60 * (2 ** retries) + random.uniform(0, 10), 300)
                
                print(f"Rate limit exceeded. Waiting for {retry_delay} seconds before retry {retries}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                if retries > max_retries:
                    print(f"Maximum retries exceeded. Giving up on analyzing this text.")
                else:
                    print(f"Error analyzing toxicity: {e}")
                return {"toxicity_score": 1, "explanation": f"Error: {error_msg[:100]}..."}
    
    return {"toxicity_score": 1, "explanation": "Failed after maximum retries"}

def get_top_monthly_posts(subreddit_name, limit=POSTS_LIMIT):
    """
    Get top posts from the past month in a subreddit.
    
    Args:
        subreddit_name (str): Name of the subreddit
        limit (int): Number of posts to retrieve
        
    Returns:
        list: List of post objects
    """
    subreddit = reddit.subreddit(subreddit_name)
    return list(subreddit.top(limit=limit, time_filter="month"))

def get_top_comments(post, limit=COMMENTS_LIMIT):
    """
    Get top comments from a post.
    
    Args:
        post (praw.models.Submission): Post object
        limit (int): Number of comments to retrieve
        
    Returns:
        list: List of comment objects
    """
    post.comment_sort = "top"
    post.comments.replace_more(limit=0)  # Skip "more comments" objects
    return post.comments.list()[:limit]

def analyze_subreddit(subreddit_name, results):
    """
    Analyze posts and comments from a subreddit.
    
    Args:
        subreddit_name (str): Name of the subreddit
        results (list): List to store results
        
    Returns:
        None
    """
    print(f"\nAnalyzing subreddit: r/{subreddit_name}")
    
    try:
        # Get top posts from the past month
        posts = get_top_monthly_posts(subreddit_name)
        
        # Analyze each post and its comments
        for post in tqdm(posts, desc=f"Analyzing monthly posts from r/{subreddit_name}"):
            try:
                # Get post creation date
                post_date = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')
                
                # Analyze post title
                post_title = post.title
                post_analysis = analyze_toxicity(post_title)
                
                # Add post result to results list
                results.append({
                    "subreddit": subreddit_name,
                    "post_title": post_title,
                    "post_date": post_date,
                    "comment_text": "",  # Empty for main post
                    "toxicity_score": post_analysis["toxicity_score"],
                    "explanation": post_analysis["explanation"]
                })
                
                # Get and analyze top comments
                try:
                    comments = get_top_comments(post)
                    for comment in comments:
                        try:
                            if hasattr(comment, 'body') and comment.body:
                                comment_analysis = analyze_toxicity(comment.body)
                                comment_date = datetime.fromtimestamp(comment.created_utc).strftime('%Y-%m-%d')
                                
                                # Add comment result to results list
                                results.append({
                                    "subreddit": subreddit_name,
                                    "post_title": post_title,
                                    "post_date": post_date,
                                    "comment_date": comment_date,
                                    "comment_text": comment.body,
                                    "toxicity_score": comment_analysis["toxicity_score"],
                                    "explanation": comment_analysis["explanation"]
                                })
                            
                            # Respect API rate limits with a longer delay
                            time.sleep(2)
                        except Exception as e:
                            print(f"Error analyzing comment: {e}")
                except Exception as e:
                    print(f"Error getting comments for post: {e}")
                
                # Respect API rate limits with a longer delay between posts
                time.sleep(5)
            except Exception as e:
                print(f"Error analyzing post: {e}")
    except Exception as e:
        print(f"Error analyzing subreddit {subreddit_name}: {e}")

def save_results_to_csv(results, filename="monthly_toxicity_analysis.csv"):
    """
    Save analysis results to a CSV file.
    
    Args:
        results (list): List of result dictionaries
        filename (str): Name of the output file
        
    Returns:
        None
    """
    try:
        # Convert results to DataFrame
        df = pd.DataFrame(results)
        
        # Save to CSV
        df.to_csv(filename, index=False)
        print(f"\nResults saved to {filename}")
    except Exception as e:
        print(f"Error saving results to CSV: {e}")
        
        # Fallback to using csv module
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ["subreddit", "post_title", "post_date", "comment_date", 
                             "comment_text", "toxicity_score", "explanation"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for result in results:
                    writer.writerow(result)
            print(f"\nResults saved to {filename} using fallback method")
        except Exception as e2:
            print(f"Fallback CSV save also failed: {e2}")

def main():
    """
    Main function to run the monthly subreddit toxicity analysis.
    """
    current_month = datetime.now().strftime('%B %Y')
    print(f"Running monthly analysis for {current_month}")
    print(f"Analyzing {POSTS_LIMIT} posts and {COMMENTS_LIMIT} comments per post")
    
    results = []
    
    # Analyze liberal subreddit
    analyze_subreddit("politics", results)
    
    # Analyze conservative subreddit
    analyze_subreddit("conservative", results)
    
    # Save results to CSV
    save_results_to_csv(results)
    
    # Print basic statistics
    if results:
        df = pd.DataFrame(results)
        print("\nBasic Statistics:")
        print(f"Total items analyzed: {len(df)}")
        
        # Compare toxicity averages by subreddit
        subreddit_stats = df.groupby("subreddit")["toxicity_score"].agg(['mean', 'min', 'max', 'count'])
        print("\nToxicity by Subreddit:")
        print(subreddit_stats)
        
        # Show toxicity distribution
        if 'comment_text' in df.columns:
            # Separate posts and comments
            posts = df[df['comment_text'] == ""]
            comments = df[df['comment_text'] != ""]
            
            print("\nPosts vs Comments Toxicity:")
            print(f"Average post toxicity: {posts['toxicity_score'].mean():.2f}")
            print(f"Average comment toxicity: {comments['toxicity_score'].mean():.2f}")

if __name__ == "__main__":
    main() 