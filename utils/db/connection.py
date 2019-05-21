from pymysql import connect, cursors

# Connect to the database
from settings import (
    MYSQL_HOST, 
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
)


def get_connection():
    """Get database connection"""
    try:
        return connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            db=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=cursors.Cursor
        )
    except Exception as exp:
        raise exp
