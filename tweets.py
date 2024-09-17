from sqlWriter import parseQuery
import tempfile
from tweetApi import TwitterAPI


# Verify credentials
def verifyCreds():
    client = TwitterAPI.getClient()
    try:
        if client.get_me():
         return True
    except Exception as e:
        print(f"Error during authentication: {e}")
    return False

def uploadMedia(media_bytes: list, media_type :str) -> None:
        api = TwitterAPI.getApi()
        media_ids = []
        if not media_bytes:
            return
        for bytes in media_bytes:
            with tempfile.NamedTemporaryFile(delete = True, suffix = media_type) as temp_file:
                temp_file.write(bytes)
                temp_file.flush() 
                media_uplaod_id = api.media_upload(filename = temp_file.name).media_id_string
                media_ids.append(media_uplaod_id) 
        return media_ids
                
#must handle parsing and uploading of single message no bigegr than list of 4 look into making a thread        
def getMediaIds():
    query_data = parseQuery() 
    tweet_text = query_data.get("text")
    if query_data.get('images_byte'):
       image_media_ids =  uploadMedia(query_data.get('images_byte'), "jpeg")
       
    if query_data.get('videos'):
       video_media_ids =  uploadMedia(query_data.get('images_byte'), "mp4")
    all_media_ids = image_media_ids + video_media_ids    
    return  all_media_ids, tweet_text


#create and post tweet using v2 endpoint
def createSingleTweet(text: str, media_ids = None):
    client = TwitterAPI.getClient()
    try:
        if media_ids:
            client.create_tweet(text = text, media_ids = media_ids)
        else:
         client.create_tweet(text = text)
    except Exception as e:
        print(f"Error creating tweet: {e}")
    
def createTweetThread(media_ids: list, text: str) -> None: 
    client = TwitterAPI.getClient()
    thread_id  = None
    for index, media_id_group in enumerate(media_ids):
        try:
            if index == 0:
                initial_tweet = client.create_tweet(text = text, media_ids = media_id_group)
                thread_id = initial_tweet.data["id"]
            else:
                response_tweet = client.create_tweet(text = None, media_ids = media_id_group, in_reply_to_tweet_id = thread_id)# done keep text the same for some reason
                thread_id = response_tweet.data["id"]
        except Exception as e:
            print(f"Error creating tweet thread: {e}")

            
def createTweetWithMedia():
    split_ids = []
    media_ids, text = getMediaIds()
    if media_ids:
        if len(media_ids) > 4:
            for i in range(0, len(media_ids), 4):
             split_ids.append(media_ids[i : i + 4])
            createTweetThread(split_ids, text)
        else:
            createSingleTweet(text, media_ids)
    else:
        print("Failed to create single tweet/tweet thread")
        
         

createTweetWithMedia()


