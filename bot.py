from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import json
from dotenv import load_dotenv
import os
import asyncio


load_dotenv()
TOKEN = os.getenv("TOKEN")
BOT_USERNAME= os.getenv("BOT_USERNAME")
GROUP_ID = os.getenv("GROUP_ID")
IMAGE_DIR = os.getenv("IMAGE_DIR")
VID_DIR = os.getenv("VID_DIR")




if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)
if not os.path.exists(VID_DIR):
    os.makedirs(VID_DIR)


#parses and returns meta data
def parse_message_metadata(message):
    
    metadata = {
        "message_id": message.message_id,
        "date": {
            "year": message.date.year,
            "month": message.date.month,
            "day": message.date.day,
            "hour": message.date.hour,
            "minute": message.date.minute,
            "second": message.date.second
        },
        "content": {
            "text": message.caption if message.caption else message.text
        },
        "user": {
            "id": message.from_user.id
        },
        "chat_id": message.chat_id,
        "media": {}
    }

    # Save photo object
    if message.photo:
        slicing = len(message.photo) // 3  # Adjust slicing logic as needed
        img_list = message.photo[-slicing:]
        metadata["media"]["type"] = "photo"
        metadata["media"]["photo_object"] = img_list

    # Save video object
    elif message.video:
        metadata["media"]["type"] = "video"
        metadata["media"]["video_object"] = message.video

    return metadata
    

# grabs sent messages in the group and saves to a  file
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    metadata = parse_message_metadata(update.message)
   
   
  
    
    if metadata['media'].get('photo_object'):
        for i in metadata['media']['photo_object']:
                file = await context.bot.get_file(i.file_id)
                file_path = os.path.join(IMAGE_DIR,f"downloaded_image_{i.file_id}.jpg")# save to directory
                await file.download_to_drive(file_path)

            

    if metadata['media'].get('video_object'):

        video = metadata['media']['video_object']
        file = await context.bot.get_file(video.file_id)
        file_path = os.path.join(VID_DIR, f"downloaded_video_{video.file_id}.mp4")  # save to directory
        await file.download_to_drive(file_path)

 
    # del metadata['media']
    with open("metadata", "w") as f:
        json.dump(metadata,f, indent=4, default=str)

    # with open("message_content.txt", "a") as w:
    #     json.dump(msg_info,indent=4)

    
            

    
    

        
# sends the coffe msg to the group 
async def send_message_to_group(file_name: str):
    try:
        application = Application.builder().token(TOKEN).build()
        bot = application.bot

        group_chat_id = GROUP_ID
        print(group_chat_id )
        with open(file_name, "r") as msg:
            message_text = msg.read()
        await bot.send_message(chat_id=group_chat_id, text=message_text)

    except Exception as e:
        print(f"Error sending message: {e}")

def main():
    try:
        application = Application.builder().token(TOKEN).build()

        # Add a handler for regular messages (non-command text)
        # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND | filters.TEXT &  filters.PHOTO, handle_message))
        application.add_handler(MessageHandler(filters.TEXT | filters.PHOTO | filters.VIDEO, handle_message))

        # Add a command handler for the /send command
        application.add_handler(CommandHandler("send", lambda update, context: asyncio.create_task(send_message_to_group())))

        # Start the application (assuming this runs the bot and starts handling updates)
        application.run_polling()

    except KeyboardInterrupt:
        print("Bot stopped by keyboard interrupt")


if __name__ == '__main__':
    while True:
        try:
            value = int(input("Enter 1 to start the bot,\nEnter 2 to send a coffee message,\nEnter 3 for boost message: "))

            if value == 1:
                main()
                break
            elif value == 2:
                asyncio.run(send_message_to_group("coffee.txt"))
                break
            elif value == 3:
                asyncio.run(send_message_to_group("boost.txt"))
                break
            else:
                print("Invalid input. Please enter either 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number (1, 2, or 3).")
            
        
        
    


