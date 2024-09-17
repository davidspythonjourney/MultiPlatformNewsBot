from dotenv import load_dotenv
import os
import asyncio
from telethon import events
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument, DocumentAttributeVideo
from utils import parseMessageMetadata, downloadMedia , jsonLoader, jsonWriter, ensureDirectoriesExist
from typing import Dict, List, Callable, Any

load_dotenv()
TOKEN = os.getenv("TOKEN")
IMAGE_DIR = os.getenv("IMAGE_DIR")
VID_DIR = os.getenv("VID_DIR")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
METADATA_FILE = "metadata.json"
COFFEE_MESSAGE_FILE = "coffee.txt"
BOOST_MESSAGE_FILE = "boost.txt"

client = TelegramClient('bot', API_ID, API_HASH).start(bot_token = TOKEN)

@client.on(events.NewMessage)
async def handler(event: events.NewMessage) -> None:
    if event.grouped_id:
        # parse multiple messages
        await gatherAlbum(event, handleAlbum)
    else:
        #parse single message 
        await handleMessage(event) 

pending_albums = {}
async def gatherAlbum(incoming_event: events.NewMessage, album_parsing_func: Callable[[List[events.NewMessage]], asyncio.Future]) -> None:
    pending = pending_albums.get(incoming_event.grouped_id)
    if pending:
        pending.append(incoming_event)
    else:
        pending_albums[incoming_event.grouped_id] = [incoming_event]
        # Wait for other events to come in.change for big batches
        await asyncio.sleep(0.5)  
        album_media = pending_albums.pop(incoming_event.grouped_id, [])
        if album_media:
            await album_parsing_func(album_media)

async def processMedia(message_metadata: Dict[str, any]) -> None:
    media_types = {
        "photo_object": IMAGE_DIR,
        "video_object": VID_DIR
        }
    for media_type, media_dir in media_types.items():
        media_for_download = message_metadata.get(media_type)
        if media_for_download:
            for media in media_for_download:
                await downloadMedia(client, media, media_dir)   
    if message_metadata.get("content").get("text"):
        del message_metadata["photo_object"], message_metadata["video_object"], message_metadata["media"]
        jsonWriter(message_metadata, METADATA_FILE)
    
async def handleAlbum(media_events_batch: List[events.NewMessage]) -> None:
    for event in media_events_batch:
        metadata = parseMessageMetadata(event)
        await processMedia(metadata)
              
# grabs sent messages in the group and saves to a  file
async def handleMessage(single_msg: events.NewMessage) -> None:
    metadata = parseMessageMetadata(single_msg)
    if metadata.get("media"):
        if isinstance(single_msg.media, MessageMediaPhoto):
            await downloadMedia(client, single_msg.media, IMAGE_DIR) 
        elif isinstance(single_msg.media, MessageMediaDocument):
            if single_msg.video:
                await downloadMedia(client, single_msg.media, VID_DIR)
         
# sends the coffe msg to the group 
async def sendMessageToGroup(group_name: str, file_name: str) -> None:
    message = jsonLoader(file_name)
    if message:
        await client.send_message(group_name, message )
    
def main():
    try:
        ensureDirectoriesExist([VID_DIR, IMAGE_DIR ])
        # Start the Telethon client
        client.start()
        print("Bot is running. Press Ctrl+Z to stop.")
        # Block the script to keep it running
        client.run_until_disconnected() 
    except KeyboardInterrupt:
        print("Bot stopped by keyboard interrupt")