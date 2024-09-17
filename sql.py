import mysql.connector
from utils import getSqlCreds

# function to check and establish conenction with sql databse
def createConnection(**kwargs: dict[str, str]):
    try:
        connection = mysql.connector.connect(**getSqlCreds())
        if connection.is_connected():
            return connection, connection.cursor() 
    except mysql.connector.Error as error:
        print(f"Error connecting to MySQL: {error}")
    return None, None

def closeConnections(connection = None, cursor = None):
    if cursor:
        try:
            cursor.close()
            print("Cursor is closed")
        except mysql.connector.Error as error:
            print(f"Error closing cursor: {error}")
    
    if connection:
        try:
            connection.close()
            print("MySQL connection is closed")
        except mysql.connector.Error as error:
            print(f"Error closing connection: {error}")



# createConnection(**getSqlCreds())

