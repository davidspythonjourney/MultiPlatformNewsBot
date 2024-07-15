from bot import handle_message
from sql import *
import json
# from dotenv import load_dotenv
import os
# load_dotenv()
from pathlib import Path

Image_directory = Path(os.getenv("IMAGE_DIR"))
sql_dict = {
    "host": os.getenv('HOST'),
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "database": os.getenv('DATABASE')
}

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


# think about how i can run my hadlke message fucntion return a result and parse that stuff tow rite to my sql
def write_to_db_metadata():
    
    msg_dict = json_loader('metadata')
    # if os.path.exists('metadata'):
    #     with open('metadata', 'r') as f:
    #         msg_dict = json.load(f)
    if json_loader('metadata'):
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                
                sql = """INSERT INTO Metadata 
                        (message_id, date_year, date_month, date_day, 
                        date_hour, date_minute, date_second, 
                        user_id, chat_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                
                val = (
                    msg_dict["message_id"],
                    msg_dict["date"]["year"],
                    msg_dict["date"]["month"],
                    msg_dict["date"]["day"],
                    msg_dict["date"]["hour"],
                    msg_dict["date"]["minute"],
                    msg_dict["date"]["second"],
                    msg_dict["user"]["id"],
                    msg_dict["chat_id"]
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
                    
        except mysql.connector.Error as error:
            print(f"Error connecting to MySQL: ")
            
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
                print("MySQL connection is closed")


def write_msg_db():
    
    # if os.path.exists('metadata'):
    #     with open('metadata', 'r') as f:
    #         msg_dict = json.load(f)
    # msg_text = msg_dict['content']['text']
    msg_dict = json_loader('metadata')
    if msg_dict:
        try:
            connection = mysql.connector.connect(**sql_dict)
            if connection.is_connected():
                cursor = connection.cursor()
                msg_text = msg_dict['content']['text']
                msg_id = msg_dict['message_id']
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
        

write_msg_db()



    
# write_to_db_metadata()
# write_images_db()