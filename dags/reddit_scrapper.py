import os
import praw
import pandas as pd
import datetime as dt
from typing import List, Optional, Dict
from dotenv import load_dotenv
from praw.models import MoreComments

class RedditScraper:
    """
    A comprehensive class for scraping Reddit subreddit data with flexible authentication.
    
    Supports authentication via:
    1. Environment variables
    2. Direct credential input
    3. JSON configuration file
    """

    def __init__(
        self, 
        client_id: Optional[str] = None, 
        client_secret: Optional[str] = None, 
        user_agent: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        load_env: bool = True
    ):
        """
        Initialize the Reddit Scraper with flexible authentication options.
        
        Args:
            client_id (str, optional): Reddit API client ID
            client_secret (str, optional): Reddit API client secret
            user_agent (str, optional): User agent string
            username (str, optional): Reddit username
            password (str, optional): Reddit password
            load_env (bool, optional): Whether to load environment variables. Defaults to True.
        """
        # Load environment variables if specified
        if load_env:
            load_dotenv()

        # Prioritize direct input over environment variables
        self.credentials = {
            'client_id': client_id or os.getenv('REDDIT_CLIENT_ID'),
            'client_secret': client_secret or os.getenv('REDDIT_CLIENT_SECRET'),
            'user_agent': user_agent or os.getenv('REDDIT_USER_AGENT', 'Reddit Scraper'),
            'username': username or os.getenv('REDDIT_USERNAME'),
            'password': password or os.getenv('REDDIT_PASSWORD')
        }

        # Authenticate Reddit instance
        self.reddit = self._authenticate()

    def _authenticate(self) -> praw.Reddit:
        """
        Authenticate with Reddit API using provided or environment credentials.
        
        Returns:
            praw.Reddit: Authenticated Reddit instance
        
        Raises:
            ValueError: If required credentials are missing
        """
        # Remove None values from credentials
        cleaned_credentials = {k: v for k, v in self.credentials.items() if v is not None}

        # Validate essential credentials
        required_keys = ['client_id', 'client_secret', 'user_agent']
        for key in required_keys:
            if key not in cleaned_credentials:
                raise ValueError(f"Missing essential Reddit API credential: {key.upper()}")

        try:
            return praw.Reddit(**cleaned_credentials)
        except Exception as e:
            raise ValueError(f"Authentication failed: {str(e)}")

    def scrape_subreddit(
        self,
        subreddit_name: str,
        sort_by: str = 'top',
        time_filter: str = 'year',
        limit: int = 10,
        include_comments: bool = True,
        comments_limit: int = 10
    ) -> pd.DataFrame:
        """
        Scrape posts from a specified subreddit with advanced configuration.
        
        Args:
            subreddit_name (str): Name of the subreddit to scrape
            sort_by (str, optional): Sorting method. Defaults to 'top'.
            time_filter (str, optional): Time filter for sorting. Defaults to 'week'.
            limit (int, optional): Number of posts to retrieve. Defaults to 100.
            include_comments (bool, optional): Whether to include comments. Defaults to True.
            comments_limit (int, optional): Number of comments to retrieve per post. Defaults to 10.
        
        Returns:
            pd.DataFrame: DataFrame containing scraped post information
        """
        try:
            # Select the subreddit
            subreddit = self.reddit.subreddit(subreddit_name)

            # Select sorting method
            sorting_methods = {
                'top': subreddit.top(time_filter=time_filter, limit=limit),
                'hot': subreddit.hot(limit=limit),
                'new': subreddit.new(limit=limit),
                'rising': subreddit.rising(limit=limit)
            }
            
            posts = sorting_methods.get(sort_by.lower())
            if not posts:
                raise ValueError(f"Invalid sort method: {sort_by}")

            # Prepare data collection
            topics_dict = {
                "title": [],
                "score": [],
                "id": [],
                "url": [],
                "comments_num": [],
                "created": [],
                "author": [],
                "body": [],
                "subreddit": [],
                "comments": [],
            }

            # Collect post data
            for submission in posts:
                # Extract post details
                topics_dict["title"].append(submission.title)
                topics_dict["score"].append(submission.score)
                topics_dict["id"].append(submission.id)
                topics_dict["url"].append(submission.url)
                topics_dict["comments_num"].append(submission.num_comments)
                topics_dict["created"].append(
                    dt.datetime.fromtimestamp(submission.created)
                )
                topics_dict["author"].append(
                    str(submission.author) if submission.author else "Deleted"
                )
                topics_dict["body"].append(
                    submission.selftext if submission.selftext else "No body text"
                )
                topics_dict["subreddit"].append(subreddit_name)

                # Collect comments if enabled
                if include_comments:
                    comment_texts = []
                    submission.comments.replace_more(limit=0)  # Expand comment trees
                    for comment in submission.comments.list()[:comments_limit]:
                        if not isinstance(comment, MoreComments):
                            comment_texts.append({
                                'text': comment.body,
                                'score': comment.score,
                                'author': str(comment.author)
                            })
                    topics_dict["comments"].append(comment_texts)
                else:
                    topics_dict["comments"].append([])

            # Convert to DataFrame
            return pd.DataFrame(topics_dict)

        except praw.exceptions.PRAWException as e:
            print(f"Reddit API Error: {e}")
            return pd.DataFrame()
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return pd.DataFrame()

    def save_to_file(
        self,
        dataframe: pd.DataFrame,
        base_filename: str = 'reddit_data',
        output_dir: str = 'output',
        formats: List[str] = ['csv', 'xlsx']
    ) -> None:
        """
        Save DataFrame to multiple file formats with flexible options.
        
        Args:
            dataframe (pd.DataFrame): DataFrame to save
            base_filename (str, optional): Base filename for output files
            output_dir (str, optional): Directory to save files
            formats (List[str], optional): File formats to save. Defaults to CSV and Excel
        """
        if dataframe.empty:
            print("No data to save.")
            return

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamped filename
        timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")

        try:
            # Save to specified formats
            for fmt in formats:
                filename = os.path.join(output_dir, f'{base_filename}_{timestamp}.{fmt}')
                
                if fmt == 'csv':
                    dataframe.to_csv(filename, index=False)
                elif fmt == 'xlsx':
                    dataframe.to_excel(filename, index=False)
                elif fmt == 'json':
                    dataframe.to_json(filename, orient='records')
                
                print(f"Data saved to {fmt.upper()}: {filename}")

        except PermissionError:
            print("Permission denied. Unable to save files.")
        except Exception as e:
            print(f"Error saving files: {e}")

    def scrape_multiple_subreddits(
        self,
        subreddits: List[str],
        sort_by: str = 'top',
        time_filter: str = 'week',
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Scrape multiple subreddits and combine their data.
        
        Args:
            subreddits (List[str]): List of subreddit names to scrape
            sort_by (str, optional): Sorting method. Defaults to 'top'.
            time_filter (str, optional): Time filter for sorting. Defaults to 'week'.
            limit (int, optional): Number of posts to retrieve per subreddit. Defaults to 100.
        
        Returns:
            pd.DataFrame: Combined DataFrame of posts from multiple subreddits
        """
        combined_data = []

        for subreddit_name in subreddits:
            subreddit_data = self.scrape_subreddit(
                subreddit_name,
                sort_by=sort_by,
                time_filter=time_filter,
                limit=limit
            )
            combined_data.append(subreddit_data)

        return pd.concat(combined_data, ignore_index=True)