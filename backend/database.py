"""
Connects to a SQL database using pyodbc
"""
import pyodbc

# Creating and returning a connection to my database
def db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=localhost\\SQLEXPRESS;'
        'DATABASE=Proiect_DB;'
        'Encrypt=no;'
        'Trusted_Connection=yes;'
    )
    return conn