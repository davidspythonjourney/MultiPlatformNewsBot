import os
import tweepy
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
            cls._instance.client = tweepy.Client(
                consumer_key=os.getenv("CONSUMER_KEY"),
                consumer_secret=os.getenv("CONSUMER_SECRET"),
                access_token=os.getenv("ACCESS_TOKEN"),
                access_token_secret=os.getenv("ACCESS_TOKEN_SECRET")
            )
        return cls._instance

    @staticmethod
    def get_client():
        return TwitterAPI()._instance.client


    

# Verify credentials
def verify_creds():
    api = TwitterAPI.get_api()
    try:
        if api.verify_credentials():
         return True
    except Exception as e:
        print(f"Error during authentication: {e}")
    return False
        
    

def create_tweet(text: str):
    client = TwitterAPI.get_client()
    try:
        response = client.create_tweet(text=text)
        print(f"Tweet created successfully with ID: {response.data['id']}")
    except Exception as e:
        print(f"Error creating tweet: {e}")
   
tweet_text = "This is my first tweet using tweepy API with Singleton pattern!"
create_tweet(tweet_text)
