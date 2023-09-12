import mysql.connector
from mysql.connector import Error

def connectDB():
    try:
        return  mysql.connector.connect(host='redacted',
                                         database='redacted',
                                         user='redacted',
                                         password='redacted')
    except Error as e:
        print("Error while connecting to MySQL", e)
