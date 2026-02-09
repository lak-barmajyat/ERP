from os import getenv
from dotenv import load_dotenv
import pymysql

# Load environment variables
load_dotenv(".env")


def get_db_connection():
    try:
        connection = pymysql.connect(
            host=getenv("DB_HOST"),
            user=getenv("DB_USER"),
            password=getenv("DB_PASSWORD"),
            database=getenv("DB_NAME")
        )
        cursor = connection.cursor()
        return connection, cursor
    except pymysql.Error as e:
        print(f"Error connecting to database: {e}")
        raise


def close_db_connection(connection, cursor=None):
    if cursor:
        cursor.close()
    if connection:
        connection.close()
