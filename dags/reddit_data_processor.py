import os
import json
from datetime import datetime
import pandas as pd
import time

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore


# Additional imports
from pinecone import Pinecone, ServerlessSpec
import boto3
import psycopg2
from dotenv import load_dotenv

class RedditDataProcessor:
    def __init__(self):
        """
        Initialize the RedditDataProcessor with necessary configurations and clients
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.pinecone_environment = os.getenv('PINECONE_ENVIRONMENT')
        self.pinecone_index_name = os.getenv('PINECONE_INDEX_NAME')
        
        # AWS S3 configuration
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_s3_bucket = os.getenv('AWS_S3_BUCKET')
        
        # PostgreSQL configuration
        self.db_host = os.getenv("POSTGRES_HOSTNAME")
        self.db_name = os.getenv("POSTGRES_DB")
        self.db_user = os.getenv("POSTGRES_USER")
        self.db_password = os.getenv("POSTGRES_PASSWORD")
        self.db_port = os.getenv("POSTGRES_PORT")
        
        # Initialize clients
        self._init_s3_client()
        self._init_pinecone()
        self._init_embedding_model()
    
    def _init_s3_client(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key
        )
    
    def _init_pinecone(self):
        """Initialize Pinecone client and index"""
        pc = Pinecone(
            api_key=self.pinecone_api_key
        )

        # Now do stuff
        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

        if self.pinecone_index_name not in existing_indexes:
            pc.create_index(
                name=self.pinecone_index_name, 
                dimension=1536, 
                metric='euclidean',
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            while not pc.describe_index(self.pinecone_index_name).status["ready"]:
                time.sleep(1)


        self.pc_index = pc.Index(self.pinecone_index_name)
        # pinecone.init(
        #     api_key=self.pinecone_api_key,
        #     environment=self.pinecone_environment
        # )
        
        # # Ensure index exists
        # if self.pinecone_index_name not in pinecone.list_indexes():
        #     pinecone.create_index(
        #         name=self.pinecone_index_name,
        #         dimension=1536,  # OpenAI embedding dimension
        #         metric='cosine'
        #     )
    
    def _init_embedding_model(self):
        """Initialize OpenAI embedding model"""
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=self.openai_api_key,
            model='text-embedding-3-small'
        )
    
    def save_to_s3(self, content, filename):
        """
        Save content to S3 bucket
        
        Args:
            content (str): Content to save
            filename (str): Filename/key for S3 object
            
        Returns:
            str: S3 URL of saved object
        """
        try:
            self.s3_client.put_object(
                Bucket=self.aws_s3_bucket,
                Key=filename,
                Body=content.encode('utf-8'),
                ContentType='application/json'
            )
            return f"s3://{self.aws_s3_bucket}/{filename}"
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            raise
    
    def insert_reddit_article(self, post_data):
        """
        Insert Reddit post data into PostgreSQL
        
        Args:
            post_data (dict): Dictionary containing post details
        
        Returns:
            bool: Success status of insertion
        """
        conn = None
        try:
            conn = psycopg2.connect(
                host=self.db_host,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                port=self.db_port
            )
            
            cursor = conn.cursor()
            
            # Create table if not exists
            create_table_query = """
            CREATE TABLE IF NOT EXISTS reddit_posts (
                id TEXT PRIMARY KEY,
                title TEXT,
                body TEXT,
                author TEXT,
                subreddit TEXT,
                score INTEGER,
                created_at TIMESTAMP,
                s3_url TEXT,
                vector_id TEXT
            );
            """
            cursor.execute(create_table_query)
            
            # Insert or update post
            insert_query = """
            INSERT INTO reddit_posts 
            (id, title, body, author, subreddit, score, created_at, s3_url, vector_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET 
            title = EXCLUDED.title,
            body = EXCLUDED.body,
            score = EXCLUDED.score,
            s3_url = EXCLUDED.s3_url,
            vector_id = EXCLUDED.vector_id;
            """
            
            cursor.execute(insert_query, (
                post_data.get('id', ''),
                post_data.get('title', ''),
                post_data.get('body', ''),
                post_data.get('author', ''),
                post_data.get('subreddit', ''),
                post_data.get('score', 0),
                post_data.get('created', datetime.now()),
                post_data.get('s3_url', ''),
                post_data.get('vector_id', '')
            ))
            
            conn.commit()
            return True
        
        except Exception as e:
            print(f"Database insertion error: {e}")
            if conn:
                conn.rollback()
            return False
        
        finally:
            if conn:
                conn.close()
    
    def process_reddit_data(self, dataframe):
        """
        Process Reddit data by:
        1. Saving to S3
        2. Creating vector embeddings
        3. Storing in Pinecone
        4. Inserting into PostgreSQL
        
        Args:
            dataframe (pd.DataFrame): DataFrame containing Reddit posts
        """
        # Text splitter for large documents
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        # Timestamp for S3 and tracking
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Process each post
        for _, row in dataframe.iterrows():
            try:
                # Combine title and body for embedding
                full_text = f"{row['title']} {row.get('body', '')}"
                
                # Split text into chunks
                text_chunks = text_splitter.split_text(full_text)
                
                # Save raw data to S3
                s3_key = f"reddit_posts/{timestamp}/{row['id']}.json"
                s3_url = self.save_to_s3(
                    json.dumps(row.to_dict(), default=str), 
                    s3_key
                )

                vector_store = PineconeVectorStore(index=self.pc_index, embedding=self.embeddings)

                vector_store.add_texts(full_text, id=row['id'])
                # Prepare post data for database
                post_data = {
                    'id': row['id'],
                    'title': row['title'],
                    'body': row.get('body', ''),
                    'author': row['author'],
                    'subreddit': row['subreddit'],
                    'score': row['score'],
                    'created': row['created'],
                    's3_url': s3_url,
                    'vector_id': row['id'],  # Pinecone index name
                }
                
                # Insert into database
                self.insert_reddit_article(post_data)
                
                print(f"Processed post: {row['title']}")
            
            except Exception as e:
                print(f"Error processing post: {e}")