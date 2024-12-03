import praw
import json
import time
from praw.models import MoreComments

# Initialize the Reddit API client
reddit = praw.Reddit(
    client_id="1165tokZ2UXzA-PHTRpNZg",
    client_secret="XFWDD6bI-5CfZSj2H45IIk6WOzS4mQ",
    user_agent="damg_ASS"
)

# Choose a subreddit to scrape
subreddit_name = "Sneakers"
subreddit = reddit.subreddit(subreddit_name)

# Function to fetch a limited number of comments
def fetch_comments(comment_list, limit=30):
    comments_data = []
    count = 0
    for comment in comment_list:
        if isinstance(comment, MoreComments) or count >= limit:
            continue
        try:
            comment_data = {
                "author": str(comment.author),
                "body": comment.body,
                "score": comment.score,
                "created_utc": comment.created_utc
            }
            comments_data.append(comment_data)
            count += 1
        except Exception as e:
            print(f"Skipping a comment due to an error: {e}")
    return comments_data

# Fetch top 2000 posts from this year with pagination
posts = []
batch_size = 100  # Max limit per API call
count = 0
after = None

while count < 10:
    submissions = subreddit.top(limit=batch_size, time_filter='year', params={"after": after})
    batch_posts = []
    try:
        for submission in submissions:
            after = submission.name  # Set pagination token
            count += 1
            print(f"Fetching post {count}: {submission.title}")

            submission.comments.replace_more(limit=0)  # Load all top-level comments
            post_data = {
                "title": submission.title,
                "author": str(submission.author),
                "score": submission.score,
                "url": submission.url,
                "num_comments": submission.num_comments,
                "created_utc": submission.created_utc,
                "comments": fetch_comments(submission.comments.list(), limit=30)  # Limit to 30 comments
            }
            batch_posts.append(post_data)

            if count >= 10:
                break

        # Append to main post list
        posts.extend(batch_posts)

        # Save batch to JSON incrementally
        with open('reddit_posts.json', 'w') as json_file:
            json.dump(posts, json_file, indent=4)

        # Respect Reddit's rate limits
        time.sleep(60)  # Adjust based on load

    except Exception as e:
        print(f"Error fetching posts: {e}")
        break

print(f"Successfully fetched {len(posts)} posts and saved to reddit_posts.json")
