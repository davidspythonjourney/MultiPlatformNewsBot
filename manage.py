from sql import *
import json
import os
from pathlib import Path
# if i change import from sql change this as well
# from dotenv import load_dotenv
# load_dotenv()




Image_directory = Path(os.getenv("IMAGE_DIR"))

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
                msg_dict.get("chat_id")
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




def write_images_db():

    if os.path.exists(Image_directory):
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                
                for img in Image_directory.iterdir() :
                    
                    image_blob = img.read_bytes()
                    
                    sql = "INSERT INTO Picture (image_blob) VALUES (%s)"
                    cursor.execute(sql, (image_blob,))
                    connection.commit()
                    print(f"Record inserted successfully into Metadata table")
                    
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e} ")
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")


def write_msg_db():
    
   
    msg_dict = json_loader(metadata_file )
    if msg_dict:
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                msg_text = msg_dict.get('content', {}).get('text')
                msg_id = msg_dict.get('message_id')
                sql = "INSERT INTO Text (text_content, text_id) VALUES (%s, %s)"
                cursor.execute(sql, (msg_text ,msg_id))
                connection.commit()
                print(f"Record inserted successfully into Metadata table")
                            
        except mysql.connector.Error as error:
            print(f"Error connecting to MySQL: ")
                
        finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()
                    print("MySQL connection is closed")
        

# write_msg_db()
# write_to_db_metadata()
# write_images_db()