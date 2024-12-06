import os
from dotenv import load_dotenv

# Import custom modules
from reddit_scrapper import RedditScraper
from reddit_data_processor import RedditDataProcessor

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize scraper and processor
    scraper = RedditScraper()
    processor = RedditDataProcessor()
    
    # Subreddits to scrape
    subreddits = ['Sneakers', 'handbags']
    
    try:
        # Scrape data
        scraped_data = scraper.scrape_multiple_subreddits(
            subreddits, 
            sort_by='top', 
            time_filter='year', 
            limit=10
        )
        
        # Save to CSV
        scraper.save_to_file(
            scraped_data, 
            base_filename='reddit_posts', 
            output_dir='output', 
            formats=['csv']
        )
        
        # Process scraped data
        processor.process_reddit_data(scraped_data)
    
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()