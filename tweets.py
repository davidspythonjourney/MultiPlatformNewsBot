import os
from manage import parse_query
import tweepy
from tweepy.auth import OAuthHandler

from dotenv import load_dotenv
load_dotenv()

twitter_creds = {
    'bearer_token': os.getenv("BEARER_TOKEN"),
    "consumer_key": os.getenv("CONSUMER_KEY"),
    "consumer_secret": os.getenv("CONSUMER_SECRET"),
    "access_token": os.getenv("ACCESS_TOKEN"),
    "access_token_secret": os.getenv("ACCESS_TOKEN_SECRET")
}


#singleton pattern to ensure single twitter api object

class TwitterAPI:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            # Create v2 client
            cls._instance.client = tweepy.Client(
                consumer_key=os.getenv("CONSUMER_KEY"),
                consumer_secret=os.getenv("CONSUMER_SECRET"),
                access_token=os.getenv("ACCESS_TOKEN"),
                access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
            )
            # Create v1.1 API
            auth = OAuthHandler(
                os.getenv("CONSUMER_KEY"),
                os.getenv("CONSUMER_SECRET")
            )
            auth.set_access_token(
                os.getenv("ACCESS_TOKEN"),
                os.getenv("ACCESS_TOKEN_SECRET")
            )
            cls._instance.api = tweepy.API(auth)
        return cls._instance

    @staticmethod
    def get_client():
        return TwitterAPI()._instance.client

    @staticmethod
    def get_api():
        return TwitterAPI()._instance.api
    
# Verify credentials
def verify_creds():
    api = TwitterAPI.get_client()
    try:
        if api.get_me():
         return True
    except Exception as e:
        print(f"Error during authentication: {e}")
    return False
        
    
#create and post tweet using v2 endpoint
def create_tweet(text: str, media_ids=None):
    client = TwitterAPI.get_client()
    try:
        response = client.create_tweet(text=text, media_ids=media_ids)
        print(f"Tweet created successfully with ID: {response.data['id']}")
    except Exception as e:
        print(f"Error creating tweet: {e}")
        
# tweet_text = "This is my first tweet using tweepy API with Singleton pattern!"
# create_tweet(tweet_text)





def upload_media():
    api = TwitterAPI.get_api()
    try:
        query_data = parse_query()
        media_ids = []

        # Upload images
        for img_bytes in query_data['images_byte']:
            media = api.media_upload(file=img_bytes)
            media_ids.append(media.media_id)

        # Upload videos (if supported and implemented)
        for video_path in query_data['videos']:
            # Note: Video upload might require chunked upload for larger files
            media = api.media_upload(filename=video_path)
            media_ids.append(media.media_id)

        return media_ids
    except Exception as e:
        print(f"Error uploading media: {e}")
        return None
   
   
   
def create_tweet_with_media():
    query_data = parse_query()
    print(query_data)
    media_ids = upload_media()
    
    if media_ids:
        tweet_text = query_data['text'] if query_data['text'] else "Check out this media!"
        create_tweet(tweet_text, media_ids)
    else:
        print("Failed to upload media or no media to upload")
         
tweet_text = "This is a tweet with media!"
media_ids = upload_media()
if media_ids:
    create_tweet(tweet_text, media_ids)
else:
    print("Failed to upload media")
    
create_tweet_with_media()