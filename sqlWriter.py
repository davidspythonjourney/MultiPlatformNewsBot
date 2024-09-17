from sql import createConnection, closeConnections
import os
import io
from PIL import Image
from pathlib import Path
from utils import jsonLoader,  deleteFilesInDir

image_directory = Path(os.getenv("IMAGE_DIR"))
video_directory = Path(os.getenv("VID_DIR"))
metadata_file = 'metadata.json'


def writeMetadata(msg_dict, connection, cursor):
    sql = """INSERT INTO Metadata 
            (message_id, date_year, date_month, date_day, 
            date_hour, date_minute, date_second, 
            user_id, chat_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
    val = (
    msg_dict.get("message_id"),
    msg_dict.get("date", {}).get("year"),
    msg_dict.get("date", {}).get("month"),
    msg_dict.get("date", {}).get("day"),
    msg_dict.get("date", {}).get("hour"),
    msg_dict.get("date", {}).get("minute"),
    msg_dict.get("date", {}).get("second"),
    msg_dict.get("user", {}).get("id"),
    msg_dict.get("chat_id"),
    )
    cursor.execute(sql, val)
    connection.commit()
    print(f"Record inserted successfully into Metadata table")
    # closeConnections(connection, cursor)
            
def writeImagesDb(text_id, connection, cursor):
    if os.path.exists(image_directory):
        for img in image_directory.iterdir():
            image_blob = img.read_bytes()
            sql = "INSERT INTO Picture (text_id, image_blob) VALUES (%s, %s)"
            cursor.execute(sql, (text_id, image_blob))
        connection.commit()
        print(f"Image inserted successfully for text_id: {text_id}")
        deleteFilesInDir(image_directory)
    # closeConnections(connection, cursor)        


def writeVideosDb(text_id, connection, cursor):
    if os.path.exists(video_directory):
        for vid in video_directory.iterdir():
            video_blob = vid.read_bytes()
            sql = "INSERT INTO Video (video_data, text_id) VALUES (%s, %s)"
            cursor.execute(sql, (video_blob, text_id))
        connection.commit()
        print(f"Video '{vid.name}' inserted successfully for text_id: {text_id}")
        deleteFilesInDir(video_directory)
                    
def writeMsgDb():
    msg_dict = jsonLoader(metadata_file)
    if msg_dict:
        connection, cursor = createConnection()
        if  connection and cursor:
            msg_text = msg_dict.get('content', {}).get('text')
            msg_id = msg_dict.get('message_id')
            sql = "INSERT INTO Text (text_content, text_id) VALUES (%s, %s)"
            cursor.execute(sql, (msg_text, msg_id))
            connection.commit()
            print(f"Text inserted successfully with ID: {msg_id}")
            
            # Now insert associated images and videos
            writeImagesDb(msg_id, connection, cursor)
            writeVideosDb(msg_id, connection, cursor)
            writeMetadata(msg_dict, connection, cursor)
            closeConnections(connection, cursor) 

   
def readMsgDb():
    connection, cursor = createConnection()
    if  connection and cursor:
        query =  """
                SELECT t.text_id, t.text_content, p.image_blob, v.video_data
                FROM text t
                LEFT JOIN picture p ON t.text_id = p.text_id
                LEFT JOIN video v ON t.text_id = v.text_id;
            """
        cursor.execute(query)
        results = cursor.fetchall()
        closeConnections(connection, cursor)
        # print(results)
        return results

def parseQuery():
    query_dict = {
        'text': None,
        'images_byte': [],
        'videos': [],
        'images': []
    }
    query_result = readMsgDb()  
    if query_result:
        for row in query_result:
            _, text_content, image_blob, video_data = row
            if text_content and not query_dict['text']:
                query_dict['text'] = text_content
            if image_blob:
                image = Image.open(io.BytesIO(image_blob))
                query_dict['images'].append(image)
                query_dict['images_byte'].append(image_blob)
            if video_data:
                query_dict['videos'].append(video_data)

    return query_dict

parseQuery()
# print(parseQuery())
# writeMsgDb()
# writeMetadata()
# writeImagesDb()