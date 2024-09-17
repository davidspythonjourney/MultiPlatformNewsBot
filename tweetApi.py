import tweepy
from tweepy.auth import OAuthHandler
from utils import getTwitterCreds

#singleton pattern to ensure single twitter api object
class TwitterAPI:
    _instance = None
    def __new__(cls):
        if not cls._instance:
            twitter_creds = getTwitterCreds()
            if not all(twitter_creds.values()):
                raise ValueError("Missing one or more Twitter API credentials")# maybe handle better
            cls._instance = super().__new__(cls)
            # Create v2 client
            cls._instance.client = tweepy.Client(
                bearer_token = twitter_creds.get("bearer_token"),
                consumer_key = twitter_creds.get("consumer_key"),
                consumer_secret = twitter_creds.get("consumer_secret"),
                access_token = twitter_creds.get("access_token"),
                access_token_secret = twitter_creds.get("access_token_secret")
            )
            # Create v1.1 API
            auth = OAuthHandler(
                twitter_creds.get("consumer_key"),
                twitter_creds.get("consumer_secret")
            )
            auth.set_access_token(
                twitter_creds.get("access_token"),
                twitter_creds.get("access_token_secret")
            )
            cls._instance.api = tweepy.API(auth)
        return cls._instance

    @staticmethod
    def getClient():
        return TwitterAPI()._instance.client

    @staticmethod
    def getApi():
        return TwitterAPI()._instance.api
    
    