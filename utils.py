import json
import os
from pathlib import Path
from telethon.errors import FloodWaitError, FilePartMissingError, RPCError
from typing import Dict, Any, List
from dotenv import load_dotenv
load_dotenv()

#parses and returns meta data
def parseMessageMetadata(event) -> Dict[str, Any]:
    metadata = {
        "message_id" : event.message.id,
        "date" : {
            "year" : event.date.year,
            "month" : event.date.month,
            "day" : event.date.day,
            "hour" : event.date.hour,
            "minute" : event.date.minute,
            "second" : event.date.second
             },
        "content" : {
            "text": event.message.message if event.message else None
            },
        "user" : {
            "id" : event.sender_id
            },
        "chat_id" : event.chat_id,
        "media" : event.media,
        "photo_object" : [],
        "video_object" : []
         }
    #handles both single message media and multiple messages by always keeping it a lsit
    messages = [event.message] if not isinstance(event.message, list) else event.message
    for message in messages:
        if message.photo:
            metadata["photo_object"].append(message)
        elif message.video:
            metadata["video_object"].append(message)
        elif not metadata["content"]["text"] and message.message:
            metadata["content"]["text"] = message.message
    return metadata



# downloads media and performs error handling
async def downloadMedia(client, media, file_path) -> None:
    try:
        await client.download_media(media, file = file_path)
    except (FloodWaitError, FilePartMissingError, RPCError) as e:
        print(f"Failed to download media: {e}\nFor file path: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while downloading media: {e}\nFor file path: {file_path}")
 
        
# handle creating/writing parsed metadata to file in json format
def jsonLoader(file_path: str):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
    else:
        print(f"File: {file_path} not found")
        return None
    
    
def jsonWriter(data: Any, file_path: str) -> None:
    try:
        if os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
    except TypeError as e:
        print(f"Error encoding data to JSON: {e}")
    except IOError as e:
        print(f"Error writing to file '{file_path}': {e}")    
        

def ensureDirectoriesExist(dir_names: list):
    for directory in dir_names:
        if not os.path.exists(directory):
            os.makedirs(directory)        
        
def deleteFilesInDir(dir_path):
    dir_path = Path(dir_path)
    if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file():
                    item.unlink()  


def getTwitterCreds():
    return{
        "bearer_token" : os.getenv("BEARER_TOKEN"),
        "consumer_key" : os.getenv("CONSUMER_KEY"),
        "consumer_secret" : os.getenv("CONSUMER_SECRET"),
        "access_token" : os.getenv("ACCESS_TOKEN"),
        "access_token_secret" : os.getenv("ACCESS_TOKEN_SECRET")
        }

def getSqlCreds():
    return {
    "host" : os.getenv('HOST'),
    "user" : os.getenv('USER'),
    "password" : os.getenv('PASSWORD'),
    "database" : os.getenv('DATABASE')
    }
    
def getBloggerCreds():
    return json.loads(os.getenv("CLIENT_SECRETS_JSON"))

