import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Replace with your MySQL credentials and database name from .env file



# function to check and establish conenction with sql databse
def try_connection(**kwargs:dict[str, str]):
    sql_dict = {
    "host": os.getenv('HOST'),
    "user": os.getenv('USER'),
    "password": os.getenv('PASSWORD'),
    "database": os.getenv('DATABASE')
}
    try:

        connection = mysql.connector.connect(**sql_dict )
        if connection.is_connected():
            return connection 
    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")
    return None

# try_connection(**sql_dict)

