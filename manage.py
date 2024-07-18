from sql import *
import json
import os
from pathlib import Path
import io
# if i change import from sql change this as well
# from dotenv import load_dotenv
# load_dotenv()


Image_directory = Path(os.getenv("IMAGE_DIR"))
Video_directory = Path(os.getenv("VID_DIR"))

metadata_file = 'metadata'

sql_dict = {
    "host": os.getenv('HOST'),
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "database": os.getenv('DATABASE')
}


# handle creating/writing parsed metadata to file in json format
def json_loader(file_path: str):
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return None
    else:
        print(f"File '{file_path}' not found")
        return None


# think about how i can run my handle message fucntion return a result and parse that stuff to write to my sql
def write_to_db_metadata():
    
    msg_dict = json_loader(metadata_file)
    if msg_dict:
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                
                sql = """INSERT INTO Metadata 
                        (message_id, date_year, date_month, date_day, 
                        date_hour, date_minute, date_second, 
                        user_id, chat_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                #using "get" method to avoid errors
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
                
        except Exception as e:
            print(f"Error while connecting to MySQL: {e}")
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")


def write_images_db(text_id):
    if os.path.exists(Image_directory):
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                
                for img in Image_directory.iterdir():
                    image_blob = img.read_bytes()
                    
                    sql = "INSERT INTO Picture (text_id, image_blob) VALUES (%s, %s)"
                    cursor.execute(sql, (text_id, image_blob))
                    connection.commit()
                    print(f"Image inserted successfully for text_id: {text_id}")
                    os.remove(img)
                    
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
                

def write_videos_db(text_id):
    if os.path.exists(Video_directory):
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                
                for vid in Video_directory.iterdir():
                    # Read the video file as binary data
                    video_blob = vid.read_bytes()
                    
                    sql = "INSERT INTO Video (video_data, text_id) VALUES (%s, %s)"
                    cursor.execute(sql, (video_blob, text_id))
                    connection.commit()
                    print(f"Video '{vid.name}' inserted successfully for text_id: {text_id}")
                    os.remove()
                    
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
                    

def write_msg_db():
    msg_dict = json_loader(metadata_file)
    if msg_dict:
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                msg_text = msg_dict.get('content', {}).get('text')
                msg_id = msg_dict.get('message_id')
                sql = "INSERT INTO Text (text_content, text_id) VALUES (%s, %s)"
                cursor.execute(sql, (msg_text, msg_id))
                connection.commit()
                print(f"Text inserted successfully with ID: {msg_id}")
                
                # Now insert associated images and videos
                write_images_db(msg_id)
                write_videos_db(msg_id)
                write_to_db_metadata()
                            
        except mysql.connector.Error as error:
            print(f"Error connecting to MySQL: {error}")
                
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")
                  
   

def read_msg_db():
    try:
        connection = mysql.connector.connect(**sql_dict)
        if connection.is_connected():
            cursor = connection.cursor()
            query = """
                SELECT t.text_id, t.text_content, p.image_blobs, v.video_data
                FROM text t
                LEFT JOIN (
                    SELECT p.text_id, GROUP_CONCAT(p.image_blob) AS image_blobs
                    FROM picture p
                    GROUP BY p.text_id
                ) AS p ON t.text_id = p.text_id
                LEFT JOIN (
                    SELECT v.text_id, GROUP_CONCAT(v.video_data) AS video_data
                    FROM video v
                    GROUP BY v.text_id
                ) AS v ON t.text_id = v.text_id;
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return results

    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")
    return None



    

def parse_query():
    
    query_dict = {
        'text': None,
        'images_byte': [],
        'videos': [] ,
        "images": []
    }
    
    query_result = read_msg_db()  
    
    if query_result:
        print(f" this si the etxt: {query_result}")
        

        
        for row in query_result:
            _, text_content, image_blobs, video_data = row
            # print(f" this si the etxt: {text_content}")
            if text_content:
                query_dict['text'] = text_content

            
            if image_blobs:
                images_list = image_blobs.split(b',')  # Split using bytes delimiter
                
                for img_blob in images_list:
                    image_bytes = img_blob
                    query_dict['images_byte'].append(image_bytes)
                    
                    # Convert bytes to Image object
                    # image = Image.open(io.BytesIO(image_bytes))
                    # query_dict['images'].append(image)
                
            if video_data:
                videos_list = video_data.split(b',')
                query_dict['videos'].extend(videos_list)
    
    return query_dict
             
             

        
        
        
        
        
     




print(parse_query())
# write_msg_db()
# write_to_db_metadata()
# write_images_db()